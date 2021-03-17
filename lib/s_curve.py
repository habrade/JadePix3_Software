import logging
import os
import coloredlogs

from lib import dac70004_defs

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class SCurve():
    def __init__(self, dac_dev, jadepix_dev):
        self._dac_dev = dac_dev
        self._jadepix_dev = jadepix_dev

    def set_pulse_hi(self, pulse_high):
        log.info("Set S-Curve pulse high: {:}".format(pulse_high))
        self._dac_dev.w_ana_chn_update_chn(dac70004_defs.DAC70004_CHN_B, pulse_high)

    def set_pulse_lo(self, pulse_low):
        log.info("Set S-Curve pulse low: {:}".format(pulse_low))
        self._dac_dev.w_ana_chn_update_chn(dac70004_defs.DAC70004_CHN_A, pulse_low)

    def run_scurve_pulse_low_test(self, pulse_hi, pulse_lo_init, pulse_lo_target, lo_step, test_num):
        self.set_pulse_hi(pulse_hi)
        pulse_lo = pulse_lo_init

        data_file_prefix = "./data/scurve/data_pulse_low_test/"

        while pulse_lo < pulse_lo_target:
            for i in range(test_num):
                data_file = "{:s}{:3d}_{:3d}_{:03d}_{:d}.txt".format(data_file_prefix, int(pulse_hi * 1000),
                                                                          int(pulse_lo * 1000),
                                                                          int(lo_step * 1000), i)
                try:
                    os.remove(data_file)
                except OSError:
                    pass
                self.set_pulse_lo(pulse_lo)
                self._jadepix_dev.reset_rfifo()
                self._jadepix_dev.start_gs()
                self._jadepix_dev.read_data(data_file, write2txt=True, safe_mode=True)
            pulse_lo += lo_step
