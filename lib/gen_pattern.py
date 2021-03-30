from lib import jadepix_defs
import os
import numpy as np
from functools import partialmethod
import coloredlogs
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
# coloredlogs.install(level='DEBUG')
# coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class GenPattern:
    def __init__(self):
        # self._config_arr = config_arr
        self._test_patter_path = "data/test_pattern.txt"

    def set_config(self, config_arr, row_low, row_high, col_low, col_high, bit_nr, data):
        config_arr[row_low:row_high, col_low:col_high, bit_nr] = data

    set_con_selm = partialmethod(set_config, bit_nr=0)
    set_con_selp = partialmethod(set_config, bit_nr=1)
    set_con_data = partialmethod(set_config, bit_nr=2)

    def calc_blk(self, col):
        return int((col % 48) / 3)

    def calc_pix_out(self, config):
        """ dout = ~CON_MASK & CON_PLSE & CON_DATA """
        return ((not config[0]) & config[1] & config[2])

    def calc_data_out(self, row, blk, pix_data):
        return (row << 7) + (blk << 3) + pix_data

    def gen_test_pattern(self, config_arr):
        line_num = 0
        dout_arr = np.zeros(3, int)
        data_string = []
        try:
            os.remove(self._test_patter_path)
        except OSError:
            pass
        with open(self._test_patter_path, "w+") as f:
            for row in range(jadepix_defs.ROW):
                for col in range(jadepix_defs.COL):
                    blk = self.calc_blk(col)
                    pix_bit = col % 3
                    pix_out = self.calc_pix_out(config_arr[row, col])

                    block = int(col / 48)

                    dout_arr[pix_bit] = pix_out
                    if pix_bit == 2:
                        pix_data = int((dout_arr[2] << 2) | (
                                dout_arr[1] << 1) | dout_arr[0])
                        dout_arr = np.empty((3, 1), int)
                        if pix_data > 0:
                            log.debug("row: {} col: {} data: {}".format(
                                row, col, pix_data))
                            data_out = self.calc_data_out(row, blk, pix_data)
                            line_num += 1
                            data_flag = 2
                            data_string.append("{:#010x}\n".format(
                                (data_flag << 30) + (block << 16) + data_out))
            f.write("".join(data_string))
        return line_num

    def code_cepc(self, config_arr):
        """ code CEPC """
        """ C """
        self.set_config(config_arr, 32, 33, 24, 168, 1, 2)
        self.set_config(config_arr, 32, 96, 24, 25, 1, 2)
        self.set_config(config_arr, 96, 97, 24, 168, 1, 2)
        """ E """
        self.set_config(config_arr, 32+128, 33+128, 24, 168, 1, 2)
        self.set_config(config_arr, 32+128+32, 33+128+32, 24, 168, 1, 2)
        self.set_config(config_arr, 32+128, 96+128, 24, 25, 1, 2)
        self.set_config(config_arr, 96+128, 97+128, 24, 168, 1, 2)
        """ P """
        self.set_config(config_arr, 32+128*2, 33+128*2, 24, 168, 1, 2)
        self.set_config(config_arr, 32+128*2+32, 33+128*2+32, 24, 168, 1, 2)
        self.set_config(config_arr, 32+128*2, 96+128*2, 24, 25, 1, 2)
        self.set_config(config_arr, 32+128*2, 33+128*2, 168, 168+32, 1, 2)
        """ C """
        self.set_config(config_arr, 32+128*3, 33+128*3, 24, 168, 1, 2)
        self.set_config(config_arr, 32+128*3, 96+128*3, 24, 25, 1, 2)
        self.set_config(config_arr, 96+128*3, 97+128*3, 24, 168, 1, 2)


    def code_c(self, config_arr):
        self.set_config(config_arr, 64, 65, 48, 144, 1, 2)
        self.set_config(config_arr, 64, 448, 48, 49, 1, 2)
        self.set_config(config_arr, 448, 449, 48, 144, 1, 2)

    def code_n(self, config_arr):
        self.set_config(config_arr, 64, 448, 48, 49, 1, 2)
        self.set_config(config_arr, 64, 448, 144, 145, 1, 2)
        for i in range(144-48):
            delta_row = 384/(144-48)
            x = 48 + i
            y = 64 + delta_row*i
            self.set_config(config_arr, x, x+1, y, y+1, 1, 2)

    def code_u(self, config_arr):
        self.set_config(config_arr, 64, 448, 48, 49, 1, 2)
        self.set_config(config_arr, 64, 448, 144, 145, 1, 2)
        self.set_config(config_arr, 448, 448+1, 48, 144, 1, 2)
