#!/usr/bin/env python3
import sys
import time
import logging
import os
import gc

from pathlib import Path
from functools import partial

import coloredlogs

from lib.global_device import GlobalDevice
from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.ipbus_link import IPbusLink
from lib.jadepix_device import JadePixDevice
from lib.s_curve import SCurve

from data_analysis import data_analysis

from lib import jadepix_defs

import ROOT

import numpy as np
from root_numpy import array2root

from queue import SimpleQueue

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class MainConfig(object):
    def __init__(self):
        self.DEBUG_MODE = False
        self.GLOBAL_RESET = True
        self.DAC70004_INITIAL = True
        self.JADEPIX_SPI_CONF = True
        self.JADEPIX_CONFIG = True
        self.JADEPIX_RUN_GS = True
        self.JADEPIX_SCURVE_TEST = True
        self.JADEPIX_RUN_RS = False
        self.JADEPIX_ANA_DATA = True

        self.W_TXT = True


def set_config(config_arr, row_low, row_high, col_low, col_high, bit_nr, data):
    config_arr[row_low:row_high, col_low:col_high, bit_nr] = data


set_con_selm = partial(set_config, bit_nr=0)
set_con_selp = partial(set_config, bit_nr=1)
set_con_data = partial(set_config, bit_nr=2)


def calc_blk(col):
    return int((col % 48) / 3)


def calc_pix_out(config):
    """ dout = ~CON_MASK & CON_PLSE & CON_DATA """
    return ((not config[0]) & config[1] & config[2])


def calc_data_out(row, blk, pix_data):
    return (row << 7) + (blk << 3) + pix_data


def gen_test_pattern(config_arr):
    line_num = 0
    test_patter_path = "data/test_pattern.txt"
    dout_arr = np.zeros(3, int)
    data_string = []
    try:
        os.remove(test_patter_path)
    except OSError:
        pass
    with open(test_patter_path, "w+") as f:
        for row in range(jadepix_defs.ROW):
            for col in range(jadepix_defs.COL):
                blk = calc_blk(col)
                pix_bit = col % 3
                pix_out = calc_pix_out(config_arr[row, col])

                block = int(col / 48)

                dout_arr[pix_bit] = pix_out
                if pix_bit == 2:
                    pix_data = int((dout_arr[2] << 2) | (dout_arr[1] << 1) | dout_arr[0])
                    dout_arr = np.empty((3, 1), int)
                    if pix_data > 0:
                        log.debug("row: {} col: {} data: {}".format(row, col, pix_data))
                        data_out = calc_data_out(row, blk, pix_data)
                        line_num += 1
                        data_flag = 2
                        data_string.append("{:#010x}\n".format((data_flag << 23) + (block << 16) + data_out))
        f.write("".join(data_string))
    return line_num


def main(enable_config=0):
    ipbus_link = IPbusLink()
    main_config = MainConfig()

    jadepix_dev = JadePixDevice(ipbus_link)
    global_dev = GlobalDevice(ipbus_link)
    dac70004_dev = Dac70004Device(ipbus_link)
    s_curve = SCurve(ipbus_link)

    ''' Soft global reset '''
    if main_config.GLOBAL_RESET:
        global_dev.set_soft_rst()

    ''' DAC70004 Config '''
    if main_config.DAC70004_INITIAL:
        dac70004_dev.soft_reset()
        dac70004_dev.soft_clr()
        dac70004_dev.w_power_chn(DAC70004_PW_UP, 0xf)  # Power up all channels
        dac70004_dev.w_ana_chn_update_chn(
            DAC70004_CHN_A, 1.3)  # Set channle A to 1.3V, LOW
        dac70004_dev.w_ana_chn_update_chn(
            DAC70004_CHN_B, 1.7)  # Set channle B to 1.7V, High
        dac70004_dev.w_ana_chn_update_chn(
            DAC70004_CHN_C, 1.4)  # Set channle C to 1.4V, Reset1
        dac70004_dev.w_ana_chn_update_chn(
            DAC70004_CHN_D, 1.4)  # Set channle D to 1.4V, Reset2

    ''' SPI master config '''
    if main_config.JADEPIX_SPI_CONF:
        jadepix_dev.reset_spi()
        jadepix_dev.set_spi(data_len=200, ie=False, ass=True,
                            lsb=False, rx_neg=False, tx_neg=True, div=0, ss=0x01)
        # Set JadePix SPI configuration
        jadepix_dev.start_spi_config()
        # Load Config

    ''' JadePix Control '''

    """ From here we can test configuration """
    CONFIG_SHAPE = [jadepix_defs.ROW, jadepix_defs.COL, 3]
    MASK_DEFAULT = (1, 0, 0)  # no mask
    PLSE_DEFAULT = (0, 1, 0)  # all pulse out

    mask_arr = np.empty(CONFIG_SHAPE, dtype=int)
    mask_arr[:, :] = MASK_DEFAULT

    plse_arr = np.empty(CONFIG_SHAPE, dtype=int)
    plse_arr[:, :] = PLSE_DEFAULT

    # set_con_data(config_arr=plse_arr, row_low=1, row_high=2, col_low=16, col_high=17, data=1)
    # set_con_data(config_arr=plse_arr, row_low=0, row_high=1, col_low=35, col_high=37, data=1)
    # set_con_data(config_arr=plse_arr, row_low=115, row_high=117, col_low=32, col_high=33, data=1)
    # set_con_data(config_arr=plse_arr, row_low=221, row_high=223, col_low=45, col_high=47, data=1)

    # set_con_data(config_arr=plse_arr, row_low=1, row_high=2, col_low=64, col_high=65, data=1)
    # set_con_data(config_arr=plse_arr, row_low=511, row_high=512, col_low=79, col_high=80, data=1)
    # set_con_data(config_arr=plse_arr, row_low=255, row_high=257, col_low=95, col_high=96, data=1)
    # set_con_data(config_arr=plse_arr, row_low=254, row_high=256, col_low=71, col_high=73, data=1)

    # set_con_data(config_arr=plse_arr, row_low=1, row_high=2, col_low=112, col_high=113, data=1)
    # set_con_data(config_arr=plse_arr, row_low=134, row_high=135, col_low=115, col_high=117, data=1)
    # set_con_data(config_arr=plse_arr, row_low=335, row_high=337, col_low=123, col_high=124, data=1)
    # set_con_data(config_arr=plse_arr, row_low=222, row_high=224, col_low=135, col_high=137, data=1)
    #
    # set_con_data(config_arr=plse_arr, row_low=1, row_high=2, col_low=160, col_high=161, data=1)
    # set_con_data(config_arr=plse_arr, row_low=111, row_high=112, col_low=167, col_high=169, data=1)
    # set_con_data(config_arr=plse_arr, row_low=333, row_high=335, col_low=171, col_high=172, data=1)
    set_con_data(config_arr=plse_arr, row_low=2, row_high=4, col_low=181, col_high=183, data=1)

    data_per_frame = gen_test_pattern(plse_arr)

    if enable_config:
        log.warning("Start configure the PULSE and MASK of each pixel...")
        start = time.process_time()
        # Write Mask to FIFO and start config
        if not jadepix_dev.is_busy_cfg():
            jadepix_dev.w_cfg(mask_arr)
            jadepix_dev.start_cfg(go_dispatch=True)
            print("It takes {:} secends to write configurations to FIFO".format(time.process_time() - start))
        time.sleep(1.2)  # 100K(512 * 192) * 10us = 1s, FIFO -> Chip
        # Write PULSE to FIFO and start config
        start = time.process_time()
        if not jadepix_dev.is_busy_cfg():
            jadepix_dev.w_cfg(plse_arr)
            jadepix_dev.start_cfg(go_dispatch=True)
        print("It takes {:} secends to write configurations to FIFO".format(time.process_time() - start))
        time.sleep(1.2)  # 100K(512 * 192) * 10us = 1s, FIFO -> Chip

    """ Set digital front-end """
    jadepix_dev.is_debug(main_config.DEBUG_MODE)

    ## only work at debug mode ##
    jadepix_dev.set_hit_rst_soft(False)  # Do not reset
    jadepix_dev.set_ca_soft(313)
    jadepix_dev.set_ca_en_soft(True)

    ## software settting has influence with firmware logic ##
    jadepix_dev.set_gshutter_soft(False)  # if true : GSHUTTER force to high
    jadepix_dev.digsel_en(True)  # and logic
    jadepix_dev.anasel_en(True)  # and logic
    jadepix_dev.set_dplse_soft(True)  # if false: DPLSE force to low
    jadepix_dev.set_aplse_soft(True)  # if false: APLSE force to low

    jadepix_dev.set_gs_plse(is_dplse=True)  # select digital or analog pulse out

    """ Enable clock link """
    jadepix_dev.set_sn_oen(0, go_dispatch=True)
    jadepix_dev.set_en_diff(1, go_dispatch=True)

    """ Set INQUIRY """
    jadepix_dev.set_d_rst(0, go_dispatch=True)
    jadepix_dev.set_d_rst(1, go_dispatch=True)
    jadepix_dev.set_inquiry(1)

    """ Set jadepix chip clock"""
    jadepix_dev.set_chip_clk(1)  # 1: clk_sys 0: clk_fpga

    """ Set BLK_SELECT default value """
    jadepix_dev.set_blk_sel_def(blk_sel_def=3)

    """ Set configuration timing dactor """
    jadepix_dev.set_cfg_add_factor_t0(t0_factor=83)  # 1-255
    jadepix_dev.set_cfg_add_factor_t1(t1_factor=83)  # 1-65535
    jadepix_dev.set_cfg_add_factor_t2(t2_factor=83)  # 1-255

    """From here we can test global shutter """
    """sys_clk period = 12 ns, so width = Number * Period"""
    """For pulse width, width = (high<<32 + low) * Period"""
    frame_number = 1
    if main_config.JADEPIX_RUN_GS:
        # TODO: Will change to real time later
        jadepix_dev.reset_rfifo()
        jadepix_dev.rs_config(cache_bit=0x0, hitmap_col_low=340,
                              hitmap_col_high=351, hitmap_en=True, frame_number=frame_number)
        jadepix_dev.gs_config(pulse_delay=256, width_low=65535, width_high=0, pulse_deassert=256, deassert=5, col=313)
        jadepix_dev.start_gs()

        # test_valid_pattern = 12
        # frame_per_slice = 4
        # num_token = 1

        # frame_number = frame_per_slice * num_token
        # num_data = frame_number * jadepix_defs.ROW * jadepix_defs.BLK * test_valid_pattern
        # num_valid_data_stream = num_data + 2 * frame_number - 1

        rfifo_depth_width = 17
        rfifo_depth = pow(2, rfifo_depth_width)

        slice_size = int(rfifo_depth)  # try largest slice as possible
        # num_data_wanted = num_token * slice_size
        # data_size = num_data_wanted * 32  # Unit: bit
        # log.warning("The data will take {} MB memory".format(data_size / 8 / 2 ** 20))

        ''' Get Data Stream '''
        data_que = SimpleQueue()
        start = time.process_time()
        data_in_total = data_per_frame * frame_number
        mem = jadepix_dev.read_ipb_data_fifo(slice_size, safe_mode=True)
        if main_config.W_TXT:
            data_string = []
            data_file = "data/data.txt"
            try:
                os.remove(data_file)
            except OSError:
                pass
            with open(data_file, 'w+') as data_file:
                for data in mem:
                    data_string.append("{:#010x}\n".format(data))
                data_file.write("".join(data_string))
        data_que.put(mem)
        # trans_speed = int(data_size / (time.process_time() - start))  # Unit: bps
        # log.info("Transfer speed: {:f} Mbps".format(trans_speed / pow(10, 6)))

    if main_config.JADEPIX_SCURVE_TEST:
        jadepix_dev.rs_config(cache_bit=0x0, hitmap_col_low=340,
                              hitmap_col_high=351, hitmap_en=True, frame_number=1)
        jadepix_dev.gs_config(pulse_delay=256, width_low=65535, width_high=0, pulse_deassert=256, deassert=5, col=313)

        s_curve.run_scurve_pulse_low_test(pulse_hi=1.7, pulse_lo_init=1.4, pulse_lo_target=1.5, lo_step=0.01,
                                          test_num=50)

    if main_config.JADEPIX_RUN_RS:
        frame_number = 20
        data_in_total = data_per_frame * frame_number
        jadepix_dev.rs_config(cache_bit=0xf, hitmap_col_low=340,
                              hitmap_col_high=341, hitmap_en=False, frame_number=frame_number)
        jadepix_dev.reset_rfifo()
        jadepix_dev.start_rs()

    if main_config.JADEPIX_ANA_DATA:
        log.info("Write data to .root ...")
        data_root_file = "data/data.root"
        hfile = ROOT.gROOT.FindObject(data_root_file)
        if hfile:
            hfile.Close()
        hfile = ROOT.TFile(data_root_file, 'RECREATE', 'Data ROOT file')
        if os.path.exists(data_root_file):
            os.remove(data_root_file)
        start = time.process_time()
        for one_config in range(1):
            data_vector = data_que.get()
            data_arr = np.asarray(data_vector, dtype=[('data', np.uint32)], order='K')
            array2root(data_arr, data_root_file, treename='data', mode='update')
            del data_vector
            gc.collect()

        time_diff = time.process_time() - start
        root_file_size = Path(data_root_file).stat().st_size
        trans_speed = int(root_file_size / time_diff)  # Unit: Bps
        start = time.process_time()
        data_path = "./data"
        log.info("Write file speed: {:f} Mbps".format(8 * trans_speed / pow(10, 6)))
        log.info("Write to .root end.")
        del data_que

        ''' Draw some plots '''
        data_ana = data_analysis.DataAnalysis(data_root_file, 1, is_save_png=True)
        lost_tmp, data_num_got = data_ana.draw_data()
        # data_lost = num_data - data_num_got
        # lost += lost_tmp
        # log.info("Lost data num: {:}".format(data_lost))
        # log.info("Lost frames: {:}".format(lost))


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print("Usage: ./run.py [enable config]")
        log.error("only one parameter is accept at most!")
        print("Example: ./run.py 1, enable config; or ./run.py 0, disable config.")
        sys.exit(0)
    elif len(sys.argv) == 1:
        main(enable_config=0)
    else:
        main(enable_config=int(sys.argv[1]))
