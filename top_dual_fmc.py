"""
Demonstrate AD9174-FMC-EBZ board on VC707

Contains the gateware needed to establish the jesd204b link.

Connects trough UART to litex_server on a host PC to access the internal
control and status registers and the AD9174 SPI interface.
"""
from sys import path
from os.path import join
path.append("spi")
# from migen import *
from migen import (Module, ClockDomain, Signal, reduce, or_,
                   Instance, ResetSignal, ClockSignal, If, ClockDomainsRenamer)
from argparse import ArgumentParser
from collections import namedtuple
from litex.build.io import DifferentialInput
from migen.genlib.resetsync import AsyncResetSynchronizer
from migen.genlib.cdc import MultiReg
from litex.build.generic_platform import Subsignal, Pins, IOStandard, Misc
from litex.soc.cores import dna, uart, spi, freqmeter
from litex.soc.interconnect import wishbone
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
from sample_gen_pulse import SampleGenPulse


class CRG(Module, AutoCSR):
    def __init__(self, settings, f_dsp, p, serd_pads, add_rst=[]):
        '''
        f_dsp = rate at which DSP datapath is clocked (jesd clock domain) [Hz]
        add_rst = additional reset signals for sys_clk
          must be active high and will be synchronized with sys_clk
          p = vc707 platform instance
        '''
        self.clock_domains.cd_sys = ClockDomain()

        # System clock from crystal on fpga board
        self.sys_clk_freq = int(1e9 / p.default_clk_period)

        # DSP rate: depends on f_dsp and dividers in AD9174 + HMC7044
        self.tx_clk_freq = int(f_dsp)

        # fixed serializer factor
        self.gtx_line_freq = self.tx_clk_freq * 40

        # # #

        clk_pads = p.request(p.default_clk_name)
        self.specials += DifferentialInput(
            clk_pads.p, clk_pads.n, self.cd_sys.clk
        )

        rst_sum = Signal()
        self.comb += rst_sum.eq(reduce(or_, add_rst))

        # Handle the GTX clock input
        self.refclk0 = Signal()
        self.specials += Instance(
            "IBUFDS_GTE2",
            i_CEB=0,
            i_I=serd_pads.clk_p,
            i_IB=serd_pads.clk_n,
            o_O=self.refclk0
        )
        self.clock_domains.cd_jesd = ClockDomain()

        self.specials += [
            AsyncResetSynchronizer(self.cd_sys, rst_sum),
            AsyncResetSynchronizer(self.cd_jesd, ResetSignal('sys')),
            Instance("BUFG", i_I=self.refclk0, o_O=self.cd_jesd.clk)
        ]

        # Add a frequency counter to `cd_jesd` (160 MHz) measures in [Hz]
        self.submodules.f_jesd = freqmeter.FreqMeter(
            self.sys_clk_freq,
            clk=ClockSignal('jesd')
        )


class LedBlinker(Module):
    def __init__(self, f_clk=100e6, out=None):
        """
        for debugging clocks
        toggles outputs at 1 Hz
        use ClockDomainsRenamer()!
        """
        self.out = out
        if out is None:
            self.out = Signal()

        ###

        max_cnt = int(f_clk / 2)
        cntr = Signal(max=max_cnt + 1)
        self.sync += [
            cntr.eq(cntr + 1),
            If(cntr == max_cnt,
                cntr.eq(0),
                self.out.eq(~self.out)
            )
        ]


class Top(SoCCore):
     def __init__(self, p, f_dsp, **kwargs):
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
            20, 1, 1,
            FCHK_OVER_OCTETS=True,
            SCR=1,
            DID=0x5A,
            BID=0x05
        )
        settings.calc_fchk()
        print(settings)

        for c in [
            "control", "dna", "crg", "f_ref", "spi_fmc1", "spi_fmc2", "sample_gen", "prbs_gen"
        ]:
            self.add_csr(c)

        for i in range(2 * settings.L):
            self.add_csr("phy{}".format(i))

        # ----------------------------
        #  Ports
        # ----------------------------
        p.add_extension([
            (
                "AD9174_JESD204_FMC1", 0,
                # CLK comes from HMC7044 CLKOUT12, goes to GTX (312.5 MHz)
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
            (
                "AD9174_SPI_FMC1", 0,
                # FMC_CS1 (AD9174), FMC_CS2 (HMC7044)
                Subsignal("cs_n", Pins("FMC1_HPC:LA04_N FMC1_HPC:LA05_P")),
                Subsignal("miso", Pins("FMC1_HPC:LA04_P"), Misc("PULLUP TRUE")),
                Subsignal("mosi", Pins("FMC1_HPC:LA03_N")),
                Subsignal("clk",  Pins("FMC1_HPC:LA03_P")),
                Subsignal("spi_en", Pins("FMC1_HPC:LA05_N")),
                IOStandard("LVCMOS18")
            ),
            (
                "AD9174_JESD204_FMC2", 0,
                # CLK comes from HMC7044 CLKOUT12, goes to GTX (312.5 MHz)
                Subsignal("clk_p", Pins("FMC2_HPC:GBTCLK0_M2C_C_P")),
                Subsignal("clk_n", Pins("FMC2_HPC:GBTCLK0_M2C_C_N")),

                # GTX data lanes
                Subsignal("tx_p",  Pins(" ".join(
                    ["FMC2_HPC:DP{}_C2M_P".format(i) for i in [5, 6, 4, 7, 3, 2, 1, 0][:settings.L]]
                ))),
                Subsignal("tx_n",  Pins(" ".join(
                    ["FMC2_HPC:DP{}_C2M_N".format(i) for i in [5, 6, 4, 7, 3, 2, 1, 0][:settings.L]]
                ))),

                # JSYNC comes from AD9174 SYNC_OUT_0B, SYNC_OUT_1B
                Subsignal("jsync0_p", Pins("FMC2_HPC:LA01_CC_P"), IOStandard("LVDS")),
                Subsignal("jsync0_n", Pins("FMC2_HPC:LA01_CC_N"), IOStandard("LVDS")),

                # Subsignal("jsync1_p", Pins("FMC2_HPC:LA02_P"), IOStandard("LVDS")),
                # Subsignal("jsync1_n", Pins("FMC2_HPC:LA02_N"), IOStandard("LVDS")),

                # SYSREF comes from HMC7044 CLKOUT13 (16 MHz)
                Subsignal("sysref_p", Pins("FMC2_HPC:LA00_CC_P"), IOStandard("LVDS")),
                Subsignal("sysref_n", Pins("FMC2_HPC:LA00_CC_N"), IOStandard("LVDS"))
            ),
            (
                "AD9174_SPI_FMC2", 0,
                # FMC_CS1 (AD9174), FMC_CS2 (HMC7044)
                Subsignal("cs_n", Pins("FMC2_HPC:LA04_N FMC2_HPC:LA05_P")),
                Subsignal("miso", Pins("FMC2_HPC:LA04_P"), Misc("PULLUP TRUE")),
                Subsignal("mosi", Pins("FMC2_HPC:LA03_N")),
                Subsignal("clk",  Pins("FMC2_HPC:LA03_P")),
                Subsignal("spi_en", Pins("FMC2_HPC:LA05_N")),
                IOStandard("LVCMOS18")
            ),
        ])
        TxPNTuple = namedtuple("TxPN", "txp txn")
        serd_pads_fmc1 = p.request("AD9174_JESD204_FMC1")
        serd_pads_fmc2 = p.request("AD9174_JESD204_FMC2")

        # use FMC1 to receive JESD_CLK (312.5MHz) and SYSREF (3.9MHz)
        self.submodules.crg = CRG(
            settings, f_dsp, p, serd_pads_fmc1, [self.ctrl.reset]
        )

        # ----------------------------
        #  GTX phy
        # ----------------------------
        # 1 JESD204BPhyTX with its own `TX<N>` clock domain for each lane

        # The two GTX quad PLLs for up to 16 lanes
        # These are taken care of and reset by GTXInit()
        qplls = []
        fmc_info = {
            'fmc1': {
                'id': 1,
                'qplls': [],
                'serd_pads': serd_pads_fmc1,
                'phys': []
            },
            'fmc2': {
                'id': 1,
                'qplls': [],
                'serd_pads': serd_pads_fmc2,
                'phys': []
            }
        }

        for name, fmc in fmc_info.items():
            for ix in range((settings.L) // 4):
                qpll = GTXQuadPLL(
                    self.crg.refclk0,
                    self.crg.tx_clk_freq,
                    self.crg.gtx_line_freq
                )
                fmc['qplls'].append(qpll)
                self.submodules += qpll

            for j, (tx_p, tx_n) in enumerate(
                    zip(fmc['serd_pads'].tx_p, fmc['serd_pads'].tx_n)):
                phy = JESD204BPhyTX(
                    pll=fmc['qplls'][j // 4],
                    tx_pads=TxPNTuple(tx_p, tx_n),
                    sys_clk_freq=self.crg.sys_clk_freq,
                    transceiver="gtx",
                    # on `AD9172_FMC_EBZ` SERDIN 0 - 3 are of __inverted__ polarity!
                    polarity=1 if j <= 3 else 0
                )
                # period = 1 / 312.5 = 3.2 ns
                p.add_period_constraint(
                    phy.transmitter.cd_tx.clk,
                    1e9 / self.crg.tx_clk_freq
                )
                # Tell vivado the clocks are async
                p.add_false_path_constraints(
                    self.crg.cd_sys.clk,
                    phy.transmitter.cd_tx.clk
                )
                fmc['phys'].append(phy)
                setattr(self, 'phy{}'.format(fmc['id'] + j), phy)

        self.submodules.core1 = LiteJESD204BCoreTX(
            fmc_info['fmc1']['phys'],
            settings
        )
        self.submodules.control1 = LiteJESD204BCoreControl(self.core1, fmc_info['fmc1']['phys'])

        self.submodules.core2 = LiteJESD204BCoreTX(
            fmc_info['fmc2']['phys'],
            settings
        )
        self.submodules.control2 = LiteJESD204BCoreControl(self.core2, fmc_info['fmc2']['phys'])

        jsync_fmc1 = Signal()
        jsync_fmc2 = Signal()
        self.specials += DifferentialInput(
            serd_pads_fmc1.jsync0_p, serd_pads_fmc1.jsync0_n, jsync_fmc1
        )
        self.specials += DifferentialInput(
            serd_pads_fmc2.jsync0_p, serd_pads_fmc2.jsync0_n, jsync_fmc2
        )

        # ----------------------------
        # Combine two SYNC_OUT signals
        # ----------------------------
        jsync = Signal()
        self.comb += jsync.eq(jsync_fmc1 & jsync_fmc2)
        self.core1.register_jsync(jsync)
        self.core2.register_jsync(jsync)
        self.comb += p.request('user_led').eq(jsync)

        # ----------------------------
        # Only use FMC1 for SYSREF
        # ----------------------------
        j_ref = Signal()
        self.specials += DifferentialInput(
            serd_pads_fmc1.sysref_p, serd_pads_fmc1.sysref_n, j_ref
        )
        self.core1.register_jref(j_ref)
        self.core2.register_jref(j_ref)
        self.submodules.f_ref = freqmeter.FreqMeter(
            self.sys_clk_freq,
            clk=j_ref
        )

        # ----------------------------
        #  Application layer
        # ----------------------------
        # self.submodules.sample_gen = SampleGen(self, settings, depth=4096)
        self.submodules.sample_gen = SampleGenPulse(
            self, settings, depth=8192, ext_trig_in=p.request('user_sma_gpio_p'))
        self.comb += [
            self.core1.sink.eq(self.sample_gen.source)
        ]

        # ----------------------------
        #  SPI master
        # ----------------------------
        spi_pads_fmc1 = p.request("AD9174_SPI_FMC1")
        self.comb += spi_pads_fmc1.spi_en.eq(0)
        self.submodules.spi_fmc1 = spi.SPIMaster(
            spi_pads_fmc1,
            32,
            self.clk_freq,
            int(1e6)
        )
        spi_pads_fmc2 = p.request("AD9174_SPI_FMC2")
        self.comb += spi_pads_fmc2.spi_en.eq(0)
        self.submodules.spi_fmc2 = spi.SPIMaster(
            spi_pads_fmc2,
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
            baudrate=115200
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
                self.core1.ready,
                self.core1.jsync,
                self.core1.jref,

                self.core1.link0.fsm,
                self.core1.link0.source.data,
                self.core1.link0.source.ctrl,

                self.core1.lmfc.count,
                self.core1.lmfc.zero,
                self.core1.lmfc.jref,
                self.core1.lmfc.is_load
            ]
        }
        self.submodules.analyzer = LiteScopeAnalyzer(
            analyzer_groups,
            4096,
            csr_csv="build/analyzer.csv",
            clock_domain='jesd'
        )
        self.add_csr("analyzer")

        # LEDs should blink at exactly 1 Hz
        # LED 0: sys_clk, LED 1: tx_clk
        self.submodules += LedBlinker(
            self.crg.sys_clk_freq, p.request('user_led')
        )
        bl = LedBlinker(self.crg.tx_clk_freq, p.request('user_led'))
        self.submodules += ClockDomainsRenamer('jesd')(bl)


def main():
    parser = ArgumentParser(description=__doc__)
    builder_args(parser)
    parser.add_argument("--build", action="store_true", help="Build bitstream")
    parser.add_argument("--load", action="store_true", help="Load bitstream")
    parser.add_argument("--f_dsp", default=312.5e6, help="DSP clock rate (see spreadsheet) [Hz]")
    args = parser.parse_args()

    if args.load:
        prog = vc707.Platform().create_programmer()
        prog.load_bitstream('build/xilinx_vc707/gateware/xilinx_vc707.bit')
    else:
        soc = Top(vc707.Platform(), int(args.f_dsp))
        builder = Builder(soc, **builder_argdict(args))
        builder.build(run=args.build)



if __name__ == "__main__":
    main()