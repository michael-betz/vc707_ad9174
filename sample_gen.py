"""
JESD204b application layer
Play samples from blockram memory
"""
from sys import path
from math import ceil
path.append("spi")
from migen import *
from litex.soc.interconnect.csr import CSRStorage
from litex.soc.interconnect.csr import AutoCSR
from migen.genlib.cdc import MultiReg
from litex.soc.interconnect import wishbone


class SampleGen(Module, AutoCSR):
    def __init__(self, soc, settings, depth=256):
        '''
        Continuously blast out samples from Memory.
        The `max_ind` csr specifies the maximum index when to roll over.

        depth: max. number of samples which can be stored (multiple of 16)

        Use 32 bit wide block ram for 1:1 mapping on the wishbone bus
        These memories are mapped to the S * 16 bit parallel samples
        So the lower 16 bit are a sample and the upper 16 bit are the next
        sample.
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

        # For each converter channel
        for m, (conv, _) in enumerate(self.source.iter_flat()):
            # How many 32 bit memories do we need to hold all parallel samples
            n_mems = ceil(len(conv) / 32)
            # For each 32 bit memory
            for n_mem in range(n_mems):
                name = "m{:}_n{:}".format(m, n_mem)

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
                p1 = mem.get_port(clock_domain="jesd", mode=READ_FIRST)
                self.specials += p1
                # Redundant registers for (maybe) better bram timing ...
                # TODO vivado does not want to merge them into the bram, why?
                b_ram_out = Signal(32, reset_less=True)
                adr_ = Signal(len(self.max_ind.storage), reset_less=True)
                self.sync.jesd += [
                    adr_.eq(adr),
                    p1.adr.eq(adr_),

                    b_ram_out.eq(p1.dat_r),
                    conv[n_mem * 32: (n_mem + 1) * 32].eq(b_ram_out)
                ]

                adr_offset += 0x10000
