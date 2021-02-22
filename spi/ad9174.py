from time import sleep
from collections import namedtuple
from spi_helper import AdSpi
from hmc7044 import Hmc7044
from litejesd204b.common import JESD204BSettings
from litejesd204b.transport import seed_to_data


def hd(dat):
    ''' print a hex-dump '''
    for i, d in enumerate(dat):
        if i % 8 == 0 and len(dat) > 8:
            print('\n{:04x}: '.format(i), end='')
        print('{:02x} '.format(d), end='')
    print()


class Ad9174Settings(JESD204BSettings):
    JM = namedtuple('JESD_MODE', 'L M F S NP N K HD')
    MODES = {
         0: JM(1, 2, 4, 1, 16, 16, 32, 1),
         1: JM(2, 4, 4, 1, 16, 16, 32, 1),
         2: JM(3, 6, 4, 1, 16, 16, 32, 1),
         3: JM(2, 2, 2, 1, 16, 16, 32, 1),
         4: JM(4, 4, 2, 1, 16, 16, 32, 1),
         5: JM(1, 2, 3, 1, 12, 12, 32, 1),
         6: JM(2, 4, 3, 1, 12, 12, 32, 1),
         7: JM(1, 4, 8, 1, 16, 16, 32, 1),
         8: JM(4, 2, 1, 1, 16, 16, 32, 1),
         9: JM(4, 2, 2, 2, 16, 16, 32, 1),
        10: JM(8, 2, 1, 2, 16, 16, 32, 1),
        11: JM(8, 2, 2, 4, 16, 16, 32, 1),
        12: JM(8, 2, 3, 8, 12, 12, 32, 1),
        18: JM(4, 1, 1, 2, 16, 16, 32, 1),
        19: JM(4, 1, 2, 4, 16, 16, 32, 1),
        20: JM(8, 1, 1, 4, 16, 16, 32, 1),
        21: JM(8, 1, 2, 8, 16, 16, 32, 1),
        22: JM(4, 2, 3, 4, 12, 12, 32, 1)
    }

    def __init__(
        self,
        JESD_MODE=0,
        INTERP_CH=None,
        INTERP_MAIN=None,
        json_file=None,
        **kwargs
    ):
        '''
        JESD_MODE:
            a number defining the set of JESD parameters, as commonly used
            by Analog Devices.

        INTERP_CH:
            channelizer datapath interpolation factor

        INTERP_MAIN:
            main datapath interpolation factor

        kwargs:
            individually overwrite JESD parameters

        json_file:
            .json file to import jesd parameters from.
            If this is given all other init parameters are ignored.
        '''
        if json_file is not None:
            super().__init__(json_file=json_file)
            return

        self.INTERP_CH = INTERP_CH
        self.INTERP_MAIN = INTERP_MAIN
        self.JESD_MODE = JESD_MODE
        mode_dict = Ad9174Settings.MODES[JESD_MODE]._asdict()
        mode_dict.update(**kwargs)

        super().__init__(**mode_dict)

        self.DSP_CLK_DIV = 0
        if INTERP_CH is not None and INTERP_MAIN is not None:
            # f_DAC / f_PCLK: this is the clock driving the FPGA
            # The division is split over AD9174 (/4) and HMC7044 (/N)
            self.DSP_CLK_DIV = self.L * 32 * INTERP_CH * INTERP_MAIN // \
                self.M // self.NP

            # Assume frequency divider by 4 in hmc7044 is hard-coded
            if (self.DSP_CLK_DIV % 4) > 0:
                raise ValueError('invalid clocking')

        self.calc_fchk()  # first one comes for free

    def __repr__(self):
        s = '----------------\n'
        s += ' JESD mode {}\n'.format(self.JESD_MODE)
        s += '----------------\n'
        s += 'INTERP_CH: {}  INTERP_MAIN: {}  DSP_CLK_DIV: {}\n'.format(
            self.INTERP_CH, self.INTERP_MAIN, self.DSP_CLK_DIV
        )
        s += super().__repr__()
        return s

    def export_constants(self, soc):
        '''
        export all settings as litex constants, which will be written to
        csr.csv / csr.json
        '''
        super().export_constants(soc)
        soc.add_constant('JESD_JESD_MODE', self.JESD_MODE)
        soc.add_constant('JESD_INTERP_CH', self.INTERP_CH)
        soc.add_constant('JESD_INTERP_MAIN', self.INTERP_MAIN)
        soc.add_constant('JESD_DSP_CLK_DIV', self.DSP_CLK_DIV)


class Ad9174Init():
    def __init__(self, r, settings):
        '''
        r:
            a litex_remote_server handle for register access

        settings:
            a Ad9174Settings instance
        '''
        self.regs = r.regs
        self.settings = settings
        self.ad = AdSpi(r)
        self.hmc = Hmc7044(r)

    def init_hmc(self):
        '''
        init for external 5.12 GHz sampling clock input to DAC
        '''
        hmc = self.hmc
        hmc.init_hmc7044()

        clk_div = self.settings.DSP_CLK_DIV // 4
        hmc.setup_channel(12, clk_div, sync_en=False)     # DEV_CLK to the FPGA

        # for litejesd, SYSREF must be an integer multiple of the LMFC
        lmfc_cycles = self.settings.K // self.settings.FR_CLK
        hmc.setup_channel(3, clk_div * lmfc_cycles * 10)   # SYSREF (DAC)
        hmc.setup_channel(13, clk_div * lmfc_cycles * 10)  # SYSREF (FPGA)
        # hmc.trigger_reseed()
        self.hmc.trigger_div_reset()


    def init_ad9174(
        self,
        ADC_CLK_DIV=4,
        USE_PLL=True,
        M_DIV=2,
        N_DIV=2,
        OUT_DIV=2,
        SYSREF_ERR_WINDOW=2
    ):
        '''
        ADC_CLK_DIV: Aux. clock output divider: 1 = off
        M_DIV: reference clock divider: 1 = off
        N_DIV: feedback divider
        OUT_DIV: output divider, 1 = off, 2 or 3
        SYSREF_ERR_WINDOW:
            Amount of jitter allowed on the SYSREF input. SYSREF jitter
            variations larger than this trigger an interrupt. [DAC clocks]
        '''
        wr = self.ad.wr
        rr = self.ad.rr
        s = self.settings

        # ------------------------
        #  Reset and general init
        # ------------------------
        # put GTX PHYs and jesd core in reset
        self.regs.control_control.write(0b01)

        # Power up sequence, Table 51
        wr(0x000, 0x81)  # Soft reset
        wr(0x000, 0x3C)  # 4 - wire SPI mode + ADDRINC

        wr(0x091, 0x00)  # Power up clock RX
        wr(0x206, 0x01)  # Bring CDR out of reset
        wr(0x705, 0x01)  # LOAD NVRAM FACTORY SETTINGS
        wr(0x090, 0x00)  # Power on DACs and bias supply
        print('AD917X_NVM_BLR_DONE:', (rr(0x705) >> 1) & 1)

        # Print product ID (0x9174)
        val = rr('SPI_PRODIDH') << 8 | rr('SPI_PRODIDL')
        print('PROD_ID: 0x{:04x}'.format(val))
        val = rr('SPI_CHIPGRADE')
        print('PROD_GRADE: {:x}  DEV_REVISION: {:x}'.format(
            val >> 8, val & 0xF
        ))

        wr(0x100, 0x01)  # Put digital datapath in reset

        if not USE_PLL:
            # Disable DAC PLL and config for external clock, Table 52
            wr(0x095, 0x01)
            wr(0x790, 0xFF)  # DACPLL_POWER_DOWN
            wr(0x791, 0x1F)
            wr(0x799, ((ADC_CLK_DIV - 1) << 6) | (N_DIV & 0x3F))
        else:
            wr(0x095, 0x00)
            wr(0x790, 0x00)
            wr(0x791, 0x00)

            wr(0x796, 0xE5)
            wr(0x7A0, 0xBC)
            wr(0x794, 0x08)  # DACPLL_CP: charge pump current

            wr(0x797, 0x10)
            wr(0x797, 0x20)
            wr(0x798, 0x10)
            wr(0x7A2, 0x7F)
            sleep(0.1)

            wr(0x799, ((ADC_CLK_DIV - 1) << 6) | (N_DIV & 0x3F))
            wr(0x793, (0x06 << 2) | ((M_DIV - 1) & 0x03))
            wr(0x094, OUT_DIV - 1)
            wr(0x792, 0x02)  # Reset VCO
            wr(0x792, 0x00)
            sleep(0.1)

            dac_pll_lock = rr(0x7B5) & 0x01
            print('DAC PLL locked:', dac_pll_lock)
            if dac_pll_lock < 1:
                raise RuntimeError('DAC PLL not locked :(')

        # Delay Lock Loop (DLL) Configuration
        wr(0x0C0, 0x00)  # Power-up delay line.
        wr(0x0DB, 0x00)  # Update DLL settings to circuitry.
        wr(0x0DB, 0x01)
        wr(0x0DB, 0x00)
        wr(0x0C1, 0x68)  # set search mode for f_DAC > 4.5 GHz
        wr(0x0C1, 0x69)  # set DLL_ENABLE
        wr(0x0C7, 0x01)  # Enable DLL read status.
        dll_lock = rr(0x0C3) & 0x01
        print('DLL locked:', dll_lock)
        if dll_lock < 1:
            raise RuntimeError('Delay locked loop not locked :(')

        wr(0x008, (0b01 << 6) | 0b000001)  # Select DAC0, channel0
        print('SPI_PAGEINDX: 0b{:08b}'.format(rr('SPI_PAGEINDX')))

        # Magic numbers from Table 54 (calibration)
        wr(0x050, 0x2A)
        wr(0x061, 0x68)
        wr(0x051, 0x82)
        wr(0x051, 0x83)
        cal_stat = rr(0x052)
        wr(0x081, 0x03)  # Power down calibration clocks
        print('CAL_STAT:', cal_stat)  # 1 = success
        if cal_stat != 1:
            raise RuntimeError('Calibration failed :(')

        # ---------------------------
        # Table 58, SERDES interface
        # ---------------------------
        # disable serdes PLL, clear sticky loss of lock bit
        wr(0x280, 0x04)
        wr(0x280, 0x00)
        # Power down the entire JESD204b receiver analog
        # (all eight lanes and bias)
        wr(0x200, 0x01)

        # EQ settings for < 11 dB insertion loss
        wr(0x240, 0xAA)
        wr(0x241, 0xAA)
        wr(0x242, 0x55)
        wr(0x243, 0x55)
        wr(0x244, 0x1F)
        wr(0x245, 0x1F)
        wr(0x246, 0x1F)
        wr(0x247, 0x1F)
        wr(0x248, 0x1F)
        wr(0x249, 0x1F)
        wr(0x24A, 0x1F)
        wr(0x24B, 0x1F)

        # Power down the unused PHYs
        # when L is 3, the first 3 lanes stay powered up
        wr(0x201, 0xFF - 2**s.L + 1)
        wr(0x203, 0x00)  # don't power down sync0, sync1
        wr(0x253, 0x01)  # Sync0: 0 = CMOS, 1 = LVDS
        wr(0x254, 0x01)  # Sync1: 0 = CMOS, 1 = LVDS

        # SERDES required register write.
        wr(0x210, 0x16)
        wr(0x216, 0x05)
        wr(0x212, 0xFF)
        wr(0x212, 0x00)
        wr(0x210, 0x87)
        wr(0x210, 0x87)
        wr(0x216, 0x11)
        wr(0x213, 0x01)
        wr(0x213, 0x00)
        wr(0x200, 0x00)  # Power up the SERDES circuitry blocks.
        sleep(0.1)

        # SERDES required register write.
        wr(0x210, 0x86)
        wr(0x216, 0x40)
        wr(0x213, 0x01)
        wr(0x213, 0x00)
        wr(0x210, 0x86)
        wr(0x216, 0x00)
        wr(0x213, 0x01)
        wr(0x213, 0x00)
        wr(0x210, 0x87)
        wr(0x216, 0x01)
        wr(0x213, 0x01)
        wr(0x213, 0x00)
        wr(0x280, 0x05)

        # Start up SERDES PLL and initiate calibration
        wr(0x280, 0x01)
        pll_locked = rr(0x281) & 0x01
        print('SERDES PLL locked:', pll_locked)
        if pll_locked != 1:
            raise RuntimeError("SERDES PLL not locked")

        # Setup deterministic latency buffer release delay
        wr(0x304, 0)  # LMFC_DELAY_0 for link0 [PCLK cycles], max is 0x3F
        wr(0x305, 0)  # LMFC_DELAY_1 for link1 [PCLK cycles]
#         wr(0x306, 3)  # LMFC_VAR_0  variable delay buffer, max is 0x0C
#         wr(0x307, 3)  # LMFC_VAR_1

        # Enable all interrupts
        wr('JESD_IRQ_ENABLEA', 0xFF)
        wr('JESD_IRQ_ENABLEB', 1)  # config mismatch interrupt
        wr('IRQ_ENABLE', 0xFF)
        wr('IRQ_ENABLE0', 0xFF)
        wr('IRQ_ENABLE1', 0xFF)
        wr('IRQ_ENABLE2', 0xFF)

        # ---------------------
        # JESD init
        # ---------------------
        wr(0x100, 0x00)  # Power up digital datapath clocks
        wr(0x110, (0 << 5) | s.JESD_MODE)  # 0 = single link

        wr(0x111, (s.INTERP_MAIN << 4) | s.INTERP_CH)
        mode_not_in_table = (rr(0x110) >> 7) & 0x01
        print('MODE_NOT_IN_TABLE:', mode_not_in_table)
        if mode_not_in_table:
            raise RuntimeError('JESD mode / interpolation factors not valid')

        wr(0x084, (0 << 6))  # SYSREF_PD: 0 = AC couple, don't power down
        wr(0x300, 0b0001)  # select single link, page link0, enable link0
        wr(0x475, 0x09)  # Soft reset the JESD204B quad-byte deframer

        # Write JESD settings blob to AD9174 registers
        for i, o in enumerate(s.octets):
            wr(0x450 + i, o)

        # bit0 checksum method: 0 = sum fields (seems buggy), 1 = sum registers
        wr('CTRLREG1', 0x11)
        wr('ERRORTHRES', 0x01)  # Error threshold
        wr(0x475, 1)  # Bring the JESD204B quad-byte deframer out of reset.

        # Enable the sync logic, and set the rotation mode to reset
        # the synchronization logic upon a sync reset trigger.
        wr(0x03B, 0xF1)  # enable sync circuit (no datapath ramping)
        wr(0x039, SYSREF_ERR_WINDOW)  # Allowable ref jitter (DAC clocks)
        wr(0x036, 0x10)  # ignore the first 16 sysref edges

        # TODO: Table 56, setup channel datapath
        # TODO: Table 57, setup main datapath


    def setTone(
        self,
        dac_select=1,
        f_out=None,
        ampl=None,
        del_a=None,
        mod_b=None,
        phase=None,
        f_ref=5125e6
    ):
        '''
        dac_select: 1 = first DAC, 2 = second DAC, 3 = both DACs
        '''
        wr = self.ad.wr
        rr = self.ad.rr
        s = self.settings

        # Select a DAC main datapath
        dac_select &= 0x03

        if ampl is not None:
            # Set DC amplitude level (2 bytes), 0x50FF is full-scale tone
            # Updates immediately without the need for DDSM_FTW_LOAD_REQ
            # TODO: not clear if synchronized to 16 bit write
            ampl_b = int(min(ampl, 1.0) * 0x50FF).to_bytes(2, 'little')
            wr(0x008, dac_select)  # need to use __CHANNEL_PAGE_ !!!!
            wr(0x148, ampl_b)
            print('DC_CAL_TONE: ', end='')
            hd(rr(0x148, 2))

        # All other regs are on MAINDAC_PAGE
        wr(0x008, (dac_select << 6))

        if f_out is not None:
            # ftw updates on posedge DDSM_FTW_LOAD_REQ
            ftw_b = int(f_out / f_ref * 2**48).to_bytes(6, 'little')  # [Hz]
            wr(0x114, ftw_b)  # Write 6 bytes FTW into main NCO
            print('DDSM_FTW: ', end='')
            hd(rr(0x114, 6))

        if phase is not None:
            # DDSM_NCO_PHASE_OFFSET updates immediately without DDSM_FTW_LOAD_REQ
            # However it updates after each 8th risign edge on the SPI clock (see scope shot)
            # it does not synchronize to the 16 bit register width :(
            # --> phase jump of ~1.4 degree on register rollover is unavoidable :(
            phase_b = int(phase / 180 * 2**15).to_bytes(2, 'little', signed=True)  # [deg]
            wr(0x11C, phase_b)  # Write 2 bytes
            print('DDSM_NCO_PHASE_OFFSET: ', end='')
            hd(rr(0x11C, 2))

        if del_a is not None:
            # Modulus and Delta are updated after posedge DDSM_FTW_LOAD_REQ
            # confirmed by scope measurement
            wr(0x12A, del_a.to_bytes(6, 'little'))  # Write 6 bytes Delta [A]
            print('DDSM_ACC_DELTA: ', end='')
            hd(rr(0x12A, 6))

            wr(0x124, mod_b.to_bytes(6, 'little'))  # Write 6 bytes Modulus [B]
            print('DDSM_ACC_MODULUS: ', end='')
            hd(rr(0x124, 6))

        if f_out is not None or del_a is not None:
            # Positive edge on DDSM_FTW_LOAD_REQ applies the FTW and causes a phase glitch!
            # Random phase jump -pi .. pi on selected DAC
            wr(0x113, 0x01)  # Update settings
            print('DDSM_FTW_LOAD_ACK:', (rr(0x113) >> 1) & 0x01)
            wr(0x113, 0x00)

    def trigger_jref_sync(self):
        '''
        Re-aligns the LMFC with the sysref signal.
        Will also shutdown and re-initialize the link.
        '''
        ad = self.ad
        ad.wr(0x03a, 0)
        ad.wr(0x03a, 2)   # trigger one shot sync
        sync_done = (ad.rr(0x3a) >> 4) & 1
        print('SYNC_ROTATION_DONE', sync_done)
        if not sync_done:
            raise RuntimeError('Sync. of LMFC with JREF failed. JREF missing?')
        print('DYN_LINK_LATENCY {:2d} cycles'.format(ad.rr(0x302)))

    def print_irq_flags(self, reset=False, silent=False):
        '''
        print the status of the latched error flags
        and optionally resets them.
        returns True on error
        '''
        def p(name, reset, bit_strs):
            val = self.ad.rr(name)
            isErr = False
            for i, b_str in enumerate(bit_strs):
                if b_str is not None:
                    if val & 1 and not silent:
                        print('{:}: {:}'.format(name, b_str))
                        isErr = True
                val >>= 1
            if reset:
                self.ad.wr(name, 0xFF)
            return isErr

        isErr = p('JESD_IRQ_STATUSA', reset, [
            'Code Group Sync. failed',
            'Frame Sync. failed',
            'ILAS checksum bad',
            'ILAS failed',
            'Interlane deskew failed',
            'Unexpected K > threshold',
            'Not in table > threshold',
            'Bad disparity > threshold'
        ])

        isErr |= p('JESD_IRQ_STATUSB', reset, [
            'lane0 ILAS config mismatch'
        ])

        isErr |= p('IRQ_STATUS', reset, [
            'DAC0 PRBS error',
            'DAC1 PRBS error',
            'Lane FIFO overflow/underflow',
            'JESD204x receiver not ready',
            'SYSREF jitter too large'
        ])

        isErr |= p('IRQ_STATUS0', reset, [
            'DAC0 Power Amplifier error',
            None, None,
            'DAC0 calibration not done'
        ])

        isErr |= p('IRQ_STATUS1', reset, [
            'DAC1 Power Amplifier error',
            None, None,
            'DAC1 calibration not done'
        ])

        isErr |= p('IRQ_STATUS2', reset, [
            'DAC PLL locked',
            'DAC PLL lock lost',
            None, None,
            'DLL locked',
            'DLL lost'
        ])

        return isErr

    def fpga_print_clocks(self):
        ''' Print measured clock frequency in FPGA '''
        f_jesd = self.regs.crg_f_jesd_value.read()
        f_ref = self.regs.f_ref_value.read()
        print('f_jesd = {:.6f} MHz  f_ref = {:.6f} MHz'.format(
            f_jesd / 1e6, f_ref / 1e6
        ))

    def fpga_set_tp(self, on=True, tp=0b1111111101111111111100000000000000000000):
        ''' set test-pattern mode and 40 bit pattern for all GTX phys '''
        for i in range(self.settings.L):
            getattr(self.regs, 'phy{:}_transmitter_tp_on'.format(i)).write(on)
            getattr(self.regs, 'phy{:}_transmitter_tp'.format(i)).write(tp)

    def get_phy_snapshot(self, silent=False):
        ''' print and return snapshot of received PHY data for each active lane '''
        ad = self.ad
        ad.wr('PHY_PRBS_TEST_EN', 0xFF)  # Needed: clock to test module
        ad.wr('PHY_PRBS_TEST_CTRL', 0b01)  # rst
        vals = []
        if not silent:
            print('PHY_SNAPSHOT_DATA:')
        for lane in range(self.settings.L):
            ad.wr('PHY_PRBS_TEST_CTRL', (lane << 4))
            ad.wr('PHY_DATA_SNAPSHOT_CTRL', 0x01)
            ad.wr('PHY_DATA_SNAPSHOT_CTRL', 0x00)
            val = 0
            for i in range(5):
                val = (val << 8) | ad.rr(0x323 - i)
            vals.append(val)
            if not silent:
                print('{0:}: 0x{1:010x}, 0b{1:040b}'.format(lane, val))
        return vals

    def phy_pattern_test(self, tp=0b1111111101111111111100000000000000000000):
        '''
        apply 40 bit test-pattern `tp` on GTX phy and verify received values
        on AD9174 PHY match for each lane (except for some bit shift).
        returns True on error
        '''
        isFailed = False
        bTp = '{:040b}'.format(tp)

        self.fpga_set_tp(True, tp)
        vals = self.get_phy_snapshot(True)
        self.fpga_set_tp(False)

        for i, v in enumerate(vals):
            bVal = '{:040b}'.format(v)
            isMatch = bTp in (bVal + bVal)
            isFailed |= not isMatch
            print('{0:}: 0x{1:010x}, 0b{1:040b}, match: {2:}'.format(i, v, isMatch))

        return isFailed

    def print_ilas(self):
        '''
        returns True on error
        '''
        print("JESD settings, received on lane 0 vs (programmed):")
        # FCHK_N = 1:
        # Checksum is calculated by summing the registers containing the packed
        # link configuration fields
        # (sum of Register 0x450 to Register 0x45A, modulo 256).
        chk_rx = 0
        chk_prog = 0
        cfg_mismatch = False
        for i in range(0x400, 0x40E):
            rx_val = self.ad.rr(i)
            prog_val = self.ad.rr(i + 0x50)
            if (i >= 0x400) and (i <= 0x40a):
                chk_rx += rx_val
                chk_prog += prog_val
            print('{:03x}: {:02x} ({:02x})'.format(i + 0x50, rx_val, prog_val))
            if rx_val != prog_val:
                cfg_mismatch = True
        print('CHK: {:02x} ({:02x}) {:}'.format(chk_rx & 0xFF, chk_prog & 0xFF, 'config mismatch!' if cfg_mismatch else ''))
        return cfg_mismatch

    def print_lane_status(self):
        def st(n, fmt='08b'):
            print('{:>17s}: {:{:}}'.format(n, self.ad.rr(n), fmt))

        print('\nLane status:')
        st('LANE_DESKEW')
        st('BAD_DISPARITY')
        st('NOT_IN_TABLE')
        st('UNEXPECTED_KCHAR')
        st('CODE_GRP_SYNC')
        st('FRAME_SYNC')
        st('GOOD_CHECKSUM')
        st('INIT_LANE_SYNC')
        st('FIFO_STATUS_REG_0')
        st('FIFO_STATUS_REG_1')

        print('fpga j_sync errs: {:}'.format(
            self.regs.control_jsync_errors.read()
        ))

    def test_stpl(self, wait_secs=1):
        ''' retruns true on failure '''
        print('STPL test:')
        test_fail = False
        ad = self.ad
        self.regs.control_stpl_enable.write(1)

        for converter in range(self.settings.M):
            for sample in range(self.settings.S * self.settings.FR_CLK):
                channel = converter // 2  # 0 - 2
                i_q = converter % 2
                tp = seed_to_data((converter << 8) | sample)
                # tp = 0x597A  # I
                # tp = 0xD27A  # Q

                cfg = (sample << 4) | (channel << 2)
                ad.wr(0x32c, cfg)         # select sample and chanel, disable
                ad.wr(0x32e, tp >> 8)
                ad.wr(0x32d, tp & 0xFF)
                ad.wr(0x32f, (i_q << 6))    # 0: I,  1: Q
                ad.wr(0x32c, cfg | 0x01)  # enable
                ad.wr(0x32c, cfg | 0x03)  # reset
                ad.wr(0x32c, cfg | 0x01)  # run
                sleep(wait_secs)
                is_fail = ad.rr('SHORT_TPL_TEST_3') & 1
                test_fail |= is_fail
                print('converter: {:}, sample: {:}, tp: {:04x}, fail: {:}'.format(
                    converter, sample, tp, is_fail
                ))
        self.regs.control_stpl_enable.write(0)
        return test_fail
