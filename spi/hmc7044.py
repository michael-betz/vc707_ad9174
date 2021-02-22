from spi_helper import NewSpi


class Hmc7044(NewSpi):
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

    def init_hmc7044_ext(self):
        '''
        init for external clock input on CLKIN1 (J41 on eval board)
        Only use the output frequency dividers. Both PLLs are disabled.
        '''
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

    def init_hmc7044_int(self, N2=21):
        '''
        Setup the 2 PLLs to clock from the on-board 122.8 MHz crystal + VCO
        Does not setup the output channels
        N2: clock multiplier factor. 8 .. 65535. f_VCO2 = 122.88 MHz * N2
        '''
        # I was using the hmc7044 eval board windows software to generate the
        # init sequence:  https://www.analog.com/en/products/hmc7044.html

        # glbl_cfg1_swrst[0:0] = 0x0
        self.wr(0x0, 0x0)

        # glbl_cfg1_sleep[0:0] = 0x0
        # glbl_cfg1_restart[1:1] = 0x0
        # sysr_cfg1_pulsor_req[2:2] = 0x0
        # grpx_cfg1_mute[3:3] = 0x0
        # pll1_cfg1_forceholdover[4:4] = 0x0
        # glbl_cfg1_perf_pllvco[5:5] = 0x1
        # dist_cfg1_perf_floor[6:6] = 0x1
        # sysr_cfg1_reseed_req[7:7] = 0x0
        self.wr(0x1, 0x60)

        # sysr_cfg1_rev[0:0] = 0x0
        # sysr_cfg1_slipN_req[1:1] = 0x0
        # pll2_cfg1_autotune_trig[2:2] = 0x1
        self.wr(0x2, 0x4)

        # glbl_cfg1_ena_pll1[0:0] = 0x1
        # glbl_cfg1_ena_pll2[1:1] = 0x1
        # glbl_cfg1_ena_sysr[2:2] = 0x1
        # glbl_cfg2_ena_vcos[4:3] = 0x2
        # glbl_cfg1_ena_sysri[5:5] = 0x1
        fVco = 122.88e6 * N2
        if fVco < 2.15e9 or fVco > 3.55e9:
            raise RuntimeError("f_VCO out of range: {:.6f} MHz".format(
                fVco / 1e6
            ))
        isHighVco = 122.88e6 * N2 >= 2.765e9
        vcoSel = 1 if isHighVco else 2
        self.wr(0x3, 0x27 | (vcoSel << 3))

        # glbl_cfg7_ena_clkgr[6:0] = 0x42
        self.wr(0x4, 0x42)

        # glbl_cfg4_ena_rpath[3:0] = 0x1
        # dist_cfg1_refbuf0_as_rfsync[4:4] = 0x0
        # dist_cfg1_refbuf1_as_extvco[5:5] = 0x0
        # pll2_cfg2_syncpin_modesel[7:6] = 0x1
        self.wr(0x5, 0x41)

        # glbl_cfg1_clear_alarms[0:0] = 0x1
        self.wr(0x6, 0x1)

        # glbl_reserved[0:0] = 0x0
        self.wr(0x7, 0x0)

        # glbl_cfg1_dis_pll2_syncatlock[0:0] = 0x1
        self.wr(0x9, 0x1)

        # glbl_cfg5_ibuf0_en[0:0] = 0x1
        # glbl_cfg5_ibuf0_mode[4:1] = 0x1
        self.wr(0xA, 0x3)

        # glbl_cfg5_ibuf1_en[0:0] = 0x0
        # glbl_cfg5_ibuf1_mode[4:1] = 0x0
        self.wr(0xB, 0x0)

        # glbl_cfg5_ibuf2_en[0:0] = 0x0
        # glbl_cfg5_ibuf2_mode[4:1] = 0x0
        self.wr(0xC, 0x0)

        # glbl_cfg5_ibuf3_en[0:0] = 0x0
        # glbl_cfg5_ibuf3_mode[4:1] = 0x0
        self.wr(0xD, 0x0)

        # glbl_cfg5_ibufv_en[0:0] = 0x1
        # glbl_cfg5_ibufv_mode[4:1] = 0x3
        self.wr(0xE, 0x7)

        # pll1_cfg2_rprior1[1:0] = 0x0
        # pll1_cfg2_rprior2[3:2] = 0x1
        # pll1_cfg2_rprior3[5:4] = 0x2
        # pll1_cfg2_rprior4[7:6] = 0x3
        self.wr(0x14, 0xE4)

        # pll1_cfg3_los_valtime_sel[2:0] = 0x3
        self.wr(0x15, 0x3)

        # pll1_cfg2_holdover_exitcrit[1:0] = 0x0
        # pll1_cfg2_holdover_exitactn[3:2] = 0x1
        self.wr(0x16, 0x4)

        # pll1_cfg7_hodac_offsetval[6:0] = 0x0
        self.wr(0x17, 0x0)

        # pll1_cfg2_hoadc_bw_reduction[1:0] = 0x0
        # pll1_cfg1_hodac_force_quickmode[2:2] = 0x0
        # pll1_cfg1_hodac_dis_avg_track[3:3] = 0x0
        self.wr(0x18, 0x0)

        # pll1_cfg1_los_uses_vcxodiv[0:0] = 0x0
        # pll1_cfg1_los_bypass_lcmdiv[1:1] = 0x0
        self.wr(0x19, 0x0)

        # pll1_cfg4_cpi[3:0] = 0x6
        self.wr(0x1A, 0x6)

        # pll1_cfg1_pfd_invert[0:0] = 0x0
        # pll1_cfg1_cppulldn[1:1] = 0x0
        # pll1_cfg1_cppullup[2:2] = 0x0
        # pll1_cfg1_cpendn[3:3] = 0x1
        # pll1_cfg1_cpenup[4:4] = 0x1
        self.wr(0x1B, 0x18)

        # pll1_cfg8_los_div_setpt_r0[7:0] = 0x4
        self.wr(0x1C, 0x4)

        # pll1_cfg8_los_div_setpt_r1[7:0] = 0x4
        self.wr(0x1D, 0x4)

        # pll1_cfg8_los_div_setpt_r2[7:0] = 0x4
        self.wr(0x1E, 0x4)

        # pll1_cfg8_los_div_setpt_r3[7:0] = 0x4
        self.wr(0x1F, 0x4)

        # pll1_cfg8_los_div_setpt_vcxo[7:0] = 0x4
        self.wr(0x20, 0x4)

        # pll1_cfg16_refdivrat_lsb[7:0] = 0x4
        self.wr(0x21, 0x4)

        # pll1_cfg16_refdivrat_msb[7:0] = 0x0
        self.wr(0x22, 0x0)

        # pll1_cfg16_fbdivrat_lsb[7:0] = 0x10
        self.wr(0x26, 0x10)

        # pll1_cfg16_fbdivrat_msb[7:0] = 0x0
        self.wr(0x27, 0x0)

        # pll1_cfg5_lkdtimersetpt[4:0] = 0xF
        # pll1_cfg1_use_slip_for_lkdrst[5:5] = 0x0
        self.wr(0x28, 0xF)

        # pll1_cfg1_automode[0:0] = 0x0
        # pll1_cfg1_autorevertive[1:1] = 0x0
        # pll1_cfg1_holdover_uses_dac[2:2] = 0x1
        # pll1_cfg2_manclksel[4:3] = 0x0
        # pll1_cfg1_byp_debouncer[5:5] = 0x0
        self.wr(0x29, 0x4)

        # pll1_hoff_timer_setpoint[7:0] = 0x0
        self.wr(0x2A, 0x0)

        # pll2_reserved[7:0] = 0x1
        self.wr(0x31, 0x1)

        # pll2_cfg1_rpath_x2_bypass[0:0] = 0x1
        self.wr(0x32, 0x1)

        # pll2_rdiv_cfg12_divratio_lsb[7:0] = 0x1
        self.wr(0x33, 0x1)

        # pll2_rdiv_cfg12_divratio_msb[3:0] = 0x0
        self.wr(0x34, 0x0)

        # pll2_vdiv_cfg16_divratio_lsb[7:0] = 0x15
        self.wr(0x35, N2)

        # pll2_vdiv_cfg16_divratio_msb[7:0] = 0x0
        self.wr(0x36, 0x0)

        # pll2_cfg4_cp_gain[3:0] = 0xF
        self.wr(0x37, 0xF)

        # pll2_pfd_cfg1_invert[0:0] = 0x0
        # pll2_pfd_cfg1_force_dn[1:1] = 0x0
        # pll2_pfd_cfg1_force_up[2:2] = 0x0
        # pll2_pfd_cfg1_dn_en[3:3] = 0x1
        # pll2_pfd_cfg1_up_en[4:4] = 0x1
        self.wr(0x38, 0x18)

        # pll2_cfg1_oscout_path_en[0:0] = 0x0
        # pll2_cfg2_oscout_divratio[2:1] = 0x0
        self.wr(0x39, 0x0)

        # pll2_cfg1_obuf0_drvr_en[0:0] = 0x0
        # pll2_cfg5_obuf0_drvr_res[2:1] = 0x0
        # pll2_cfg5_obuf0_drvr_mode[5:4] = 0x0
        self.wr(0x3A, 0x0)

        # pll2_cfg1_obuf1_drvr_en[0:0] = 0x0
        # pll2_cfg5_obuf1_drvr_res[2:1] = 0x0
        # pll2_cfg5_obuf1_drvr_mode[5:4] = 0x0
        self.wr(0x3B, 0x0)

        # glbl_cfg5_gpi1_en[0:0] = 0x0
        # glbl_cfg5_gpi1_sel[4:1] = 0x0
        self.wr(0x46, 0x0)

        # glbl_cfg5_gpi2_en[0:0] = 0x0
        # glbl_cfg5_gpi2_sel[4:1] = 0x0
        self.wr(0x47, 0x0)

        # glbl_cfg5_gpi3_en[0:0] = 0x0
        # glbl_cfg5_gpi3_sel[4:1] = 0x4
        self.wr(0x48, 0x8)

        # glbl_cfg5_gpi4_en[0:0] = 0x0
        # glbl_cfg5_gpi4_sel[4:1] = 0x8
        self.wr(0x49, 0x10)

        # glbl_cfg8_gpo1_en[0:0] = 0x0
        # glbl_cfg8_gpo1_mode[1:1] = 0x1
        # glbl_cfg8_gpo1_sel[7:2] = 0x7
        self.wr(0x50, 0x1E)

        # glbl_cfg8_gpo2_en[0:0] = 0x0
        # glbl_cfg8_gpo2_mode[1:1] = 0x1
        # glbl_cfg8_gpo2_sel[7:2] = 0xA
        self.wr(0x51, 0x2A)

        # glbl_cfg8_gpo3_en[0:0] = 0x0
        # glbl_cfg8_gpo3_mode[1:1] = 0x0
        # glbl_cfg8_gpo3_sel[7:2] = 0x0
        self.wr(0x52, 0x0)

        # glbl_cfg8_gpo4_en[0:0] = 0x0
        # glbl_cfg8_gpo4_mode[1:1] = 0x0
        # glbl_cfg8_gpo4_sel[7:2] = 0x0
        self.wr(0x53, 0x0)

        # glbl_cfg2_sdio_en[0:0] = 0x0
        # glbl_cfg2_sdio_mode[1:1] = 0x1
        self.wr(0x54, 0x2)

        # sysr_cfg3_pulsor_mode[2:0] = 0x1
        self.wr(0x5A, 0x1)

        # sysr_cfg1_synci_invpol[0:0] = 0x0
        # sysr_cfg1_pll2_carryup_sel[1:1] = 0x1
        # sysr_cfg1_ext_sync_retimemode[2:2] = 0x1
        self.wr(0x5B, 0x6)

        # sysr_cfg16_divrat_lsb[7:0] = 0x0
        self.wr(0x5C, 0x0)

        # sysr_cfg16_divrat_msb[3:0] = 0x6
        self.wr(0x5D, 0x6)

        # dist_cfg1_extvco_islowfreq_sel[0:0] = 0x0
        # dist_cfg1_extvco_div2_sel[1:1] = 0x0
        self.wr(0x64, 0x0)

        # clkgrpx_cfg1_alg_dly_lowpwr_sel[0:0] = 0x0
        self.wr(0x65, 0x0)

        # alrm_cfg4_pll1_los4_allow[3:0] = 0x0
        # alrm_cfg1_pll1_hold_allow[4:4] = 0x0
        # alrm_cfg1_pll1_lock_allow[5:5] = 0x0
        # alrm_cfg1_pll1_acq_allow[6:6] = 0x0
        # alrm_cfg1_pll1_nearlock_allow[7:7] = 0x0
        self.wr(0x70, 0x0)

        # alrm_cfg1_pll2_lock_allow[0:0] = 0x0
        # alrm_cfg1_sysr_unsyncd_allow[1:1] = 0x0
        # alrm_cfg1_clkgrpx_validph_allow[2:2] = 0x0
        # alrm_cfg1_plls_both_locked_allow[3:3] = 0x0
        # alrm_cfg1_sync_req_allow[4:4] = 0x1
        self.wr(0x71, 0x10)

        # glbl_ro8_chipid_lob[7:0] = 0x51
        self.wr(0x78, 0x51)

        # glbl_ro8_chipid_mid[7:0] = 0x16
        self.wr(0x79, 0x16)

        # glbl_ro8_chipid_hib[7:0] = 0x30
        self.wr(0x7A, 0x30)

        # alrm_ro1_alarm_masked_viaspi[0:0] = 0x1
        self.wr(0x7B, 0x1)

        # alrm_ro4_pll1_los4_now[3:0] = 0xF
        # alrm_ro1_pll1_hold_now[4:4] = 0x1
        # alrm_ro1_pll1_lock_now[5:5] = 0x0
        # alrm_ro1_pll1_acq_now[6:6] = 0x0
        # alrm_ro1_pll1_nearlock_now[7:7] = 0x0
        self.wr(0x7C, 0x1F)

        # alrm_ro1_pll2_lock_now[0:0] = 0x1
        # alrm_ro1_sysr_unsyncd_now[1:1] = 0x1
        # alrm_ro1_clkgrpx_validph_now[2:2] = 0x0
        # alrm_ro1_plls_both_locked_now[3:3] = 0x0
        # alrm_ro1_sync_req_now[4:4] = 0x1
        self.wr(0x7D, 0x13)

        # alrm_ro4_pll1_los4_latch[3:0] = 0xF
        # alrm_ro1_pll1_hold_latch[4:4] = 0x1
        # alrm_ro1_pll1_acq_latch[5:5] = 0x1
        # alrm_ro1_pll2_acq_latch[6:6] = 0x1
        self.wr(0x7E, 0x7F)

        # pll1_ro3_fsm_state[2:0] = 0x4
        # pll1_ro2_selected_clkidx[4:3] = 0x0
        # pll1_ro2_bestclk[6:5] = 0x0
        self.wr(0x82, 0x4)

        # pll1_ro7_dac_avg[6:0] = 0x4C
        self.wr(0x83, 0x4C)

        # pll1_ro7_dac_current[6:0] = 0x4C
        # pll1_ro1_dac_compare[7:7] = 0x0
        self.wr(0x84, 0x4C)

        # pll1_ro1_adc_outofrange[0:0] = 0x0
        # pll1_ro1_adc_moving_quick[1:1] = 0x1
        # pll1_ro1_lookslikelos_vcxo[2:2] = 0x0
        # pll1_ro1_los_active_ref[3:3] = 0x1
        self.wr(0x85, 0xA)

        # pll1_ro5_eng_fullstate[4:3] = 0x0
        self.wr(0x86, 0x0)

        # pll2_ro8_tunestatus[7:0] = 0xE
        self.wr(0x8C, 0xE)

        # pll2_ro8_vtune_error_lsb[7:0] = 0x2
        self.wr(0x8D, 0x2)

        # pll2_ro8_vtune_error_msb[5:0] = 0x0
        # pll2_ro8_vtune_error_sign[6:6] = 0x0
        # pll2_ro8_vtune_status[7:7] = 0x0
        self.wr(0x8E, 0x0)

        # pll2_ro4_syncfsm_state[3:0] = 0x0
        # pll2_ro4_atunefsm_state[7:4] = 0x0
        self.wr(0x8F, 0x0)

        # sysr_ro4_fsmstate[3:0] = 0x2
        # grpx_ro1_outdivfsm_busy[4:4] = 0x0
        self.wr(0x91, 0x2)

        # reg_96[7:0] = 0x0
        self.wr(0x96, 0x0)

        # reg_97[7:0] = 0x0
        self.wr(0x97, 0x0)

        # reg_98[7:0] = 0x0
        self.wr(0x98, 0x0)

        # reg_99[7:0] = 0x0
        self.wr(0x99, 0x0)

        # reg_9A[7:0] = 0x0
        self.wr(0x9A, 0x0)

        # reg_9B[7:0] = 0xAA
        self.wr(0x9B, 0xAA)

        # reg_9C[7:0] = 0xAA
        self.wr(0x9C, 0xAA)

        # reg_9D[7:0] = 0xAA
        self.wr(0x9D, 0xAA)

        # reg_9E[7:0] = 0xAA
        self.wr(0x9E, 0xAA)

        # reg_9F[7:0] = 0x4D
        self.wr(0x9F, 0x4D)

        # reg_A0[7:0] = 0xDF
        self.wr(0xA0, 0xDF)

        # reg_A1[7:0] = 0x97
        self.wr(0xA1, 0x97)

        # reg_A2[7:0] = 0x3
        self.wr(0xA2, 0x3)

        # reg_A3[7:0] = 0x0
        self.wr(0xA3, 0x0)

        # reg_A4[7:0] = 0x0
        self.wr(0xA4, 0x0)

        # reg_A5[7:0] = 0x6
        self.wr(0xA5, 0x6)

        # reg_A6[7:0] = 0x1C
        self.wr(0xA6, 0x1C)

        # reg_A7[7:0] = 0x0
        self.wr(0xA7, 0x0)

        # reg_A8[7:0] = 0x6
        self.wr(0xA8, 0x6)

        # reg_A9[7:0] = 0x0
        self.wr(0xA9, 0x0)

        # reg_AB[7:0] = 0x0
        self.wr(0xAB, 0x0)

        # reg_AC[7:0] = 0x20
        self.wr(0xAC, 0x20)

        # reg_AD[7:0] = 0x0
        self.wr(0xAD, 0x0)

        # reg_AE[7:0] = 0x8
        self.wr(0xAE, 0x8)

        # reg_AF[7:0] = 0x50
        self.wr(0xAF, 0x50)

        # reg_B0[7:0] = 0x4
        self.wr(0xB0, 0x4)

        # reg_B1[7:0] = 0xD
        self.wr(0xB1, 0xD)

        # reg_B2[7:0] = 0x0
        self.wr(0xB2, 0x0)

        # reg_B3[7:0] = 0x0
        self.wr(0xB3, 0x0)

        # reg_B5[7:0] = 0x0
        self.wr(0xB5, 0x0)

        # reg_B6[7:0] = 0x0
        self.wr(0xB6, 0x0)

        # reg_B7[7:0] = 0x0
        self.wr(0xB7, 0x0)

        # reg_B8[7:0] = 0x0
        self.wr(0xB8, 0x0)

        # Disable all channels
        for chId in range(14):
            reg0 = 0xC8 + 10 * chId
            self.wr(reg0, 0x00)
            self.wr(reg0 + 8, 0x00)

        self.wr(0x001, 0x62)  # restart FSMs
        self.wr(0x001, 0x60)


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
