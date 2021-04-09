'''
'''
from migen import *
from sim_soc import SimSoC, main
from sys import path
path.append("..")
path.append("../spi")
from sample_gen_pulse import SampleGenPulse
from ad9174 import Ad9174Settings


class SimSampleGenPulse(SimSoC):
    def __init__(self):
        '''
        Demonstrate the `SampleGenPulse` arbitrary waveform generator
        '''
        SimSoC.__init__(self, cpu_type=None)

        # Need this for SampleGenPulse
        self.settings = settings = Ad9174Settings(
            20, 1, 1,
            FCHK_OVER_OCTETS=True,
            SCR=1,
            DID=0x5A,
            BID=0x05
        )
        settings.calc_fchk()
        print(settings)

        # Fake jesd clock domain
        self.clock_domains.cd_jesd = ClockDomain()
        self.comb += [
            ClockSignal('jesd').eq(ClockSignal('sys')),
            # use AsyncResetSynchronizer with real hardware
            ResetSignal('jesd').eq(ResetSignal('sys'))
        ]

        # ----------------------------
        #  DUT
        # ----------------------------
        self.submodules.sample_gen = SampleGenPulse(self, settings, depth=8192)
        self.add_csr("sample_gen")


if __name__ == "__main__":
    main(SimSampleGenPulse())
