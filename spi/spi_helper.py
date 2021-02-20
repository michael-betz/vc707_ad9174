import sys
import json
from collections import Iterable

class NewSpi:
    '''
    only supports 4 wire SPI with
    litex/soc/cores/spi.py
    enough for HMC chip in read only mode
    '''
    SPI_CONTROL_START = 0
    SPI_CONTROL_LENGTH = 8
    SPI_STATUS_DONE = 0

    def __init__(self, r, LEN=24):
        ''' LEN: bits / transfer '''
        self.r = r
        self._ctrl = LEN << NewSpi.SPI_CONTROL_LENGTH
        r.regs.spi_control.write(self._ctrl)

    def rxtx(self, dat24, cs, isWrite=None):
        '''
        dat24: data to send (LEN bits)
        cs: when high, enable asserting cs = low during transfer
        isWrite: ignored
        '''
        self.r.regs.spi_mosi.write(dat24 << 8)
        self.r.regs.spi_cs.write(cs)
        self.r.regs.spi_control.write(self._ctrl | 1)
        return self.r.regs.spi_miso.read() & 0xFFFFFF


class AdSpi(NewSpi):
    def __init__(self, r, f_json='regs_ad9174.json'):
        super().__init__(r)
        with open('regs_ad9174.json') as f:
            self.regs = json.load(f)
        self._make_index()

    def _make_index(self):
        self.reg_names = dict()
        self.bit_names = dict()
        for k, v in self.regs.items():
            if v['name'] == 'RESERVED':
                continue
            # if v['name'] in self.reg_names:
            #     kk = self.reg_names[v['name']]
            #     print('reg {} ({:03x}) already exist ({:03x})'.format(
            #         v['name'], int(k), int(kk))
            #     )
            self.reg_names[v['name']] = k
            for bk, bv in v['bits'].items():
                if bv['name'] == 'RESERVED':
                    continue
                self.bit_names[bv['name']] = (k, bk)

    def rr(self, adr, length=1):
        ''' read register @ adr, which can be integer or reg. name '''
        if type(adr) is str:
            adr = int(self.reg_names[adr])
        if length > 1:
            return [self.rr(adr + i) for i in range(length)]
        word = (1 << 23) | ((adr & 0x7FFF) << 8)
        return self.rxtx(word, 1, True) & 0xFF

    def wr(self, adr, val):
        ''' write register @ adr, which can be integer or reg. name '''
        if type(adr) is str:
            adr = int(self.reg_names[adr])
        if isinstance(val, Iterable):
            for i, v in enumerate(val):
                self.wr(adr + i, v)
            return
        word = (0 << 23) | ((adr & 0x7FFF) << 8) | (val & 0xFF)
        return self.rxtx(word, 1, True)

    def help(self, s):
        ''' lookup a register address or name in the datasheet '''
        k = str(s)
        bit = None

        if s in self.bit_names:
            k, bit = self.bit_names[s]
        elif s in self.reg_names:
            k = self.reg_names[s]

        print('reg 0x{:03x}, {:s}:'.format(
            int(k),
            self.regs[k]['name'],
        ))
        for bk in sorted(self.regs[k]['bits'], reverse=True):
            bv = self.regs[k]['bits'][bk]
            if bit is None or bk == bit:
                print('    bit {:s}, {:s}, {:s}, reset 0x{:02x}\n    {:}\n'.format(
                    bk,
                    bv['name'],
                    bv['access'],
                    bv['reset'],
                    bv['description']
                ))
