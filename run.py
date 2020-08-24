#!/usr/bin/env python3
import logging
import coloredlogs

from lib.global_device import GlobalDevice
from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.ipbus_link import IPbusLink
from lib.spi_device import SpiDevice
from lib.jadepix_device import JadePixDevice

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


def dac_config(dac_dev):
    dac_dev.soft_reset()
    dac_dev.soft_clr()
    dac_dev.w_power_chn(DAC70004_PW_UP, 0xf)  # Power up all channels
    dac_dev.w_chn_update_chn(DAC70004_CHN_A, dac_dev.anaVal_2_digVal(1.5))  # Set channle A to 1.5V
    dac_dev.w_chn_update_chn(DAC70004_CHN_B, dac_dev.anaVal_2_digVal(2.0))  # Set channle B to 2.0V


def spi_config(spi_dev):
    spi_dev.set_char_len(200)
    spi_dev.set_ie(False)
    spi_dev.set_ass(True)
    spi_dev.set_lsb(True)
    spi_dev.set_rx_neg(False)
    spi_dev.set_tx_neg(False)
    spi_dev.w_div(1)
    spi_dev.w_ctrl()


if __name__ == '__main__':
    hw = IPbusLink().get_hw()

    jadepix_dev = JadePixDevice(hw)
    global_dev = GlobalDevice(hw)
    dac70004_dev = Dac70004Device(hw)
    spi_dev = SpiDevice(hw)

    ## Soft global reset
    global_dev.set_soft_rst()

    ## DAC70004 Config
    dac_config(dac70004_dev)

    ## SPI master config
    spi_config(spi_dev)

    ## Set JadePix SPI configuration
    jadepix_dev.spi_config()
    # test = jadepix_dev.foo_bar()
    # log.debug("test : {}".format(test))
