import logging

from lib.dac70004_defs import *

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class Dac70004Device:
    def __init__(self, hw):
        self.reg_name_base = "dac70004_dev."
        self.hw = hw

    def is_busy(self):
        reg_name = "DAC_BUSY"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        busy_raw = node.read()
        self.hw.dispatch()
        busy = busy_raw.value()
        return busy == 1

    def write_data(self, data):
        if self.is_busy():
            log.error("DAC70004 is busy now, stop write!")
            return False
        else:
            ## Write to data reg
            reg_name = "DAC_DATA"
            node_name = self.reg_name_base + reg_name
            node = self.hw.getNode(node_name)
            node.write(data)
            ## Set WE
            reg_name = "DAC_WE"
            node_name = self.reg_name_base + reg_name
            node = self.hw.getNode(node_name)
            node.write(1)
            self.hw.dispatch()
            return True

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
    def out_to_din(analog_out):
        if analog_out > DAC70004_REF_VOLT or analog_out < .0:
            raise ValueError(
                'Unexpected analog output value: {0}, should be less than reference voltage'.format(analog_out))
        return int((2 ** 16) * analog_out / DAC70004_REF_VOLT)
