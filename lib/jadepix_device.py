import coloredlogs
import logging

from lib.jadepix_defs import *
from lib.spi_device import SpiDevice

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='INFO')
coloredlogs.install(level='INFO', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class JadePixDevice:
    def __init__(self, hw):
        self.hw = hw
        self.reg_name_base = "jadepix_dev."
        self.spi_dev = SpiDevice(self.hw)
        self.spi_reg = bitarray(200 * "0")

        self.cfg_file_path = "./config/jadepix_config.txt"

    @staticmethod
    def get_spi_reg():
        log.info("Reading SPI configuration from defines file...")
        vdac5_data_tmp = vdac5_data
        vdac5_data_tmp.reverse()
        vdac2_data_tmp = vdac2_data
        vdac2_data_tmp.reverse()
        idac5_data_tmp = idac5_data
        idac5_data_tmp.reverse()
        idac3_data_tmp = idac3_data
        idac3_data_tmp.reverse()
        idac1_data_tmp = idac1_data
        idac1_data_tmp.reverse()

        spi_reg = pll_ibit0 + pll_ibit1 + pll_rbit1 + pll_rbit0 + bitarray(4 * "0") + rsds_sel_tx + rsds_sel_rx + \
                  rsds_sel_lpbk + bgp_trim + bgp_en + bitarray(64 * "0") + vdac6_data + moni_sel_vdac6 + vdac3_data + \
                  moni_sel_vdac3 + moni_sel_vdac5 + vdac5_data_tmp + moni_sel_vdac2 + vdac2_data_tmp + vdac4_data + \
                  moni_sel_vdac4 + vdac1_data + moni_sel_vdac1 + idac6_data + moni_sel_idac6 + moni_sel_idac5 + \
                  idac5_data_tmp + idac4_data + moni_sel_idac4 + moni_sel_idac3 + idac3_data_tmp + idac2_data + \
                  moni_sel_idac2 + moni_sel_idac1 + idac1_data_tmp
        log.debug("Lenth of spi_reg bit array: {:d}".format(len(spi_reg)))
        return spi_reg

    def update_spi_reg(self):
        self.spi_reg = self.get_spi_reg()

    def get_spi_data(self):
        self.update_spi_reg()
        spi_data = []
        for i in range(0, 6):
            low = i * 32
            high = (i + 1) * 32
            spi_data.append(int(self.spi_reg[low:high].to01(), base=2))
        spi_data.append(int(self.spi_reg[6 * 32:200].to01(), base=2))
        spi_data.append(0)
        for i in range(0, 8):
            log.debug("SPI Send Data Ch: {:d} Val: {:#010x}".format(i, spi_data[i]))
        return spi_data

    def load_config(self, go_dispatch):
        log.info("Loading spi configuration...")
        reg_name = "load"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(0)
        node.write(1)
        node.write(0)
        if go_dispatch:
            self.hw.dispatch()

    def w_data_regs(self, go_dispatch):
        spi_data = self.get_spi_data()
        log.info("Writing SPI configuration data to SPI data registers...")
        for i in range(0, 8):
            reg_name = "d" + str(i)
            node_name = self.spi_dev.reg_name_base + reg_name
            node = self.hw.getNode(node_name)
            data = spi_data[i]
            node.write(data)
            log.debug("Write d{:d} : {:#010x}".format(i, data))
        if go_dispatch:
            self.hw.dispatch()

    def spi_config(self):
        self.w_data_regs(go_dispatch=False)
        self.spi_dev.w_ctrl(go_dispatch=False)
        self.spi_dev.start(go_dispatch=False)
        self.load_config(go_dispatch=True)

    def w_cfg_fifo(self, data, go_dispatch):
        # log.debug("Write data to JadePix configuration FIFO: {}".format(data))
        reg_name = "cfg_fifo.data"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(data)
        if go_dispatch:
            self.hw.dispatch()

    def wr_en_fifo(self, go_dispatch):
        reg_name = "cfg_fifo.wr_en"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(0)
        node.write(1)
        node.write(0)
        if go_dispatch:
            self.hw.dispatch()

    def g_cfg_fifo_empty(self):
        reg_name = "cfg_fifo_status.empty"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        empty = node.read()
        self.hw.dispatch()
        empty_val = empty.value()
        return empty_val

    def g_cfg_fifo_pfull(self):
        reg_name = "cfg_fifo_status.prog_full"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        pfull = node.read()
        self.hw.dispatch()
        pgull_val = pfull.value()
        return pgull_val

    def g_cfg_fifo_count(self):
        reg_name = "cfg_fifo_status.data_count"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        data_count = node.read()
        self.hw.dispatch()
        count = data_count.value()
        return count

    def clear_fifo(self, go_dispatch):
        log.debug("Clear jadepix configuration FIFO!")
        reg_name = "cfg_fifo_rst"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(0)
        node.write(1)
        node.write(0)
        if go_dispatch:
            self.hw.dispatch()

    def w_cfg(self):
        self.clear_fifo(go_dispatch=True)
        fifo_empty = self.g_cfg_fifo_empty()
        fifo_pfull = self.g_cfg_fifo_pfull()
        fifo_count = self.g_cfg_fifo_count()
        log.debug("Fifo status: empty {} \t prog_full {}, count {}".format(fifo_empty, fifo_pfull, fifo_count))
        cnt = 0
        with open(self.cfg_file_path, mode='r') as fp:
            for line in fp:
                data = int(line, 2)
                row, col = self.calc_row_col(cnt)
                log.info("JadePix config Row {} Col {} : {:#05b}".format(row, col, data))
                self.w_cfg_fifo(data=data, go_dispatch=False)
                self.wr_en_fifo(go_dispatch=True)
                cnt += 1
        if cnt != (ROW * COL):
            log.error("Data count {} is not right, should be {}".format(cnt, ROW * COL))
        fifo_empty = self.g_cfg_fifo_empty()
        fifo_pfull = self.g_cfg_fifo_pfull()
        fifo_count = self.g_cfg_fifo_count()
        log.debug("Fifo status: empty {} \t prog_full {} \t count {}".format(fifo_empty, fifo_pfull, fifo_count))

    def start_cfg(self, go_dispatch):
        log.info("Read configuration from FIFO, and write to JadePix3")
        reg_name = "cfg_start"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(0)
        node.write(1)
        node.write(0)
        if go_dispatch:
            self.hw.dispatch()

    def is_busy_cfg(self):
        log.info("Read configuration from FIFO, and write to JadePix3")
        reg_name = "cfg_busy"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        cfg_busy = node.read()
        self.hw.dispatch()
        cfg_busy_val = cfg_busy.value()
        if cfg_busy_val:
            return True
        else:
            return False

    @staticmethod
    def calc_row_col(cnt):
        row = int(cnt / COL)
        col = int(cnt % COL)
        return row, col
