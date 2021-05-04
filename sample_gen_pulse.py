"""
JESD204b application layer
Play samples from blockram memory at trigger
"""
from math import ceil
from migen import Module, Signal, If, Record, Memory, READ_FIRST
from litex.soc.interconnect.csr import CSRStorage
from litex.soc.interconnect.csr import AutoCSR
from migen.genlib.cdc import MultiReg
from litex.soc.interconnect import wishbone


class TriggerGen(Module, AutoCSR):
    def __init__(self, ext_trig_in=None):
        '''
        registers:
        `enable_ext_trig`:  enable external trigger
        `wfm_len`:          waveform length after trigger.
        `trig_cnt_max`:     max pieriod of cycle count in internal trigger
        '''
        # external trigger
        self.ext_trig_in = ext_trig_in
        if ext_trig_in is None:
            self.ext_trig_in = Signal()

        # capture rising edge of ext trigger
        ext_trig_in_jesd1 = Signal()
        self.specials += MultiReg(
            self.ext_trig_in, ext_trig_in_jesd1, "jesd", n=2)
        ext_trig_in_jesd2 = Signal()
        self.specials += MultiReg(
            ext_trig_in_jesd1, ext_trig_in_jesd2, "jesd", n=2)
        ext_trig_flag = Signal()
        self.comb += ext_trig_flag.eq(~ext_trig_in_jesd2 & ext_trig_in_jesd1)

        # internal trigger
        # 25 bit enable trigger down to 312.5e6 // (1<<25) = 10Hz
        self.trig_cnt_max = CSRStorage(25)
        trig_cnt_max_ = Signal.like(self.trig_cnt_max.storage)
        # cross clock domains to jesd
        self.specials += MultiReg(
            self.trig_cnt_max.storage, trig_cnt_max_, "jesd")
        trig_cnt = Signal.like(self.trig_cnt_max.storage)
        self.sync.jesd += [
            If(
                trig_cnt >= trig_cnt_max_,
                trig_cnt.eq(0)
            ).Else(
                trig_cnt.eq(trig_cnt + 1)
            )
        ]
        int_trig_flag = Signal()
        self.comb += int_trig_flag.eq(trig_cnt == 1)

        # internal / external trigger selection
        self.enable_ext_trig = CSRStorage(1)
        self.wfm_trigger = Signal()
        self.sync.jesd += [
            If(
               self.enable_ext_trig.storage,
               self.wfm_trigger.eq(ext_trig_flag)
            ).Else(
               self.wfm_trigger.eq(int_trig_flag)
            )
        ]


class SampleGenPulse(Module, AutoCSR):
    def __init__(self, soc, settings, depth=256,
                 wfm_trigger=None, adr_offset=0x10000000,
                 idx=0, clock_domain="jesd"):
        '''
        registers:
        `depth`:            max. number of samples which can be stored,
                            must be multiple of 16
        `wfm_trigger`:      trigger signal to start playing buffer
        `adr_offset`:       global memory address
        `idx`:              index of fmc board

        Use 32 bit wide block ram for 1:1 mapping on the wishbone bus
        These memories are mapped to the S * 16 bit parallel samples
        So the lower 16 bit are a sample and the upper 16 bit are the next
        sample.
        '''
        if wfm_trigger is None:
            wfm_trigger = Signal()

        self.source = Record(settings.get_dsp_layout())

        self.wfm_len = CSRStorage(16)
        # cross clock domains to jesd
        wfm_len_ = Signal.like(self.wfm_len.storage)
        self.specials += MultiReg(self.wfm_len.storage, wfm_len_, "jesd")
        adr = Signal.like(self.wfm_len.storage)

        wfm_last = Signal()
        counting = Signal()
        self.comb += wfm_last.eq(adr == wfm_len_ - 1)

        self.sync.jesd += [
            If(
                wfm_last,
                counting.eq(0)
            ).Elif(
                wfm_trigger,
                counting.eq(1)
            )
        ]

        self.sync.jesd += [
            If(
                counting,
                adr.eq(adr + 1)
            ).Else(
                adr.eq(0)
            )
        ]

        # For each converter channel
        for m, (conv, _) in enumerate(self.source.iter_flat()):
            # How many 32 bit memories do we need to hold all parallel samples
            n_mems = ceil(len(conv) / 32)  # = 8
            # For each 32 bit memory
            for n_mem in range(n_mems):
                name = "d{:}_m{:}_n{:}".format(idx, m, n_mem)

                # This generates 32 bit wide blockram, wishbone access is 1:1
                # divide depth by 16 because we provide 16 samples in parallel
                mem = Memory(32, depth // 16, name=name)

                self.specials += mem
                sram = wishbone.SRAM(mem)
                self.submodules += sram
                soc.register_mem(
                    name,
                    adr_offset,  # [bytes]
                    sram.bus,
                    mem.depth * 4  # [bytes]
                )

                # with mode=WRITE_FIRST vivado does only do distributed RAM
                p1 = mem.get_port(clock_domain=clock_domain, mode=READ_FIRST)
                self.specials += p1
                # Redundant registers for (maybe) better bram timing ...
                # TODO vivado does not want to merge them into the bram, why?
                b_ram_out = Signal(32, reset_less=True)
                adr_ = Signal(len(self.wfm_len.storage), reset_less=True)
                self.sync.jesd += [
                    adr_.eq(adr),
                    p1.adr.eq(adr_),
                    b_ram_out.eq(p1.dat_r),
                    conv[n_mem * 32: (n_mem + 1) * 32].eq(b_ram_out)
                ]

                adr_offset += 0x10000
