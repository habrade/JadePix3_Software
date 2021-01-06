import sys
import time
import coloredlogs
import logging
from lib.dac70004_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='INFO')
coloredlogs.install(level='INFO', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class Dac70004Device:
    def __init__(self, ipbus_link):
        self.reg_name_base = "dac70004_dev."
        self._ipbus_link = ipbus_link

    def w_reg(self, reg_name, reg_val, is_pulse, go_dispatch):
        self._ipbus_link.w_reg(self.reg_name_base, reg_name, reg_val, is_pulse, go_dispatch)

    def r_reg(self, reg_name):
        self._ipbus_link.r_reg(self.reg_name_base, reg_name)

    def is_busy(self):
        reg_name = "DAC_BUSY"
        return self.r_reg(reg_name) == 1

    def write_data(self, data):
        busy = self.is_busy()
        while busy:
            log.warning("DAC70004 is busy now, stop writing!")
            time.sleep(0.003)
            busy = self.is_busy()
        """Write to data reg"""
        reg_name = "DAC_DATA"
        self.w_reg(reg_name, data, is_pulse=False, go_dispatch=False)
        """Set WE"""
        reg_name = "DAC_WE"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def cmd(self, wr, cmd, chn, din, mode):
        if cmd not in [DAC70004_CMD_WR_BUF, DAC70004_CMD_UPDATE_CHN, DAC70004_CMD_W_UPDATE_ALL, DAC70004_CMD_W_UPDATE,
                       DAC70004_CMD_POWER_ONOFF, DAC70004_CMD_CLR_MODE, DAC70004_CMD_LDAC_REG, DAC70004_CMD_SOFT_RST,
                       DAC70004_CMD_DIS_SDO, DAC70004_CMD_RESERVED_1, DAC70004_CMD_SCL_REG, DAC70004_CMD_SOFT_CLR,
                       DAC70004_CMD_RESERVED_2, DAC70004_CMD_STATUS_REG, DAC70004_CMD_NOP, DAC70004_CMD_RESERVED_3]:
            raise ValueError('Unexpected cmd value {0}.'.format(cmd))
        send_data = (wr << 28) + (cmd << 24) + (chn << 20) + (din << 4) + mode
        return self.write_data(send_data)

    def w_buf(self, chn, din):
        if chn not in [DAC70004_CHN_A, DAC70004_CHN_B, DAC70004_CHN_C, DAC70004_CHN_D, DAC70004_CHN_ALL]:
            raise ValueError('Unexpected chn value {0}.'.format(chn))
        return self.cmd(0, DAC70004_CMD_WR_BUF, chn, din, 0)

    def r_buf(self, chn, din):
        if chn not in [DAC70004_CHN_A, DAC70004_CHN_B, DAC70004_CHN_C, DAC70004_CHN_D, DAC70004_CHN_ALL]:
            raise ValueError('Unexpected chn value {0}.'.format(chn))
        return self.cmd(1, DAC70004_CMD_WR_BUF, chn, din, 0)

    def update_chn(self, chn):
        if chn not in [DAC70004_CHN_A, DAC70004_CHN_B, DAC70004_CHN_C, DAC70004_CHN_D, DAC70004_CHN_ALL]:
            raise ValueError('Unexpected chn value {0}.'.format(chn))
        return self.cmd(0, DAC70004_CMD_UPDATE_CHN, chn, 0, 0)

    def w_chn_update_all(self, chn, din):
        if chn not in [DAC70004_CHN_A, DAC70004_CHN_B, DAC70004_CHN_C, DAC70004_CHN_D, DAC70004_CHN_ALL]:
            raise ValueError('Unexpected chn value {0}.'.format(chn))
        return self.cmd(0, DAC70004_CMD_W_UPDATE_ALL, chn, din, 0)

    def w_chn_update_chn(self, chn, din):
        if chn not in [DAC70004_CHN_A, DAC70004_CHN_B, DAC70004_CHN_C, DAC70004_CHN_D, DAC70004_CHN_ALL]:
            raise ValueError('Unexpected chn value {0}.'.format(chn))
        return self.cmd(0, DAC70004_CMD_W_UPDATE, chn, din, 0)

    def w_ana_chn_update_chn(self, chn, vout):
        if vout > 1.8 or vout < 0:
            log.error("Voltage shouldn't larger than 1.8 and less than 0, now: {:}".format(vout))
            sys.exit(0)
        else:
            self.w_chn_update_chn(chn, self.anaVal_2_digVal(vout))

    def w_power_chn(self, pd_bits, chn_map):
        # mode = chn_map, mode[0]=ch-A, mode[1]=ch-B, mode[2]=ch-C, mode[3]=ch-D
        if pd_bits not in [DAC70004_PW_UP, DAC70004_PW_DOWN_1K, DAC70004_PW_DOWN_100K, DAC70004_PW_DOWN_HIZ]:
            raise ValueError('Unexpected pd_bits value {0}.'.format(pd_bits))
        return self.cmd(0, DAC70004_CMD_POWER_ONOFF, pd_bits << 8, 0, chn_map)

    def r_power_chn(self, chn_map, pd_bits):
        # mode = chn_map, mode[0]=ch-A, mode[1]=ch-B, mode[2]=ch-C, mode[3]=ch-D
        if pd_bits not in [DAC70004_PW_UP, DAC70004_PW_DOWN_1K, DAC70004_PW_DOWN_100K, DAC70004_PW_DOWN_HIZ]:
            raise ValueError('Unexpected pd_bits value {0}.'.format(pd_bits))
        return self.cmd(1, DAC70004_CMD_POWER_ONOFF, pd_bits << 8, 0, chn_map)

    def w_clr_mode_reg(self, cm_bits):
        # mode[1:0] = cm_bits, mode[0]=CM0, mode[1]=CM1
        if cm_bits not in [DAC70004_CM_ZERO, DAC70004_CM_MID, DAC70004_CM_FULL]:
            raise ValueError('Unexpected cm_bits value {0}.'.format(cm_bits))
        return self.cmd(0, DAC70004_CMD_CLR_MODE, 0, 0, cm_bits)

    def r_clr_mode_reg(self, cm_bits):
        # mode[1:0] = cm_bits, mode[0]=CM0, mode[1]=CM1
        if cm_bits not in [DAC70004_CM_ZERO, DAC70004_CM_MID, DAC70004_CM_FULL]:
            raise ValueError('Unexpected cm_bits value {0}.'.format(cm_bits))
        return self.cmd(1, DAC70004_CMD_CLR_MODE, 0, 0, cm_bits)

    def soft_reset(self):
        return self.cmd(0, DAC70004_CMD_SOFT_RST, 0, 0, 0)

    def w_disable_sdo(self, dsd):
        # TODO: check mode
        return self.cmd(0, DAC70004_CMD_DIS_SDO, 0, 0, 0)

    def r_disable_sdo(self, dsd):
        # TODO: check mode
        return self.cmd(1, DAC70004_CMD_DIS_SDO, 0, 0, 0)

    def w_set_scl(self, chn_map):
        """Short circuit limit register"""
        # mode = chn_map, mode[0]=ch-A, mode[1]=ch-B, mode[2]=ch-C, mode[3]=ch-D
        return self.cmd(0, DAC70004_CMD_SCL_REG, 0, 0, chn_map)

    def r_set_scl(self, chn_map):
        """
        Short circuit limit register
        :param chn_map: mode = chn_map, mode[0]=ch-A, mode[1]=ch-B, mode[2]=ch-C, mode[3]=ch-D
        """
        return self.cmd(1, DAC70004_CMD_SCL_REG, 0, 0, chn_map)

    def soft_clr(self):
        return self.cmd(0, DAC70004_CMD_SOFT_CLR, 0, 0, 0)

    def r_status(self):
        return self.cmd(1, DAC70004_CMD_STATUS_REG, 0, 0, 0)

    def w_nop(self):
        return self.cmd(0, DAC70004_CMD_NOP, 0, 0, 0)

    @staticmethod
    def anaVal_2_digVal(anaVal):
        if anaVal > DAC70004_REF_VOLT or anaVal < .0:
            raise ValueError(
                'Unexpected analog output value: {0}, should be less than reference voltage'.format(anaVal))
        digVal = int((2 ** 16) * anaVal / DAC70004_REF_VOLT)
        log.debug("Convert analog to digital: {:f} {:d}".format(anaVal, digVal))
        return digVal
