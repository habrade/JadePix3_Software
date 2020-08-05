#!/usr/bin/env python
import logging
import coloredlogs

from lib.global_device import GlobalDevice
from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.ipbus_link import IPbusLink

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"

if __name__ == '__main__':
    hw = IPbusLink().get_hw()

    global_dev = GlobalDevice(hw)
    dac70004_dev = Dac70004Device(hw)

    ## Soft global reset
    global_dev.set_soft_rst()

    ## SET DAC70004
    dac70004_dev.soft_reset()
    dac70004_dev.soft_clr()
    dac70004_dev.w_power_chn(DAC70004_PW_UP, 0xf)  # Power up all channels
    dac70004_dev.w_chn_update_chn(DAC70004_CHN_A, dac70004_dev.out_to_din(1.5))  # Set channle A to 1.5V
    dac70004_dev.w_chn_update_chn(DAC70004_CHN_B, dac70004_dev.out_to_din(2.0))  # Set channle B to 2.0V
