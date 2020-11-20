#!/usr/bin/env python3
import time
import logging

import coloredlogs

from lib.global_device import GlobalDevice
from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.ipbus_link import IPbusLink
from lib.jadepix_device import JadePixDevice

from ROOT import gROOT, TFile, TTree
from array import array

from data_analysis import data_analysis

from lib import jadepix_defs

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

    # Soft global reset
    global_dev.set_soft_rst()

    # DAC70004 Config
    dac70004_dev.soft_reset()
    dac70004_dev.soft_clr()
    dac70004_dev.w_power_chn(DAC70004_PW_UP, 0xf)  # Power up all channels
    dac70004_dev.w_ana_chn_update_chn(
        DAC70004_CHN_A, 1.5)  # Set channle A to 1.5V
    dac70004_dev.w_ana_chn_update_chn(
        DAC70004_CHN_B, 2.0)  # Set channle B to 2.0V

    # SPI master config
    jadepix_dev.reset_spi()
    jadepix_dev.set_spi(data_len=200, ie=False, ass=True,
                        lsb=False, rx_neg=False, tx_neg=True, div=0, ss=0x01)
    # Set JadePix SPI configuration
    jadepix_dev.start_spi_config()
    # Load Config
    jadepix_dev.load_config_soft()

    # JadePix Control

    """ From here we can test configuration """
    # start = time.process_time()
    # jadepix_dev.w_cfg()
    # jadepix_dev.start_cfg(go_dispatch=True)
    # print("It takes {:} secends to write configurations to FIFO".format(time.process_time() - start))
    #
    # time.sleep(20)

    """ From here we can test rolling shutter """
    frame_number = 640*2
    jadepix_dev.set_gs_plse(is_dplse=True)
    jadepix_dev.rs_config(cache_bit=0xf, hitmap_col_low=340,
                          hitmap_col_high=341, hitmap_en=False, frame_number=frame_number)
    jadepix_dev.reset_rfifo()
    jadepix_dev.start_rs()

    """From here we can test global shutter """
    """sys_clk period = 12 ns, so width = Number * Period"""
    """For pulse width, width = (high<<32 + low) * Period"""
    """Will change to real time later"""
    # jadepix_dev.gs_config(pulse_delay=4, width_low=3, width_high=0, pulse_deassert=2, deassert=5, col=224)
    # jadepix_dev.start_gs()

    test_valid_pattern = 1
    num_valid_data = frame_number * jadepix_defs.ROW * \
                     jadepix_defs.BLK * test_valid_pattern + 2 * frame_number - 1

    rfifo_depth_width = 17
    rfifo_depth = pow(2, rfifo_depth_width)

    slice_size = int(rfifo_depth)  # try largest slice as possible

    num_token = 10 * 1
    num_data_wanted = num_token * slice_size

    if num_data_wanted > num_valid_data:
        new_num_token = int(num_valid_data / slice_size)
        log.warning("Token number {:d} should be less than valid number {:d}, set new tolken number to {:d}".format(
            num_data_wanted, num_valid_data, new_num_token))
    else:
        new_num_token = num_token

    num_data_got = new_num_token * slice_size
    data_size = num_data_got * 32  # Unit: bit
    # Get Data Stream and Write to txt
    data_list = []
    start = time.process_time()
    for i in range(new_num_token):
        mem = jadepix_dev.read_ipb_data_fifo(slice_size, safe_style=False)
        data_list.append(mem)
    trans_speed = int(data_size / (time.process_time() - start))  # Unit: bps
    log.info("Transfer speed: {:f} Mbps".format(trans_speed / pow(10, 6)))

    # Write data to .root
    log.info("Write data to .root ...")
    data_file = "data/data.root"
    hfile = gROOT.FindObject(data_file)
    if hfile:
        hfile.Close()
    hfile = TFile(data_file, 'RECREATE', 'Data ROOT file')

    data = array("I", [0])
    d_tree = TTree('root_tree', 'Data_Stream')
    d_branch = d_tree.Branch('data', data, 'data/i')
    for data_vector in data_list:
        for data_in in data_vector:
            data[0] = data_in
            d_tree.Fill()
        del data_vector
    del data_list
    d_tree.Write()

    hfile.Close()
    log.info("Write to .root end.")

    data_analysis.draw_data(data_file)
