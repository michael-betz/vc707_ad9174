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


class HmcSpi(NewSpi):
    def __init__(self, r):
        self.reg001 = (1 << 6) | (1 << 5)
        self.reg004 = 0
        super().__init__(r)

    def wr(self, adr, val):
        # R/W + W1 + W0 + A[13] + D[8]
        word = (0 << 23) | ((adr & 0x1FFF) << 8) | (val & 0xFF)
        self.rxtx(word, 2, True)

    def rr(self, adr):
        '''
        works with OLD_SPI only and no chance on
        AD9174-FMC-EBZ due to hardware bug:
        https://ez.analog.com/data_converters/high-speed_dacs/f/q-a/115934/ad9174-fmc-ebz-reading-hmc7044-registers-over-fmc
        '''
        word = (1 << 23) | ((adr & 0x1FFF) << 8)
        # Send 24 bit / 32 bit starting from MSB
        word <<= 8
        return self.rxtx(word, 2, False) & 0xFF

    def init_hmc7044(self):
        self.wr(0x000, 1)  # reset
        self.wr(0x000, 0)
        self.wr(0x054, 0)  # Disable SDATA driver (uni-direct. buffer)

        self.reg001 = (1 << 6) | (1 << 5)
        self.wr(0x001, self.reg001)  # High performance dividers / PLL

        # VCO Selection
        # 0 Internal disabled/external
        # 1 High
        # 2 Low
        VCO_SELECT = 3
        self.wr(0x003, (0 << VCO_SELECT))

        # set global enable for channel
        self.reg004 = 0
        self.wr(0x004, self.reg004)

        # clkin1 as external VCO input
        self.wr(0x005, (1 << 5))

        # Updates from datasheet Table 74 for `optimum performance` :p
        self.wr(0x09F, 0x4D)
        self.wr(0x0A0, 0xDF)
        self.wr(0x0A5, 0x06)
        self.wr(0x0A8, 0x06)
        self.wr(0x0B0, 0x04)

        # Disable all channels
        for chId in range(14):
            reg0 = 0xC8 + 10 * chId
            self.wr(reg0, 0x00)
            self.wr(reg0 + 8, 0x00)

    def trigger_reseed(self):
        '''
        Requests the centralized resync timer and FSM to reseed any of the
        output dividers that are programmed to pay attention to sync events.
        This signal is only acknowledged if the resync FSM has completed all
        events (has finished any previous pulse generator and/or sync events,
        and is in the done state; SYSREF FSM State[3:0] = 0010).
        '''
        self.wr(0x001, self.reg001 | 0x80)
        self.wr(0x001, self.reg001)

    def trigger_div_reset(self):
        '''
        Resets all dividers and FSMs. Does not affect configuration registers.
        '''
        self.wr(0x001, self.reg001 | 0x02)
        self.wr(0x001, self.reg001)

    def setup_channel(
        self, chId, f_div=1, sync_en=True, fine_delay=0, coarse_delay=0
    ):
        '''
            set a channel up for CML mode,
            100 Ohm termination,
            no delays

            chId:
                channel Id starting at 0
            f_div:
                frequency divison factor from 1 to 4094
            sync_en:
                channel will be suspectible to sync events if enabled
            fine_delay:
                noisy analog phase delay in 25 ps steps (max. value 23)
            coarse_delay:
                phase delay in 1/2 input clock cycles (max. value 17)
        '''
        # set global enable for channel
        self.reg004 |= (1 << (chId // 2))
        self.wr(0x004, self.reg004)

        reg0 = 0xC8 + 10 * chId

        HP_MODE_EN = 7
        SYNC_EN = 6
        SLIP_EN = 5
        STARTUP_MODE = 2
        MULTISLIP_EN = 1
        CH_EN = 0
        self.wr(
            reg0,
            # High performance mode. Adjusts the divider and buffer
            # bias to improve swing/phase noise at the expense of
            # power.
            (1 << HP_MODE_EN) |

            (sync_en << SYNC_EN) |
            # Configures the channel to normal mode with
            # asynchronous startup, or to a pulse generator mode
            # with dynamic start-up. Note that this must be set to
            # asynchronous mode if the channel is unused.
            # 0 Asynchronous.
            # 1 Reserved.
            # 2 Reserved.
            # 3 Dynamic.
            (0 << STARTUP_MODE) |
            # Channel enable. If this bit is 0, channel is disabled.
            (1 << CH_EN)
        )

        # 12-bit channel divider setpoint LSB. The divider
        # supports even divide ratios from 2 to 4094. The
        # supported odd divide ratios are 1, 3, and 5. All even and
        # odd divide ratios have 50.0% duty cycle.
        # f_div = 10
        self.wr(reg0 + 1, f_div & 0xFF)
        self.wr(reg0 + 2, (f_div >> 8) & 0x0F)

        # 24 fine delay steps. Step size = 25 ps. Values greater
        # than 23 have no effect on analog delay
        self.wr(reg0 + 3, fine_delay & 0x1F)

        # 17 coarse delay steps. Step size = 1/2 VCO cycle. This flip
        # flop (FF)-based digital delay does not increase noise
        # level at the expense of power. Values greater than 17
        # have no effect on coarse delay.
        self.wr(reg0 + 4, coarse_delay & 0x1F)

        # 12-bit multislip digital delay amount LSB.
        # Step size = (delay amount: MSB + LSB) × VCO cycles. If
        # multislip enable bit = 1, any slip events (caused by GPI,
        # SPI, SYNC, or pulse generator events) repeat the
        # number of times set by 12-Bit Multislip Digital
        # Delay[11:0] to adjust the phase by step size.
        multislip_delay = 0
        self.wr(reg0 + 5, multislip_delay & 0xFF)
        self.wr(reg0 + 6, (multislip_delay >> 8) & 0x0F)

        # Channel output mux selection.
        # 0 Channel divider output.
        # 1 Analog delay output.
        # 2 Other channel of the clock group pair.
        # 3 Input VCO clock (fundamental). Fundamental can also
        #   be generated with 12-Bit Channel Divider[11:0] = 1.
        self.wr(reg0 + 7, 0)

        DRIVER_IMPEDANCE = 0
        DRIVER_MODE = 3
        self.wr(
            reg0 + 8,
            # Output driver impedance selection for CML mode.
            # 0 Internal resistor disable.
            # 1 Internal 100 Ω resistor enable per output pin.
            # 2 Reserved.
            # 3 Internal 50 Ω resistor enable per output pin.
            (1 << DRIVER_IMPEDANCE) |
            # Output driver mode selection.
            # 0 CML mode.
            # 1 LVPECL mode.
            # 2 LVDS mode.
            # 3 CMOS mode.
            (0 << DRIVER_MODE)
        )


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
