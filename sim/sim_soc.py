#!/usr/bin/env python3
"""
Connect litex_server to a verilator emulation for testing and experimenting.
"""
import argparse

from migen import *
from migen.genlib.io import CRG

from litex.build.generic_platform import *
from litex.build.sim import SimPlatform
from litex.build.sim.config import SimConfig

from litex.soc.integration.soc_core import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *
from litex.soc.cores.uart import Stream2Wishbone, RS232PHYModel


class SimPins(Pins):
    def __init__(self, n=1):
        Pins.__init__(self, "s " * n)


_io = [
    ("sys_clk", 0, SimPins(1)),
    ("sys_rst", 0, SimPins(1)),
    ("ext_trig", 0, SimPins(1)),
    ("serial", 0,
        Subsignal("source_valid", SimPins()),
        Subsignal("source_ready", SimPins()),
        Subsignal("source_data", SimPins(8)),

        Subsignal("sink_valid", SimPins()),
        Subsignal("sink_ready", SimPins()),
        Subsignal("sink_data", SimPins(8))
    )
]


class SimSoC(SoCCore):
    def __init__(
        self,
        **kwargs
    ):
        # Setting sys_clk_freq too low will cause wishbone timeouts !!!
        sys_clk_freq = int(20e6)
        print(kwargs)
        SoCCore.__init__(
            self,
            SimPlatform("SIM", _io),
            clk_freq=sys_clk_freq,
            integrated_rom_size=0,
            integrated_sram_size=0,
            ident="LiteX Simulation",
            ident_version=True,
            with_uart=False,
            **kwargs
        )
        # crg
        self.submodules.crg = CRG(self.platform.request("sys_clk"))

        # ----------------------------
        #  Virtual serial to Wishbone bridge
        # ----------------------------
        # bridge virtual serial phy as wishbone master
        self.submodules.uart_phy = RS232PHYModel(self.platform.request("serial"))
        self.submodules.uartbone = \
            Stream2Wishbone(self.uart_phy, clk_freq=self.clk_freq)
        self.bus.add_master(name="uartbone", master=self.uartbone.wishbone)


def main(soc):
    parser = argparse.ArgumentParser(description="LiteX SoC Simulation test")
    builder_args(parser)
    parser.add_argument("--trace", action="store_true",
                        help="engage VCD tracing on power up")
    args = parser.parse_args()

    soc.platform.add_debug(soc, reset=args.trace)

    builder_kwargs = builder_argdict(args)
    builder_kwargs['output_dir'] = 'out'
    builder_kwargs['csr_csv'] = 'out/csr.csv'

    sim_config = SimConfig(default_clk="sys_clk")
    sim_config.add_module("serial2tcp", "serial", args={
        "port": 1111
    })

    builder = Builder(soc, **builder_kwargs)
    builder.build(
        run=True,
        sim_config=sim_config,
        trace=True,  # compile in trace support
        # trace_fst=True  # alternative to .vcd format
    )


if __name__ == "__main__":
    main(SimSoC(cpu_type=None))
