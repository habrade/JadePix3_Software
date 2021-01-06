#!/usr/bin/env python3
import sys
import time
import logging
import os
import gc

from pathlib import Path

import coloredlogs

from lib.global_device import GlobalDevice
from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.ipbus_link import IPbusLink
from lib.jadepix_device import JadePixDevice

from data_analysis import data_analysis

from lib import jadepix_defs

import ROOT

import numpy as np
from root_numpy import array2root

from queue import SimpleQueue

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"

if __name__ == '__main__':
    ipbus_link = IPbusLink()

    jadepix_dev = JadePixDevice(ipbus_link)
    global_dev = GlobalDevice(ipbus_link)
    dac70004_dev = Dac70004Device(ipbus_link)

    ''' Soft global reset '''
    global_dev.set_soft_rst()

    ''' DAC70004 Config '''
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
    jadepix_dev.reset_spi()
    jadepix_dev.set_spi(data_len=200, ie=False, ass=True,
                        lsb=False, rx_neg=False, tx_neg=True, div=0, ss=0x01)
    # Set JadePix SPI configuration
    jadepix_dev.start_spi_config()
    # Load Config
    jadepix_dev.load_config_soft()

    ''' JadePix Control '''

    """ From here we can test configuration """
    # start = time.process_time()
    # jadepix_dev.w_cfg()
    # jadepix_dev.start_cfg(go_dispatch=True)
    # print("It takes {:} secends to write configurations to FIFO".format(time.process_time() - start))
    # #
    # time.sleep(20)

    """From here we can test global shutter """
    """sys_clk period = 12 ns, so width = Number * Period"""
    """For pulse width, width = (high<<32 + low) * Period"""
    """Will change to real time later"""
    jadepix_dev.digsel_en(1)
    jadepix_dev.anasel_en(1)
    jadepix_dev.set_dplse_soft(True)  # if false: DPLSE force to low
    jadepix_dev.set_aplse_soft(True)  # if false: APLSE force to low
    jadepix_dev.set_gs_plse(is_dplse=True)  # select digital or analog pulse out
    jadepix_dev.rs_config(cache_bit=0xf, hitmap_col_low=340,
                          hitmap_col_high=348, hitmap_en=True, frame_number=1)
    jadepix_dev.gs_config(pulse_delay=4, width_low=2000, width_high=0, pulse_deassert=2, deassert=5, col=340)
    jadepix_dev.start_gs()

    sys.exit(0)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  
    test_valid_pattern = 1
    frame_per_slice = 64
    num_token = 2

    frame_number = frame_per_slice * num_token
    num_data = frame_number * jadepix_defs.ROW * jadepix_defs.BLK * test_valid_pattern
    num_valid_data_stream = num_data + 2 * frame_number - 1

    rfifo_depth_width = 17
    rfifo_depth = pow(2, rfifo_depth_width)

    slice_size = int(rfifo_depth)  # try largest slice as possible
    num_data_wanted = num_token * slice_size
    data_size = num_data_wanted * 32  # Unit: bit
    log.warning("The data will take {} MB memory".format(data_size / 8 / 2 ** 20))

    jadepix_dev.dig_sel(False)
    jadepix_dev.rs_config(cache_bit=0xf, hitmap_col_low=340,
                          hitmap_col_high=341, hitmap_en=False, frame_number=frame_number)
    jadepix_dev.reset_rfifo()
    jadepix_dev.start_rs()

    # if num_data_wanted > num_valid_data_stream:
    #     new_num_token = int(num_valid_data_stream / slice_size)
    #     log.warning("Token number {:d} should be less than valid number {:d}, set new tolken number to {:d}".format(
    #         num_data_wanted, num_valid_data_stream, new_num_token))
    # else:
    #     new_num_token = num_token

    lost = 0
    ''' Get Data Stream '''
    data_que = SimpleQueue()
    start = time.process_time()
    for j in range(num_token):
        mem = jadepix_dev.read_ipb_data_fifo(slice_size, safe_style=False)
        data_que.put(mem)
    trans_speed = int(data_size / (time.process_time() - start))  # Unit: bps
    log.info("Transfer speed: {:f} Mbps".format(trans_speed / pow(10, 6)))

    log.info("Write data to .root ...")
    data_root_file = "data/data.root"
    hfile = ROOT.gROOT.FindObject(data_root_file)
    if hfile:
        hfile.Close()
    hfile = ROOT.TFile(data_root_file, 'RECREATE', 'Data ROOT file')
    if os.path.exists(data_root_file):
        os.remove(data_root_file)
    start = time.process_time()
    for i in range(num_token):
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
    data_ana = data_analysis.DataAnalysis(data_root_file, frame_number, is_save_png=True)
    lost_tmp, data_num_got = data_ana.draw_data()
    data_lost = num_data - data_num_got
    lost += lost_tmp
    log.info("Lost data num: {:}".format(data_lost))
    log.info("Lost frames: {:}".format(lost))
