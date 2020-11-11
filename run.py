#!/usr/bin/env python3
import time
import logging

import coloredlogs

from lib.global_device import GlobalDevice
from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.ipbus_link import IPbusLink
from lib.jadepix_device import JadePixDevice

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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

    ## Soft global reset
    global_dev.set_soft_rst()

    ## DAC70004 Config
    dac70004_dev.soft_reset()
    dac70004_dev.soft_clr()
    dac70004_dev.w_power_chn(DAC70004_PW_UP, 0xf)  # Power up all channels
    dac70004_dev.w_ana_chn_update_chn(DAC70004_CHN_A, 1.5)  # Set channle A to 1.5V
    dac70004_dev.w_ana_chn_update_chn(DAC70004_CHN_B, 2.0)  # Set channle B to 2.0V

    ## SPI master config
    jadepix_dev.reset_spi()
    jadepix_dev.set_spi(data_len=200, ie=False, ass=True, lsb=False, rx_neg=False, tx_neg=True, div=0, ss=0x01)
    ## Set JadePix SPI configuration
    jadepix_dev.start_spi_config()
    ## Load Config
    jadepix_dev.load_config_soft()

    ## JadePix Control

    """ From here we can test configuration """
    # start = time.process_time()
    # jadepix_dev.w_cfg()
    # jadepix_dev.start_cfg(go_dispatch=True)
    # print("It takes {:} secends to write configurations to FIFO".format(time.process_time() - start))
    #
    # time.sleep(20)

    """ From here we can test rolling shutter """
    jadepix_dev.set_gs_plse(is_dplse=True)
    jadepix_dev.rs_config(cache_bit=0xf, hitmap_col_low=340, hitmap_col_high=341, hitmap_en=False, frame_number=100000)
    jadepix_dev.start_rs()
    # time.sleep(2)

    """From here we can test global shutter """
    """sys_clk period = 12 ns, so width = Number * Period"""
    """For pulse width, width = (high<<32 + low) * Period"""
    """Will change to real time later"""
    # jadepix_dev.gs_config(pulse_delay=4, width_low=3, width_high=0, pulse_deassert=2, deassert=5, col=224)
    # jadepix_dev.start_gs()

    rfifo_depth_width = 17
    rfifo_depth = pow(2, rfifo_depth_width)
    data_path = "./data/data.txt"
    slice_size = rfifo_depth
    # log.info("The number (word, 32bits) of data wanted: {:d}".format(slice_size))

    ## remove data file before taking data
    import os
    if os.path.exists(data_path):
        os.remove(data_path)

    num_token = 20
    data_amount = num_token * slice_size * 32

    start = time.process_time()
    for i in range(num_token):
        mem = jadepix_dev.read_ipb_data_fifo(slice_size)
        # with open(data_path, 'a') as file_handler:
        #     for item in mem:
        #         file_handler.write("{:08x}\n".format(item))
        # del mem    
    trans_time = time.process_time() -start
    trans_speed = int(data_amount / trans_time) # Unit: bps
    log.info("Transfer time: {:f} s".format(trans_time))
    log.info("Transfer speed: {:f} Mbps".format(trans_speed/pow(10, 6)))
    # file_handler.close()