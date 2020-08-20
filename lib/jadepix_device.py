import coloredlogs
import logging

from lib.jadepix_defs import *
from lib.spi_device import SpiDevice

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class JadePixDevice(SpiDevice):
    def __init__(self, hw):
        super().__init__(hw)
        self.hw = hw
        self.spi_dev = SpiDevice(self.hw)
        self.spi_reg = 200 * bitarray("0")

    @staticmethod
    def get_spi_reg():
        spi_reg = pll_ibit0 + pll_ibit1 + pll_rbit1 + pll_rbit0 + rsds_sel_tx + rsds_sel_rx + rsds_sel_lpbk + bgp_trim \
                  + bgp_en + vdac6_data + moni_sel_vdac6 + vdac3_data + moni_sel_vdac3 + moni_sel_vdac5 + \
                  vdac5_data.reverse() + moni_sel_vdac2 + vdac2_data.reverse() + vdac4_data + moni_sel_vdac4 + \
                  vdac1_data + moni_sel_vdac1 + idac6_data + moni_sel_idac6 + moni_sel_idac5 + idac5_data.reverse() + \
                  idac4_data + moni_sel_idac4 + moni_sel_idac3 + idac3_data.reverse() + idac2_data + moni_sel_idac2 \
                  + moni_sel_idac1 + idac1_data.reverse()
        return spi_reg

    def update_spi_reg(self):
        self.spi_reg = self.get_spi_reg()

    def get_spi_data(self):
        self.update_spi_reg()
        spi_data = []
        for i in range(0, 8):
            spi_data[i] = self.spi_reg[40 * i:((i + 1) * 40)]
        return spi_data

    def load_config(self, go_dispatch):
        reg_name = "load"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(0)
        node.write(1)
        node.write(0)
        if go_dispatch:
            self.hw.dispatch()

    def w_data_regs(self, go_dispatch):
        self.get_spi_data()
        for i in range(0, 8):
            reg_name = "d" + str(i)
            node_name = self.spi_dev.reg_name_base + reg_name
            node = self.hw.getNode(node_name)
            data = self.get_spi_data()[i]
            node.write(data)
            if go_dispatch:
                self.hw.dispatch()

    def spi_config(self):
        self.w_data_regs(True)
        self.load_config(True)
