# glbl_cfg1_swrst[0:0] = 0x0
dut.write(0x0, 0x0)

# glbl_cfg1_sleep[0:0] = 0x0
# glbl_cfg1_restart[1:1] = 0x0
# sysr_cfg1_pulsor_req[2:2] = 0x0
# grpx_cfg1_mute[3:3] = 0x0
# pll1_cfg1_forceholdover[4:4] = 0x0
# glbl_cfg1_perf_pllvco[5:5] = 0x1
# dist_cfg1_perf_floor[6:6] = 0x1
# sysr_cfg1_reseed_req[7:7] = 0x0
dut.write(0x1, 0x60)

# sysr_cfg1_rev[0:0] = 0x0
# sysr_cfg1_slipN_req[1:1] = 0x0
# pll2_cfg1_autotune_trig[2:2] = 0x1
dut.write(0x2, 0x4)

# glbl_cfg1_ena_pll1[0:0] = 0x1
# glbl_cfg1_ena_pll2[1:1] = 0x1
# glbl_cfg1_ena_sysr[2:2] = 0x1
# glbl_cfg2_ena_vcos[4:3] = 0x1
# glbl_cfg1_ena_sysri[5:5] = 0x1
dut.write(0x3, 0x2F)

# glbl_cfg7_ena_clkgr[6:0] = 0x42
dut.write(0x4, 0x42)

# glbl_cfg4_ena_rpath[3:0] = 0x1
# dist_cfg1_refbuf0_as_rfsync[4:4] = 0x0
# dist_cfg1_refbuf1_as_extvco[5:5] = 0x0
# pll2_cfg2_syncpin_modesel[7:6] = 0x1
dut.write(0x5, 0x41)

# glbl_cfg1_clear_alarms[0:0] = 0x1
dut.write(0x6, 0x1)

# glbl_reserved[0:0] = 0x0
dut.write(0x7, 0x0)

# glbl_cfg1_dis_pll2_syncatlock[0:0] = 0x1
dut.write(0x9, 0x1)

# glbl_cfg5_ibuf0_en[0:0] = 0x1
# glbl_cfg5_ibuf0_mode[4:1] = 0x3
dut.write(0xA, 0x7)

# glbl_cfg5_ibuf1_en[0:0] = 0x1
# glbl_cfg5_ibuf1_mode[4:1] = 0x3
dut.write(0xB, 0x7)

# glbl_cfg5_ibuf2_en[0:0] = 0x1
# glbl_cfg5_ibuf2_mode[4:1] = 0x3
dut.write(0xC, 0x7)

# glbl_cfg5_ibuf3_en[0:0] = 0x1
# glbl_cfg5_ibuf3_mode[4:1] = 0x3
dut.write(0xD, 0x7)

# glbl_cfg5_ibufv_en[0:0] = 0x1
# glbl_cfg5_ibufv_mode[4:1] = 0x3
dut.write(0xE, 0x7)

# pll1_cfg2_rprior1[1:0] = 0x0
# pll1_cfg2_rprior2[3:2] = 0x1
# pll1_cfg2_rprior3[5:4] = 0x2
# pll1_cfg2_rprior4[7:6] = 0x3
dut.write(0x14, 0xE4)

# pll1_cfg3_los_valtime_sel[2:0] = 0x3
dut.write(0x15, 0x3)

# pll1_cfg2_holdover_exitcrit[1:0] = 0x0
# pll1_cfg2_holdover_exitactn[3:2] = 0x1
dut.write(0x16, 0x4)

# pll1_cfg7_hodac_offsetval[6:0] = 0x0
dut.write(0x17, 0x0)

# pll1_cfg2_hoadc_bw_reduction[1:0] = 0x0
# pll1_cfg1_hodac_force_quickmode[2:2] = 0x1
# pll1_cfg1_hodac_dis_avg_track[3:3] = 0x0
dut.write(0x18, 0x4)

# pll1_cfg1_los_uses_vcxodiv[0:0] = 0x0
# pll1_cfg1_los_bypass_lcmdiv[1:1] = 0x0
dut.write(0x19, 0x0)

# pll1_cfg4_cpi[3:0] = 0x6
dut.write(0x1A, 0x6)

# pll1_cfg1_pfd_invert[0:0] = 0x0
# pll1_cfg1_cppulldn[1:1] = 0x0
# pll1_cfg1_cppullup[2:2] = 0x0
# pll1_cfg1_cpendn[3:3] = 0x1
# pll1_cfg1_cpenup[4:4] = 0x1
dut.write(0x1B, 0x18)

# pll1_cfg8_los_div_setpt_r0[7:0] = 0x4
dut.write(0x1C, 0x4)

# pll1_cfg8_los_div_setpt_r1[7:0] = 0x4
dut.write(0x1D, 0x4)

# pll1_cfg8_los_div_setpt_r2[7:0] = 0x4
dut.write(0x1E, 0x4)

# pll1_cfg8_los_div_setpt_r3[7:0] = 0x4
dut.write(0x1F, 0x4)

# pll1_cfg8_los_div_setpt_vcxo[7:0] = 0x4
dut.write(0x20, 0x4)

# pll1_cfg16_refdivrat_lsb[7:0] = 0x4
dut.write(0x21, 0x4)

# pll1_cfg16_refdivrat_msb[7:0] = 0x0
dut.write(0x22, 0x0)

# pll1_cfg16_fbdivrat_lsb[7:0] = 0x10
dut.write(0x26, 0x10)

# pll1_cfg16_fbdivrat_msb[7:0] = 0x0
dut.write(0x27, 0x0)

# pll1_cfg5_lkdtimersetpt[4:0] = 0xF
# pll1_cfg1_use_slip_for_lkdrst[5:5] = 0x0
dut.write(0x28, 0xF)

# pll1_cfg1_automode[0:0] = 0x0
# pll1_cfg1_autorevertive[1:1] = 0x0
# pll1_cfg1_holdover_uses_dac[2:2] = 0x1
# pll1_cfg2_manclksel[4:3] = 0x0
# pll1_cfg1_byp_debouncer[5:5] = 0x0
dut.write(0x29, 0x4)

# pll1_hoff_timer_setpoint[7:0] = 0x0
dut.write(0x2A, 0x0)

# pll2_reserved[7:0] = 0x1
dut.write(0x31, 0x1)

# pll2_cfg1_rpath_x2_bypass[0:0] = 0x0
dut.write(0x32, 0x0)

# pll2_rdiv_cfg12_divratio_lsb[7:0] = 0x1
dut.write(0x33, 0x1)

# pll2_rdiv_cfg12_divratio_msb[3:0] = 0x0
dut.write(0x34, 0x0)

# pll2_vdiv_cfg16_divratio_lsb[7:0] = 0xC
dut.write(0x35, 0xC)

# pll2_vdiv_cfg16_divratio_msb[7:0] = 0x0
dut.write(0x36, 0x0)

# pll2_cfg4_cp_gain[3:0] = 0xF
dut.write(0x37, 0xF)

# pll2_pfd_cfg1_invert[0:0] = 0x0
# pll2_pfd_cfg1_force_dn[1:1] = 0x0
# pll2_pfd_cfg1_force_up[2:2] = 0x0
# pll2_pfd_cfg1_dn_en[3:3] = 0x1
# pll2_pfd_cfg1_up_en[4:4] = 0x1
dut.write(0x38, 0x18)

# pll2_cfg1_oscout_path_en[0:0] = 0x0
# pll2_cfg2_oscout_divratio[2:1] = 0x0
dut.write(0x39, 0x0)

# pll2_cfg1_obuf0_drvr_en[0:0] = 0x0
# pll2_cfg5_obuf0_drvr_res[2:1] = 0x0
# pll2_cfg5_obuf0_drvr_mode[5:4] = 0x0
dut.write(0x3A, 0x0)

# pll2_cfg1_obuf1_drvr_en[0:0] = 0x0
# pll2_cfg5_obuf1_drvr_res[2:1] = 0x0
# pll2_cfg5_obuf1_drvr_mode[5:4] = 0x0
dut.write(0x3B, 0x0)

# glbl_cfg5_gpi1_en[0:0] = 0x0
# glbl_cfg5_gpi1_sel[4:1] = 0x0
dut.write(0x46, 0x0)

# glbl_cfg5_gpi2_en[0:0] = 0x0
# glbl_cfg5_gpi2_sel[4:1] = 0x0
dut.write(0x47, 0x0)

# glbl_cfg5_gpi3_en[0:0] = 0x0
# glbl_cfg5_gpi3_sel[4:1] = 0x4
dut.write(0x48, 0x8)

# glbl_cfg5_gpi4_en[0:0] = 0x0
# glbl_cfg5_gpi4_sel[4:1] = 0x8
dut.write(0x49, 0x10)

# glbl_cfg8_gpo1_en[0:0] = 0x0
# glbl_cfg8_gpo1_mode[1:1] = 0x1
# glbl_cfg8_gpo1_sel[7:2] = 0x7
dut.write(0x50, 0x1E)

# glbl_cfg8_gpo2_en[0:0] = 0x0
# glbl_cfg8_gpo2_mode[1:1] = 0x1
# glbl_cfg8_gpo2_sel[7:2] = 0xA
dut.write(0x51, 0x2A)

# glbl_cfg8_gpo3_en[0:0] = 0x0
# glbl_cfg8_gpo3_mode[1:1] = 0x0
# glbl_cfg8_gpo3_sel[7:2] = 0x0
dut.write(0x52, 0x0)

# glbl_cfg8_gpo4_en[0:0] = 0x0
# glbl_cfg8_gpo4_mode[1:1] = 0x0
# glbl_cfg8_gpo4_sel[7:2] = 0x0
dut.write(0x53, 0x0)

# glbl_cfg2_sdio_en[0:0] = 0x0
# glbl_cfg2_sdio_mode[1:1] = 0x1
dut.write(0x54, 0x2)

# sysr_cfg3_pulsor_mode[2:0] = 0x1
dut.write(0x5A, 0x1)

# sysr_cfg1_synci_invpol[0:0] = 0x0
# sysr_cfg1_pll2_carryup_sel[1:1] = 0x1
# sysr_cfg1_ext_sync_retimemode[2:2] = 0x1
dut.write(0x5B, 0x6)

# sysr_cfg16_divrat_lsb[7:0] = 0x0
dut.write(0x5C, 0x0)

# sysr_cfg16_divrat_msb[3:0] = 0x6
dut.write(0x5D, 0x6)

# dist_cfg1_extvco_islowfreq_sel[0:0] = 0x0
# dist_cfg1_extvco_div2_sel[1:1] = 0x0
dut.write(0x64, 0x0)

# clkgrpx_cfg1_alg_dly_lowpwr_sel[0:0] = 0x0
dut.write(0x65, 0x0)

# alrm_cfg4_pll1_los4_allow[3:0] = 0x0
# alrm_cfg1_pll1_hold_allow[4:4] = 0x0
# alrm_cfg1_pll1_lock_allow[5:5] = 0x0
# alrm_cfg1_pll1_acq_allow[6:6] = 0x0
# alrm_cfg1_pll1_nearlock_allow[7:7] = 0x0
dut.write(0x70, 0x0)

# alrm_cfg1_pll2_lock_allow[0:0] = 0x0
# alrm_cfg1_sysr_unsyncd_allow[1:1] = 0x0
# alrm_cfg1_clkgrpx_validph_allow[2:2] = 0x0
# alrm_cfg1_plls_both_locked_allow[3:3] = 0x0
# alrm_cfg1_sync_req_allow[4:4] = 0x1
dut.write(0x71, 0x10)

# glbl_ro8_chipid_lob[7:0] = 0x51
dut.write(0x78, 0x51)

# glbl_ro8_chipid_mid[7:0] = 0x16
dut.write(0x79, 0x16)

# glbl_ro8_chipid_hib[7:0] = 0x30
dut.write(0x7A, 0x30)

# alrm_ro1_alarm_masked_viaspi[0:0] = 0x1
dut.write(0x7B, 0x1)

# alrm_ro4_pll1_los4_now[3:0] = 0xF
# alrm_ro1_pll1_hold_now[4:4] = 0x1
# alrm_ro1_pll1_lock_now[5:5] = 0x0
# alrm_ro1_pll1_acq_now[6:6] = 0x0
# alrm_ro1_pll1_nearlock_now[7:7] = 0x0
dut.write(0x7C, 0x1F)

# alrm_ro1_pll2_lock_now[0:0] = 0x1
# alrm_ro1_sysr_unsyncd_now[1:1] = 0x1
# alrm_ro1_clkgrpx_validph_now[2:2] = 0x0
# alrm_ro1_plls_both_locked_now[3:3] = 0x0
# alrm_ro1_sync_req_now[4:4] = 0x1
dut.write(0x7D, 0x13)

# alrm_ro4_pll1_los4_latch[3:0] = 0xF
# alrm_ro1_pll1_hold_latch[4:4] = 0x1
# alrm_ro1_pll1_acq_latch[5:5] = 0x1
# alrm_ro1_pll2_acq_latch[6:6] = 0x1
dut.write(0x7E, 0x7F)

# pll1_ro3_fsm_state[2:0] = 0x4
# pll1_ro2_selected_clkidx[4:3] = 0x0
# pll1_ro2_bestclk[6:5] = 0x0
dut.write(0x82, 0x4)

# pll1_ro7_dac_avg[6:0] = 0x4C
dut.write(0x83, 0x4C)

# pll1_ro7_dac_current[6:0] = 0x4C
# pll1_ro1_dac_compare[7:7] = 0x0
dut.write(0x84, 0x4C)

# pll1_ro1_adc_outofrange[0:0] = 0x0
# pll1_ro1_adc_moving_quick[1:1] = 0x1
# pll1_ro1_lookslikelos_vcxo[2:2] = 0x0
# pll1_ro1_los_active_ref[3:3] = 0x1
dut.write(0x85, 0xA)

# pll1_ro5_eng_fullstate[4:3] = 0x0
dut.write(0x86, 0x0)

# pll2_ro8_tunestatus[7:0] = 0xE
dut.write(0x8C, 0xE)

# pll2_ro8_vtune_error_lsb[7:0] = 0x2
dut.write(0x8D, 0x2)

# pll2_ro8_vtune_error_msb[5:0] = 0x0
# pll2_ro8_vtune_error_sign[6:6] = 0x0
# pll2_ro8_vtune_status[7:7] = 0x0
dut.write(0x8E, 0x0)

# pll2_ro4_syncfsm_state[3:0] = 0x0
# pll2_ro4_atunefsm_state[7:4] = 0x0
dut.write(0x8F, 0x0)

# sysr_ro4_fsmstate[3:0] = 0x2
# grpx_ro1_outdivfsm_busy[4:4] = 0x0
dut.write(0x91, 0x2)

# reg_96[7:0] = 0x0
dut.write(0x96, 0x0)

# reg_97[7:0] = 0x0
dut.write(0x97, 0x0)

# reg_98[7:0] = 0x0
dut.write(0x98, 0x0)

# reg_99[7:0] = 0x0
dut.write(0x99, 0x0)

# reg_9A[7:0] = 0x0
dut.write(0x9A, 0x0)

# reg_9B[7:0] = 0xAA
dut.write(0x9B, 0xAA)

# reg_9C[7:0] = 0xAA
dut.write(0x9C, 0xAA)

# reg_9D[7:0] = 0xAA
dut.write(0x9D, 0xAA)

# reg_9E[7:0] = 0xAA
dut.write(0x9E, 0xAA)

# reg_9F[7:0] = 0x4D
dut.write(0x9F, 0x4D)

# reg_A0[7:0] = 0xDF
dut.write(0xA0, 0xDF)

# reg_A1[7:0] = 0x97
dut.write(0xA1, 0x97)

# reg_A2[7:0] = 0x3
dut.write(0xA2, 0x3)

# reg_A3[7:0] = 0x0
dut.write(0xA3, 0x0)

# reg_A4[7:0] = 0x0
dut.write(0xA4, 0x0)

# reg_A5[7:0] = 0x6
dut.write(0xA5, 0x6)

# reg_A6[7:0] = 0x1C
dut.write(0xA6, 0x1C)

# reg_A7[7:0] = 0x0
dut.write(0xA7, 0x0)

# reg_A8[7:0] = 0x6
dut.write(0xA8, 0x6)

# reg_A9[7:0] = 0x0
dut.write(0xA9, 0x0)

# reg_AB[7:0] = 0x0
dut.write(0xAB, 0x0)

# reg_AC[7:0] = 0x20
dut.write(0xAC, 0x20)

# reg_AD[7:0] = 0x0
dut.write(0xAD, 0x0)

# reg_AE[7:0] = 0x8
dut.write(0xAE, 0x8)

# reg_AF[7:0] = 0x50
dut.write(0xAF, 0x50)

# reg_B0[7:0] = 0x4
dut.write(0xB0, 0x4)

# reg_B1[7:0] = 0xD
dut.write(0xB1, 0xD)

# reg_B2[7:0] = 0x0
dut.write(0xB2, 0x0)

# reg_B3[7:0] = 0x0
dut.write(0xB3, 0x0)

# reg_B5[7:0] = 0x0
dut.write(0xB5, 0x0)

# reg_B6[7:0] = 0x0
dut.write(0xB6, 0x0)

# reg_B7[7:0] = 0x0
dut.write(0xB7, 0x0)

# reg_B8[7:0] = 0x0
dut.write(0xB8, 0x0)

# clkgrp1_div1_cfg1_en[0:0] = 0x0
# clkgrp1_div1_cfg1_phdelta_mslip[1:1] = 0x1
# clkgrp1_div1_cfg2_startmode[3:2] = 0x0
# clkgrp1_div1_cfg1_rev[4:4] = 0x1
# clkgrp1_div1_cfg1_slipmask[5:5] = 0x1
# clkgrp1_div1_cfg1_reseedmask[6:6] = 0x1
# clkgrp1_div1_cfg1_hi_perf[7:7] = 0x0
dut.write(0xC8, 0x72)

# clkgrp1_div1_cfg12_divrat_lsb[7:0] = 0x3
dut.write(0xC9, 0x3)

# clkgrp1_div1_cfg12_divrat_msb[3:0] = 0x0
dut.write(0xCA, 0x0)

# clkgrp1_div1_cfg5_fine_delay[4:0] = 0x0
dut.write(0xCB, 0x0)

# clkgrp1_div1_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0xCC, 0x0)

# clkgrp1_div1_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0xCD, 0x0)

# clkgrp1_div1_cfg12_mslip_msb[3:0] = 0x0
dut.write(0xCE, 0x0)

# clkgrp1_div1_cfg2_sel_outmux[1:0] = 0x0
# clkgrp1_div1_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0xCF, 0x0)

# clkgrp1_div1_cfg5_drvr_res[1:0] = 0x0
# clkgrp1_div1_cfg5_drvr_spare[2:2] = 0x0
# clkgrp1_div1_cfg5_drvr_mode[4:3] = 0x1
# clkgrp1_div1_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp1_div1_cfg2_mutesel[7:6] = 0x0
dut.write(0xD0, 0x8)

# clkgrp1_div2_cfg1_en[0:0] = 0x0
# clkgrp1_div2_cfg1_phdelta_mslip[1:1] = 0x0
# clkgrp1_div2_cfg2_startmode[3:2] = 0x0
# clkgrp1_div2_cfg1_rev[4:4] = 0x1
# clkgrp1_div2_cfg1_slipmask[5:5] = 0x1
# clkgrp1_div2_cfg1_reseedmask[6:6] = 0x1
# clkgrp1_div2_cfg1_hi_perf[7:7] = 0x0
dut.write(0xD2, 0x70)

# clkgrp1_div2_cfg12_divrat_lsb[7:0] = 0x3
dut.write(0xD3, 0x3)

# clkgrp1_div2_cfg12_divrat_msb[3:0] = 0x0
dut.write(0xD4, 0x0)

# clkgrp1_div2_cfg5_fine_delay[4:0] = 0x0
dut.write(0xD5, 0x0)

# clkgrp1_div2_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0xD6, 0x0)

# clkgrp1_div2_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0xD7, 0x0)

# clkgrp1_div2_cfg12_mslip_msb[3:0] = 0x0
dut.write(0xD8, 0x0)

# clkgrp1_div2_cfg2_sel_outmux[1:0] = 0x0
# clkgrp1_div2_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0xD9, 0x0)

# clkgrp1_div2_cfg5_drvr_res[1:0] = 0x1
# clkgrp1_div2_cfg5_drvr_spare[2:2] = 0x0
# clkgrp1_div2_cfg5_drvr_mode[4:3] = 0x0
# clkgrp1_div2_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp1_div2_cfg2_mutesel[7:6] = 0x0
dut.write(0xDA, 0x1)

# clkgrp2_div1_cfg1_en[0:0] = 0x1
# clkgrp2_div1_cfg1_phdelta_mslip[1:1] = 0x1
# clkgrp2_div1_cfg2_startmode[3:2] = 0x0
# clkgrp2_div1_cfg1_rev[4:4] = 0x1
# clkgrp2_div1_cfg1_slipmask[5:5] = 0x1
# clkgrp2_div1_cfg1_reseedmask[6:6] = 0x1
# clkgrp2_div1_cfg1_hi_perf[7:7] = 0x1
dut.write(0xDC, 0xF3)

# clkgrp2_div1_cfg12_divrat_lsb[7:0] = 0x2
dut.write(0xDD, 0x2)

# clkgrp2_div1_cfg12_divrat_msb[3:0] = 0x0
dut.write(0xDE, 0x0)

# clkgrp2_div1_cfg5_fine_delay[4:0] = 0x0
dut.write(0xDF, 0x0)

# clkgrp2_div1_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0xE0, 0x0)

# clkgrp2_div1_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0xE1, 0x0)

# clkgrp2_div1_cfg12_mslip_msb[3:0] = 0x0
dut.write(0xE2, 0x0)

# clkgrp2_div1_cfg2_sel_outmux[1:0] = 0x0
# clkgrp2_div1_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0xE3, 0x0)

# clkgrp2_div1_cfg5_drvr_res[1:0] = 0x0
# clkgrp2_div1_cfg5_drvr_spare[2:2] = 0x0
# clkgrp2_div1_cfg5_drvr_mode[4:3] = 0x1
# clkgrp2_div1_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp2_div1_cfg2_mutesel[7:6] = 0x0
dut.write(0xE4, 0x8)

# clkgrp2_div2_cfg1_en[0:0] = 0x0
# clkgrp2_div2_cfg1_phdelta_mslip[1:1] = 0x0
# clkgrp2_div2_cfg2_startmode[3:2] = 0x0
# clkgrp2_div2_cfg1_rev[4:4] = 0x1
# clkgrp2_div2_cfg1_slipmask[5:5] = 0x1
# clkgrp2_div2_cfg1_reseedmask[6:6] = 0x1
# clkgrp2_div2_cfg1_hi_perf[7:7] = 0x0
dut.write(0xE6, 0x70)

# clkgrp2_div2_cfg12_divrat_lsb[7:0] = 0x3
dut.write(0xE7, 0x3)

# clkgrp2_div2_cfg12_divrat_msb[3:0] = 0x0
dut.write(0xE8, 0x0)

# clkgrp2_div2_cfg5_fine_delay[4:0] = 0x0
dut.write(0xE9, 0x0)

# clkgrp2_div2_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0xEA, 0x0)

# clkgrp2_div2_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0xEB, 0x0)

# clkgrp2_div2_cfg12_mslip_msb[3:0] = 0x0
dut.write(0xEC, 0x0)

# clkgrp2_div2_cfg2_sel_outmux[1:0] = 0x0
# clkgrp2_div2_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0xED, 0x0)

# clkgrp2_div2_cfg5_drvr_res[1:0] = 0x1
# clkgrp2_div2_cfg5_drvr_spare[2:2] = 0x0
# clkgrp2_div2_cfg5_drvr_mode[4:3] = 0x0
# clkgrp2_div2_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp2_div2_cfg2_mutesel[7:6] = 0x0
dut.write(0xEE, 0x1)

# clkgrp3_div1_cfg1_en[0:0] = 0x0
# clkgrp3_div1_cfg1_phdelta_mslip[1:1] = 0x1
# clkgrp3_div1_cfg2_startmode[3:2] = 0x0
# clkgrp3_div1_cfg1_rev[4:4] = 0x1
# clkgrp3_div1_cfg1_slipmask[5:5] = 0x1
# clkgrp3_div1_cfg1_reseedmask[6:6] = 0x1
# clkgrp3_div1_cfg1_hi_perf[7:7] = 0x0
dut.write(0xF0, 0x72)

# clkgrp3_div1_cfg12_divrat_lsb[7:0] = 0x2
dut.write(0xF1, 0x2)

# clkgrp3_div1_cfg12_divrat_msb[3:0] = 0x0
dut.write(0xF2, 0x0)

# clkgrp3_div1_cfg5_fine_delay[4:0] = 0x0
dut.write(0xF3, 0x0)

# clkgrp3_div1_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0xF4, 0x0)

# clkgrp3_div1_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0xF5, 0x0)

# clkgrp3_div1_cfg12_mslip_msb[3:0] = 0x0
dut.write(0xF6, 0x0)

# clkgrp3_div1_cfg2_sel_outmux[1:0] = 0x0
# clkgrp3_div1_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0xF7, 0x0)

# clkgrp3_div1_cfg5_drvr_res[1:0] = 0x0
# clkgrp3_div1_cfg5_drvr_spare[2:2] = 0x0
# clkgrp3_div1_cfg5_drvr_mode[4:3] = 0x1
# clkgrp3_div1_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp3_div1_cfg2_mutesel[7:6] = 0x0
dut.write(0xF8, 0x8)

# clkgrp3_div2_cfg1_en[0:0] = 0x0
# clkgrp3_div2_cfg1_phdelta_mslip[1:1] = 0x0
# clkgrp3_div2_cfg2_startmode[3:2] = 0x0
# clkgrp3_div2_cfg1_rev[4:4] = 0x1
# clkgrp3_div2_cfg1_slipmask[5:5] = 0x1
# clkgrp3_div2_cfg1_reseedmask[6:6] = 0x1
# clkgrp3_div2_cfg1_hi_perf[7:7] = 0x0
dut.write(0xFA, 0x70)

# clkgrp3_div2_cfg12_divrat_lsb[7:0] = 0x0
dut.write(0xFB, 0x0)

# clkgrp3_div2_cfg12_divrat_msb[3:0] = 0x1
dut.write(0xFC, 0x1)

# clkgrp3_div2_cfg5_fine_delay[4:0] = 0x0
dut.write(0xFD, 0x0)

# clkgrp3_div2_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0xFE, 0x0)

# clkgrp3_div2_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0xFF, 0x0)

# clkgrp3_div2_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x100, 0x0)

# clkgrp3_div2_cfg2_sel_outmux[1:0] = 0x0
# clkgrp3_div2_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x101, 0x0)

# clkgrp3_div2_cfg5_drvr_res[1:0] = 0x3
# clkgrp3_div2_cfg5_drvr_spare[2:2] = 0x0
# clkgrp3_div2_cfg5_drvr_mode[4:3] = 0x0
# clkgrp3_div2_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp3_div2_cfg2_mutesel[7:6] = 0x0
dut.write(0x102, 0x3)

# clkgrp4_div1_cfg1_en[0:0] = 0x0
# clkgrp4_div1_cfg1_phdelta_mslip[1:1] = 0x1
# clkgrp4_div1_cfg2_startmode[3:2] = 0x0
# clkgrp4_div1_cfg1_rev[4:4] = 0x1
# clkgrp4_div1_cfg1_slipmask[5:5] = 0x1
# clkgrp4_div1_cfg1_reseedmask[6:6] = 0x1
# clkgrp4_div1_cfg1_hi_perf[7:7] = 0x0
dut.write(0x104, 0x72)

# clkgrp4_div1_cfg12_divrat_lsb[7:0] = 0x2
dut.write(0x105, 0x2)

# clkgrp4_div1_cfg12_divrat_msb[3:0] = 0x0
dut.write(0x106, 0x0)

# clkgrp4_div1_cfg5_fine_delay[4:0] = 0x0
dut.write(0x107, 0x0)

# clkgrp4_div1_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0x108, 0x0)

# clkgrp4_div1_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0x109, 0x0)

# clkgrp4_div1_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x10A, 0x0)

# clkgrp4_div1_cfg2_sel_outmux[1:0] = 0x0
# clkgrp4_div1_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x10B, 0x0)

# clkgrp4_div1_cfg5_drvr_res[1:0] = 0x0
# clkgrp4_div1_cfg5_drvr_spare[2:2] = 0x0
# clkgrp4_div1_cfg5_drvr_mode[4:3] = 0x1
# clkgrp4_div1_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp4_div1_cfg2_mutesel[7:6] = 0x0
dut.write(0x10C, 0x8)

# clkgrp4_div2_cfg1_en[0:0] = 0x0
# clkgrp4_div2_cfg1_phdelta_mslip[1:1] = 0x0
# clkgrp4_div2_cfg2_startmode[3:2] = 0x0
# clkgrp4_div2_cfg1_rev[4:4] = 0x1
# clkgrp4_div2_cfg1_slipmask[5:5] = 0x1
# clkgrp4_div2_cfg1_reseedmask[6:6] = 0x1
# clkgrp4_div2_cfg1_hi_perf[7:7] = 0x0
dut.write(0x10E, 0x70)

# clkgrp4_div2_cfg12_divrat_lsb[7:0] = 0x0
dut.write(0x10F, 0x0)

# clkgrp4_div2_cfg12_divrat_msb[3:0] = 0x1
dut.write(0x110, 0x1)

# clkgrp4_div2_cfg5_fine_delay[4:0] = 0x0
dut.write(0x111, 0x0)

# clkgrp4_div2_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0x112, 0x0)

# clkgrp4_div2_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0x113, 0x0)

# clkgrp4_div2_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x114, 0x0)

# clkgrp4_div2_cfg2_sel_outmux[1:0] = 0x0
# clkgrp4_div2_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x115, 0x0)

# clkgrp4_div2_cfg5_drvr_res[1:0] = 0x3
# clkgrp4_div2_cfg5_drvr_spare[2:2] = 0x0
# clkgrp4_div2_cfg5_drvr_mode[4:3] = 0x0
# clkgrp4_div2_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp4_div2_cfg2_mutesel[7:6] = 0x0
dut.write(0x116, 0x3)

# clkgrp5_div1_cfg1_en[0:0] = 0x0
# clkgrp5_div1_cfg1_phdelta_mslip[1:1] = 0x1
# clkgrp5_div1_cfg2_startmode[3:2] = 0x0
# clkgrp5_div1_cfg1_rev[4:4] = 0x1
# clkgrp5_div1_cfg1_slipmask[5:5] = 0x1
# clkgrp5_div1_cfg1_reseedmask[6:6] = 0x1
# clkgrp5_div1_cfg1_hi_perf[7:7] = 0x0
dut.write(0x118, 0x72)

# clkgrp5_div1_cfg12_divrat_lsb[7:0] = 0x2
dut.write(0x119, 0x2)

# clkgrp5_div1_cfg12_divrat_msb[3:0] = 0x0
dut.write(0x11A, 0x0)

# clkgrp5_div1_cfg5_fine_delay[4:0] = 0x0
dut.write(0x11B, 0x0)

# clkgrp5_div1_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0x11C, 0x0)

# clkgrp5_div1_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0x11D, 0x0)

# clkgrp5_div1_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x11E, 0x0)

# clkgrp5_div1_cfg2_sel_outmux[1:0] = 0x0
# clkgrp5_div1_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x11F, 0x0)

# clkgrp5_div1_cfg5_drvr_res[1:0] = 0x0
# clkgrp5_div1_cfg5_drvr_spare[2:2] = 0x0
# clkgrp5_div1_cfg5_drvr_mode[4:3] = 0x1
# clkgrp5_div1_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp5_div1_cfg2_mutesel[7:6] = 0x0
dut.write(0x120, 0x8)

# clkgrp5_div2_cfg1_en[0:0] = 0x0
# clkgrp5_div2_cfg1_phdelta_mslip[1:1] = 0x0
# clkgrp5_div2_cfg2_startmode[3:2] = 0x0
# clkgrp5_div2_cfg1_rev[4:4] = 0x1
# clkgrp5_div2_cfg1_slipmask[5:5] = 0x1
# clkgrp5_div2_cfg1_reseedmask[6:6] = 0x1
# clkgrp5_div2_cfg1_hi_perf[7:7] = 0x0
dut.write(0x122, 0x70)

# clkgrp5_div2_cfg12_divrat_lsb[7:0] = 0x0
dut.write(0x123, 0x0)

# clkgrp5_div2_cfg12_divrat_msb[3:0] = 0x1
dut.write(0x124, 0x1)

# clkgrp5_div2_cfg5_fine_delay[4:0] = 0x0
dut.write(0x125, 0x0)

# clkgrp5_div2_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0x126, 0x0)

# clkgrp5_div2_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0x127, 0x0)

# clkgrp5_div2_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x128, 0x0)

# clkgrp5_div2_cfg2_sel_outmux[1:0] = 0x0
# clkgrp5_div2_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x129, 0x0)

# clkgrp5_div2_cfg5_drvr_res[1:0] = 0x3
# clkgrp5_div2_cfg5_drvr_spare[2:2] = 0x0
# clkgrp5_div2_cfg5_drvr_mode[4:3] = 0x0
# clkgrp5_div2_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp5_div2_cfg2_mutesel[7:6] = 0x0
dut.write(0x12A, 0x3)

# clkgrp6_div1_cfg1_en[0:0] = 0x0
# clkgrp6_div1_cfg1_phdelta_mslip[1:1] = 0x1
# clkgrp6_div1_cfg2_startmode[3:2] = 0x0
# clkgrp6_div1_cfg1_rev[4:4] = 0x1
# clkgrp6_div1_cfg1_slipmask[5:5] = 0x1
# clkgrp6_div1_cfg1_reseedmask[6:6] = 0x1
# clkgrp6_div1_cfg1_hi_perf[7:7] = 0x0
dut.write(0x12C, 0x72)

# clkgrp6_div1_cfg12_divrat_lsb[7:0] = 0x3
dut.write(0x12D, 0x3)

# clkgrp6_div1_cfg12_divrat_msb[3:0] = 0x0
dut.write(0x12E, 0x0)

# clkgrp6_div1_cfg5_fine_delay[4:0] = 0x0
dut.write(0x12F, 0x0)

# clkgrp6_div1_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0x130, 0x0)

# clkgrp6_div1_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0x131, 0x0)

# clkgrp6_div1_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x132, 0x0)

# clkgrp6_div1_cfg2_sel_outmux[1:0] = 0x0
# clkgrp6_div1_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x133, 0x0)

# clkgrp6_div1_cfg5_drvr_res[1:0] = 0x0
# clkgrp6_div1_cfg5_drvr_spare[2:2] = 0x0
# clkgrp6_div1_cfg5_drvr_mode[4:3] = 0x1
# clkgrp6_div1_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp6_div1_cfg2_mutesel[7:6] = 0x0
dut.write(0x134, 0x8)

# clkgrp6_div2_cfg1_en[0:0] = 0x0
# clkgrp6_div2_cfg1_phdelta_mslip[1:1] = 0x0
# clkgrp6_div2_cfg2_startmode[3:2] = 0x0
# clkgrp6_div2_cfg1_rev[4:4] = 0x1
# clkgrp6_div2_cfg1_slipmask[5:5] = 0x1
# clkgrp6_div2_cfg1_reseedmask[6:6] = 0x1
# clkgrp6_div2_cfg1_hi_perf[7:7] = 0x0
dut.write(0x136, 0x70)

# clkgrp6_div2_cfg12_divrat_lsb[7:0] = 0x3
dut.write(0x137, 0x3)

# clkgrp6_div2_cfg12_divrat_msb[3:0] = 0x0
dut.write(0x138, 0x0)

# clkgrp6_div2_cfg5_fine_delay[4:0] = 0x0
dut.write(0x139, 0x0)

# clkgrp6_div2_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0x13A, 0x0)

# clkgrp6_div2_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0x13B, 0x0)

# clkgrp6_div2_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x13C, 0x0)

# clkgrp6_div2_cfg2_sel_outmux[1:0] = 0x0
# clkgrp6_div2_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x13D, 0x0)

# clkgrp6_div2_cfg5_drvr_res[1:0] = 0x1
# clkgrp6_div2_cfg5_drvr_spare[2:2] = 0x0
# clkgrp6_div2_cfg5_drvr_mode[4:3] = 0x0
# clkgrp6_div2_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp6_div2_cfg2_mutesel[7:6] = 0x0
dut.write(0x13E, 0x1)

# clkgrp7_div1_cfg1_en[0:0] = 0x1
# clkgrp7_div1_cfg1_phdelta_mslip[1:1] = 0x1
# clkgrp7_div1_cfg2_startmode[3:2] = 0x0
# clkgrp7_div1_cfg1_rev[4:4] = 0x1
# clkgrp7_div1_cfg1_slipmask[5:5] = 0x1
# clkgrp7_div1_cfg1_reseedmask[6:6] = 0x1
# clkgrp7_div1_cfg1_hi_perf[7:7] = 0x1
dut.write(0x140, 0xF3)

# clkgrp7_div1_cfg12_divrat_lsb[7:0] = 0x8
dut.write(0x141, 0x8)

# clkgrp7_div1_cfg12_divrat_msb[3:0] = 0x0
dut.write(0x142, 0x0)

# clkgrp7_div1_cfg5_fine_delay[4:0] = 0x0
dut.write(0x143, 0x0)

# clkgrp7_div1_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0x144, 0x0)

# clkgrp7_div1_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0x145, 0x0)

# clkgrp7_div1_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x146, 0x0)

# clkgrp7_div1_cfg2_sel_outmux[1:0] = 0x0
# clkgrp7_div1_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x147, 0x0)

# clkgrp7_div1_cfg5_drvr_res[1:0] = 0x0
# clkgrp7_div1_cfg5_drvr_spare[2:2] = 0x0
# clkgrp7_div1_cfg5_drvr_mode[4:3] = 0x1
# clkgrp7_div1_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp7_div1_cfg2_mutesel[7:6] = 0x0
dut.write(0x148, 0x8)

# clkgrp7_div2_cfg1_en[0:0] = 0x1
# clkgrp7_div2_cfg1_phdelta_mslip[1:1] = 0x0
# clkgrp7_div2_cfg2_startmode[3:2] = 0x0
# clkgrp7_div2_cfg1_rev[4:4] = 0x1
# clkgrp7_div2_cfg1_slipmask[5:5] = 0x1
# clkgrp7_div2_cfg1_reseedmask[6:6] = 0x1
# clkgrp7_div2_cfg1_hi_perf[7:7] = 0x1
dut.write(0x14A, 0xF1)

# clkgrp7_div2_cfg12_divrat_lsb[7:0] = 0xF0
dut.write(0x14B, 0xF0)

# clkgrp7_div2_cfg12_divrat_msb[3:0] = 0x0
dut.write(0x14C, 0x0)

# clkgrp7_div2_cfg5_fine_delay[4:0] = 0x0
dut.write(0x14D, 0x0)

# clkgrp7_div2_cfg5_sel_coarse_delay[4:0] = 0x0
dut.write(0x14E, 0x0)

# clkgrp7_div2_cfg12_mslip_lsb[7:0] = 0x0
dut.write(0x14F, 0x0)

# clkgrp7_div2_cfg12_mslip_msb[3:0] = 0x0
dut.write(0x150, 0x0)

# clkgrp7_div2_cfg2_sel_outmux[1:0] = 0x0
# clkgrp7_div2_cfg1_drvr_sel_testclk[2:2] = 0x0
dut.write(0x151, 0x0)

# clkgrp7_div2_cfg5_drvr_res[1:0] = 0x3
# clkgrp7_div2_cfg5_drvr_spare[2:2] = 0x0
# clkgrp7_div2_cfg5_drvr_mode[4:3] = 0x0
# clkgrp7_div2_cfg_outbuf_dyn[5:5] = 0x0
# clkgrp7_div2_cfg2_mutesel[7:6] = 0x0
dut.write(0x152, 0x3)

