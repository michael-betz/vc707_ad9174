"""
Demonstrate AD9174-FMC-EBZ board on VC707

Contains the gateware needed to establish the jesd204b link.

Connects trough UART to litex_server on a host PC to access the internal
control and status registers and the AD9174 SPI interface.
"""
from sys import path
path.append("spi")
from migen import *
from argparse import ArgumentParser
from collections import namedtuple
from litex.build.io import DifferentialInput
from migen.genlib.resetsync import AsyncResetSynchronizer
from migen.genlib.cdc import MultiReg
from litex.build.generic_platform import Subsignal, Pins, IOStandard, Misc
from litex.soc.cores import dna, uart, spi, freqmeter
from litex.soc.interconnect.csr import AutoCSR
from litex.soc.integration.builder import Builder, builder_args, builder_argdict
from litex.soc.integration.soc_core import SoCCore
from litejesd204b.phy.gtx import GTXQuadPLL
from litejesd204b.phy.prbs import PRBS15Generator
from litejesd204b.phy import JESD204BPhyTX
from litejesd204b.core import LiteJESD204BCoreTX, LiteJESD204BCoreControl
from litex.soc.interconnect.csr import CSRStorage
from litescope import LiteScopeAnalyzer
from ad9174 import Ad9174Settings
from litex_boards.platforms import vc707


class PRBSGen(Module, AutoCSR):
    def __init__(self, soc, settings):
        ''' don't bother, doesn't work !!! '''
        # TODO reverse engineer the AD9174 datapath PRBS format :(
        self.sink = Record(settings.get_dsp_layout())
        self.source = Record(settings.get_dsp_layout())

        self.sample_prbs_en = CSRStorage(1)
        self.submodules.prbs = PRBS15Generator(settings.N)

        # Bypass if PRBS disabled (gets overridden if enabled)
        self.comb += self.source.eq(self.sink)

        for i, (conv, _) in enumerate(self.source.iter_flat()):
            for s in range(settings.FR_CLK * settings.S):
                self.comb += If(
                    self.sample_prbs_en.storage,
                    conv[s * settings.N: (s + 1) * settings.N].eq(
                        self.prbs.o
                    )
                )


class SampleGen(Module, AutoCSR):
    def __init__(self, soc, settings, depth=256):
        '''
        Blast out samples from Memory.
        1 Memory for each converter for each parallel sample
        '''
        self.source = Record(settings.get_dsp_layout())

        self.max_ind = CSRStorage(16)
        max_ind_ = Signal.like(self.max_ind.storage)
        self.specials += MultiReg(self.max_ind.storage, max_ind_, "jesd")
        adr = Signal.like(self.max_ind.storage)
        self.sync.jesd += [
            If(adr >= max_ind_,
                adr.eq(0)
            ).Else(
                adr.eq(adr + 1)
            )
        ]


        adr_offset = 0x10000000

        # TODO can't convince Vivado to infer Block ram for this :(
        # for m, (conv, _) in enumerate(self.source.iter_flat()):
        #     for s in range(settings.FR_CLK * settings.S):
        #         name = "m{:}_s{:}".format(m, s)
        #         mem = Memory(settings.N, depth, name=name)
        #         # setattr(self, name, mem)
        #         self.specials += mem
        #         sram = wishbone.SRAM(mem, we_gran=0)
        #         self.submodules += sram
        #         soc.register_mem(
        #             name,
        #             adr_offset,  # [bytes]
        #             sram.bus,
        #             mem.depth * 4  # [bytes]
        #         )
        #         p1 = mem.get_port(clock_domain="jesd")
        #         self.specials += p1
        #         adr_offset += 0x10000

        #         self.sync.jesd += [
        #             p1.adr.eq(adr),
        #             conv[s * settings.N: (s + 1) * settings.N].eq(p1.dat_r)
        #         ]


class CRG(Module, AutoCSR):
    def __init__(self, settings, f_wenzel, p, serd_pads, add_rst=[]):
        '''
        add_rst = additional reset signals for sys_clk
          must be active high and will be synchronized with sys_clk
          p = vc707 platform instance
        '''
        self.clock_domains.cd_sys = ClockDomain()

        # System clock from crystal on fpga board
        self.sys_clk_freq = int(1e9 / p.default_clk_period)

        # depends on f_wenzel and dividers in AD9174 + HMC7044
        self.tx_clk_freq = int(f_wenzel / settings.DSP_CLK_DIV)

        # depends on AD9174 JESD / DAC interpolation settings
        self.gtx_line_freq = int(f_wenzel / settings.DSP_CLK_DIV * 40)

        # # #

        clk_pads = p.request(p.default_clk_name)
        self.specials += DifferentialInput(
            clk_pads.p, clk_pads.n, self.cd_sys.clk
        )

        rst_sum = Signal()
        self.comb += rst_sum.eq(reduce(or_, add_rst))

        # Handle the GTX clock input
        refclk0 = Signal()
        self.specials += Instance(
            "IBUFDS_GTE2",
            i_CEB=0,
            i_I=serd_pads.clk_p,
            i_IB=serd_pads.clk_n,
            o_O=refclk0
        )
        self.clock_domains.cd_jesd = ClockDomain()

        self.specials += [
            AsyncResetSynchronizer(self.cd_sys, rst_sum),
            AsyncResetSynchronizer(self.cd_jesd, ResetSignal('sys')),
            Instance("BUFG", i_I=refclk0, o_O=self.cd_jesd.clk)
        ]

        # Add a frequency counter to `cd_jesd` (160 MHz) measures in [Hz]
        self.submodules.f_jesd = freqmeter.FreqMeter(
            self.sys_clk_freq,
            clk=ClockSignal('jesd')
        )

        # The two GTX quad PLLs for up to 8 lanes
        # These are taken care of and reset by GTXInit()
        self.submodules.qpll0 = GTXQuadPLL(
            refclk0,
            self.tx_clk_freq,
            self.gtx_line_freq
        )
        print(self.qpll0)

        if settings.L > 4:
            self.submodules.qpll1 = GTXQuadPLL(
                refclk0,
                self.tx_clk_freq,
                self.gtx_line_freq
            )
            print(self.qpll1)


class Top(SoCCore):
     def __init__(self, p, **kwargs):
        print("Top: ", p, kwargs)

        # ----------------------------
        #  Litex config
        # ----------------------------
        SoCCore.__init__(
            self,
            clk_freq=int(1e9 / p.default_clk_period),
            cpu_type=None,
            csr_data_width=32,
            with_uart=False,
            with_timer=False,
            integrated_rom_size=0,
            integrated_main_ram_size=0,
            integrated_sram_size=0,
            ident="AD9174 + VC707 test", ident_version=True,
            platform=p,
            **kwargs
        )

        self.settings = settings = Ad9174Settings(
            2, 4, 8,
            FCHK_OVER_OCTETS=True,
            SCR=1,
            DID=0x5A,
            BID=0x05
        )
        settings.calc_fchk()
        print(settings)

        for c in [
            "control", "dna", "crg", "f_ref", "spi", "sample_gen", "prbs_gen"
        ]:
            self.add_csr(c)

        for i in range(settings.L):
            self.add_csr("phy{}".format(i))

        # ----------------------------
        #  Ports
        # ----------------------------
        p.add_extension([
            ("AD9174_JESD204", 0,
                # CLK comes from HMC7044 CLKOUT12, goes to GTX (128 MHz)
                Subsignal("clk_p", Pins("FMC1_HPC:GBTCLK0_M2C_C_P")),
                Subsignal("clk_n", Pins("FMC1_HPC:GBTCLK0_M2C_C_N")),

                # GTX data lanes
                Subsignal("tx_p",  Pins(" ".join(
                    ["FMC1_HPC:DP{}_C2M_P".format(i) for i in [5, 6, 4, 7, 3, 2, 1, 0][:settings.L]]
                ))),
                Subsignal("tx_n",  Pins(" ".join(
                    ["FMC1_HPC:DP{}_C2M_N".format(i) for i in [5, 6, 4, 7, 3, 2, 1, 0][:settings.L]]
                ))),

                # JSYNC comes from AD9174 SYNC_OUT_0B, SYNC_OUT_1B
                Subsignal("jsync0_p", Pins("FMC1_HPC:LA01_CC_P"), IOStandard("LVDS")),
                Subsignal("jsync0_n", Pins("FMC1_HPC:LA01_CC_N"), IOStandard("LVDS")),

                # Subsignal("jsync1_p", Pins("FMC1_HPC:LA02_P"), IOStandard("LVDS")),
                # Subsignal("jsync1_n", Pins("FMC1_HPC:LA02_N"), IOStandard("LVDS")),

                # SYSREF comes from HMC7044 CLKOUT13 (16 MHz)
                Subsignal("sysref_p", Pins("FMC1_HPC:LA00_CC_P"), IOStandard("LVDS")),
                Subsignal("sysref_n", Pins("FMC1_HPC:LA00_CC_N"), IOStandard("LVDS"))
            ),
            ("AD9174_SPI", 0,
                # FMC_CS1 (AD9174), FMC_CS2 (HMC7044)
                Subsignal("cs_n", Pins("FMC1_HPC:LA04_N FMC1_HPC:LA05_P")),
                Subsignal("miso", Pins("FMC1_HPC:LA04_P"), Misc("PULLUP TRUE")),
                Subsignal("mosi", Pins("FMC1_HPC:LA03_N")),
                Subsignal("clk",  Pins("FMC1_HPC:LA03_P")),
                Subsignal("spi_en", Pins("FMC1_HPC:LA05_N")),
                IOStandard("LVCMOS18")
            ),
        ])
        TxPNTuple = namedtuple("TxPN", "txp txn")
        serd_pads = p.request("AD9174_JESD204")

        self.submodules.crg = CRG(
            settings, 5.12e9, p, serd_pads, [self.ctrl.reset]
        )

        # ----------------------------
        #  GTX phy
        # ----------------------------
        # 1 JESD204BPhyTX with its own `TX<N>` clock domain for each lane
        phys = []
        for i, (tx_p, tx_n) in enumerate(zip(serd_pads.tx_p, serd_pads.tx_n)):
            phy = JESD204BPhyTX(
                self.crg.qpll0 if i <= 3 else self.crg.qpll1,
                TxPNTuple(tx_p, tx_n),
                self.crg.sys_clk_freq,
                transceiver="gtx",
                # on `AD9172_FMC_EBZ` SERDIN 0 - 3 are of __inverted__ polarity!
                polarity=1 if i <= 3 else 0
            )
            p.add_period_constraint(
                phy.transmitter.cd_tx.clk,
                1e9 / self.crg.tx_clk_freq
            )
            # Tell vivado the clocks are async
            p.add_false_path_constraints(
                self.crg.cd_sys.clk,
                phy.transmitter.cd_tx.clk
            )
            phys.append(phy)
            setattr(self, 'phy{}'.format(i), phy)

        self.submodules.core = LiteJESD204BCoreTX(
            phys,
            settings
        )
        self.submodules.control = LiteJESD204BCoreControl(self.core, phys)

        jsync = Signal()
        self.specials += DifferentialInput(
            serd_pads.jsync0_p, serd_pads.jsync0_n, jsync
        )
        self.core.register_jsync(jsync)
        self.comb += p.request('user_led').eq(jsync)

        j_ref = Signal()
        self.specials += DifferentialInput(
            serd_pads.sysref_p, serd_pads.sysref_n, j_ref
        )
        self.core.register_jref(j_ref)
        self.submodules.f_ref = freqmeter.FreqMeter(
            self.sys_clk_freq,
            clk=j_ref
        )

        # ----------------------------
        #  Application layer
        # ----------------------------
        self.submodules.prbs_gen = PRBSGen(self, settings)
        self.submodules.sample_gen = SampleGen(self, settings, 64)
        self.comb += [
            self.prbs_gen.sink.eq(self.sample_gen.source),  # has a bypass mode
            self.core.sink.eq(self.prbs_gen.source)
        ]

        # ----------------------------
        #  SPI master
        # ----------------------------
        spi_pads = p.request("AD9174_SPI")
        self.comb += spi_pads.spi_en.eq(0)
        self.submodules.spi = spi.SPIMaster(
            spi_pads,
            32,
            self.clk_freq,
            int(1e6)
        )

        # ----------------------------
        #  Serial to Wishbone bridge
        # ----------------------------
        self.submodules.uart = uart.UARTWishboneBridge(
            p.request("serial"),
            self.clk_freq,
            baudrate=1152000
        )
        self.add_wb_master(self.uart.wishbone)

        # FPGA identification
        self.submodules.dna = dna.DNA()

        settings.LID = 0
        settings.calc_fchk()
        settings.export_constants(self)

        # Analyzer
        analyzer_groups = {
            0: [
                self.core.ready,
                self.core.jsync,
                self.core.jref,

                self.core.link0.fsm,
                self.core.link0.source.data,
                self.core.link0.source.ctrl,

                self.core.lmfc.count,
                self.core.lmfc.zero,
                self.core.lmfc.jref,
                self.core.lmfc.is_load
            ]
        }
        self.submodules.analyzer = LiteScopeAnalyzer(
            analyzer_groups,
            4096,
            csr_csv="build/analyzer.csv",
            clock_domain='jesd'
        )
        self.add_csr("analyzer")


def main():
    parser = ArgumentParser(description=__doc__)
    builder_args(parser)
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load", action="store_true", help="Load bitstream")
    args = parser.parse_args()

    soc = Top(vc707.Platform())
    builder = Builder(soc, **builder_argdict(args))
    builder.build(run=args.build)

    if args.load:
        prog = soc.platform.create_programmer()
        prog.load_bitstream(
            os.path.join(builder.gateware_dir, soc.build_name + ".bit")
        )


if __name__ == "__main__":
    main()
