#!/usr/bin/env python3
import sys
import time
import logging
import os

import coloredlogs

from lib.global_device import GlobalDevice
from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.ipbus_link import IPbusLink
from lib.jadepix_device import JadePixDevice
from lib.s_curve import SCurve
from lib.gen_pattern import GenPattern

from data_analysis.data_analysis import DataAnalysis

from lib import jadepix_defs

import numpy as np

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class MainConfig(object):
    def __init__(self):
        self.GLOBAL_RESET = True
        self.JADEPIX_RUN_GS = False
        self.JADEPIX_SCURVE_TEST = False
        self.JADEPIX_RUN_RS = True
        self.JADEPIX_ANA_DATA = False


def main(enable_config=0, dac_initial=0, spi_initial=0, outfilename="data/data_rs.txt"):
    ipbus_link = IPbusLink()
    main_config = MainConfig()

    jadepix_dev = JadePixDevice(ipbus_link)
    global_dev = GlobalDevice(ipbus_link)
    dac70004_dev = Dac70004Device(ipbus_link)
    s_curve = SCurve(dac70004_dev, jadepix_dev)

    test_pattern_generator = GenPattern()

    ''' Soft global reset '''
    if main_config.GLOBAL_RESET:
        global_dev.set_soft_rst()

    ''' DAC70004 Config '''
    if dac_initial:
        dac70004_dev.soft_reset()
        dac70004_dev.soft_clr()
        dac70004_dev.w_power_chn(DAC70004_PW_UP, 0xf)  # Power up all channels
        dac70004_dev.w_ana_chn_update_chn(
            DAC70004_CHN_A, 1.2)  # Set channle A to 1.3V, LOW
        dac70004_dev.w_ana_chn_update_chn(
            DAC70004_CHN_B, 1.7)  # Set channle B to 1.7V, High
        dac70004_dev.w_ana_chn_update_chn(
            DAC70004_CHN_C, 1.4)  # Set channle C to 1.4V, Reset1
        dac70004_dev.w_ana_chn_update_chn(
            DAC70004_CHN_D, 1.4)  # Set channle D to 1.4V, Reset2

    ''' SPI master config '''
    if spi_initial:
        jadepix_dev.reset_spi()
        jadepix_dev.set_spi(data_len=200, ie=False, ass=True,
                            lsb=False, rx_neg=False, tx_neg=True, div=0, ss=0x01)
        # Set JadePix SPI configuration
        jadepix_dev.start_spi_config()
        # Load Config

    ''' JadePix Control '''
    """ Settings for some tests """
    jadepix_dev.set_rx_fpga_oe(1)

    jadepix_dev.set_digsel_en_manually(False)
    jadepix_dev.digsel_en(1)

    jadepix_dev.set_anasel_en_manually(False)
    jadepix_dev.anasel_en(1)

    jadepix_dev.set_dplse_manually(False)
    jadepix_dev.set_dplse_soft(1)

    jadepix_dev.set_aplse_manually(True)
    jadepix_dev.set_aplse_soft(1)

    jadepix_dev.set_matrix_grst_manually(True)
    jadepix_dev.set_matrix_grst_soft(0)

    jadepix_dev.set_gshutter_manually(True)
    jadepix_dev.set_gshutter_soft(1)

    jadepix_dev.set_ca_soft_manually(False)
    jadepix_dev.set_ca_soft(313)

    jadepix_dev.set_ca_en_manually(False)
    jadepix_dev.set_ca_en_soft(0)

    jadepix_dev.set_hit_rst_manually(False)
    jadepix_dev.set_hit_rst_soft(0)

    jadepix_dev.set_gs_plse(is_dplse=False)  # select digital or analog pulse out

    """ Enable clock link """
    jadepix_dev.set_sn_oen(0, go_dispatch=True)
    jadepix_dev.set_en_diff(1, go_dispatch=True)

    """ Set INQUIRY """
    jadepix_dev.set_d_rst(0, go_dispatch=True)
    jadepix_dev.set_d_rst(1, go_dispatch=True)
    jadepix_dev.set_inquiry(1)

    """ Set jadepix chip clock"""
    jadepix_dev.set_chip_clk(1)  # 1: clk_sys 0: clk_fpga

    """ PLL settings """
    jadepix_dev.set_serializer_rst(0)
    jadepix_dev.set_clk_sel(0)  # TODO: add some docs here
    jadepix_dev.set_refclk_1G(0)  # the enable port of PLL reference clock

    """ From here we can test pixel register (PULSE/MASK) configuration """
    CONFIG_SHAPE = [jadepix_defs.ROW, jadepix_defs.COL, 3]
    MASK_DEFAULT = (1, 0, 0)  # no mask
    PLSE_DEFAULT = (0, 1, 0)  # all pulse out

    mask_arr = np.empty(CONFIG_SHAPE, dtype=int)
    mask_arr[:, :] = MASK_DEFAULT

    plse_arr = np.empty(CONFIG_SHAPE, dtype=int)
    plse_arr[:, :] = PLSE_DEFAULT

    # print C
    test_pattern_generator.code_c(config_arr=plse_arr)

    data_per_frame = test_pattern_generator.gen_test_pattern(plse_arr)

    if enable_config:
        """ Set configuration timing factor """
        jadepix_dev.set_cfg_add_factor_t0(t0_factor=83)  # 1-255
        jadepix_dev.set_cfg_add_factor_t1(t1_factor=83)  # 1-65535
        jadepix_dev.set_cfg_add_factor_t2(t2_factor=83)  # 1-255

        log.info("Start configure the PULSE and MASK of each pixel...")
        # Write Mask to FIFO and start config
        if jadepix_dev.is_busy_cfg():
            log.error("Configuration is busy!")
        jadepix_dev.w_cfg(mask_arr)
        jadepix_dev.start_cfg()
        time.sleep(1.2)  # 100K(512 * 192) * 10us = 1s, FIFO -> Chip
        if not jadepix_dev.is_busy_cfg():
            log.info("Configuration mask finished!")
        # Write PULSE to FIFO and start config
        if jadepix_dev.is_busy_cfg():
            log.error("Configuration is busy!")
        jadepix_dev.w_cfg(plse_arr)
        jadepix_dev.start_cfg()
        time.sleep(1.2)  # 100K(512 * 192) * 10us = 1s, FIFO -> Chip
        if not jadepix_dev.is_busy_cfg():
            log.info("Configuration pulse finished!")

    """From here we can test global shutter """
    """sys_clk period = 12 ns, so width = Number * Period"""
    """For pulse width, width = (high<<32 + low) * Period"""
    frame_number = 1
    if main_config.JADEPIX_RUN_GS:
        jadepix_dev.reset_rfifo()
        jadepix_dev.rs_config(cache_bit=0x0, hitmap_col_low=340,
                              hitmap_col_high=351, hitmap_en=True, frame_number=frame_number)
        jadepix_dev.gs_config(pulse_delay=256, width_low=65535, width_high=0, pulse_deassert=256, deassert=5, col=313)
        jadepix_dev.start_gs()

        ''' Get Data Stream '''
        # data_in_total = data_per_frame * frame_number
        data_file = "data/data_gs.txt"
        try:
            os.remove(data_file)
        except OSError:
            pass
        data_mem = jadepix_dev.read_data(safe_mode=True)
        jadepix_dev.write2txt(data_file, data_mem)
        log.info("Global shutter finished!")

    if main_config.JADEPIX_SCURVE_TEST:
        jadepix_dev.rs_config(cache_bit=0x0, hitmap_col_low=340,
                              hitmap_col_high=351, hitmap_en=True, frame_number=1)
        jadepix_dev.gs_config(pulse_delay=256, width_low=65535, width_high=0, pulse_deassert=256, deassert=5, col=313)

        s_curve.run_scurve_pulse_low_test(pulse_hi=1.7, pulse_lo_init=1.4, pulse_lo_target=1.5, lo_step=0.01,
                                          test_num=50)

    if main_config.JADEPIX_RUN_RS:
        frame_number = 100000
        hitmap_col_low = 340
        hitmap_col_high = 351
        hitmap_en = False
        rs_frame_period_no_hitmap = 16 * jadepix_defs.SYS_CLK_PERIOD * jadepix_defs.ROW  # Unit: ns
        rs_hitmap_period = (hitmap_col_high - hitmap_col_low + 1) * 4 * jadepix_defs.SYS_CLK_PERIOD * jadepix_defs.ROW
        rs_frame_period = (rs_hitmap_period + rs_frame_period_no_hitmap) if hitmap_en else rs_frame_period_no_hitmap
        jadepix_dev.rs_config(cache_bit=0x0, hitmap_col_low=hitmap_col_low,
                              hitmap_col_high=hitmap_col_high, hitmap_en=hitmap_en, frame_number=frame_number)
        jadepix_dev.reset_rfifo()
        log.info("Normally we should wait for {:} secends until rolling shutter finished.".format(
            rs_frame_period * frame_number / pow(10, 9)))
        jadepix_dev.start_rs()
        data_mem = jadepix_dev.read_data(safe_mode=True)
        log.info("Rolling shutter finished!")

        data_file = outfilename
        jadepix_dev.write2txt(data_file, data_mem)


if __name__ == '__main__':
    if len(sys.argv) > 5:
        print("Usage: ./run.py [enable config] [dac initial] [spi_initial]")
        log.error("only three parameters is accepted at most!")
        print("Example: ./run.py 1 0 0, enable config, do not set dac, do not set spi")
        sys.exit(0)
    elif len(sys.argv) == 1:
        main(enable_config=0, dac_initial=0, spi_initial=0)
    else:
        main(enable_config=int(sys.argv[1]), dac_initial=int(sys.argv[2]), spi_initial=int(sys.argv[3]), outfilename=sys.argv[4])
