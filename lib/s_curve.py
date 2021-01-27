import logging
import os

import coloredlogs

from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.jadepix_device import JadePixDevice

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class SCurve(JadePixDevice, Dac70004Device):
    def __init__(self, ipbus_link):
        super(SCurve, self).__init__(ipbus_link)

    def set_pulse_hi(self, pulse_high):
        log.info("Set S-Curve pulse high: {:}".format(pulse_high))
        self.w_ana_chn_update_chn(DAC70004_CHN_B, pulse_high)

    def set_pulse_lo(self, pulse_low):
        log.info("Set S-Curve pulse low: {:}".format(pulse_low))
        self.w_ana_chn_update_chn(DAC70004_CHN_A, pulse_low)

    def run_scurve_pulse_low_test(self, pulse_hi, pulse_lo_init, pulse_lo_target, lo_step, test_num):
        data_file_prefix = "data/scurve/data_pulse_low_test/"
        self.set_pulse_hi(pulse_hi)
        pulse_lo = pulse_lo_init
        while pulse_lo < pulse_lo_target:
            for i in range(test_num):
                self.set_pulse_lo(pulse_lo)
                self.reset_rfifo()
                self.start_gs()
                mem = self.read_ipb_data_fifo(1, safe_mode=True)
                data_string = []
                data_file = "{:s}_{:3d}_{:3d}_{:03d}_{:d}.txt".format(data_file_prefix, pulse_hi * 1000,
                                                                      pulse_lo * 1000,
                                                                      lo_step * 1000, i)
                try:
                    os.remove(data_file)
                except OSError:
                    pass
                with open(data_file, 'w+') as data_file:
                    for data in mem:
                        data_string.append("{:#010x}\n".format(data))
                    data_file.write("".join(data_string))
                pulse_lo += lo_step
