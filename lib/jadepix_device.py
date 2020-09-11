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

    def load_config(self, go_dispatch=True):
        log.info("Loading spi configuration...")
        reg_name = "LOAD"
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
            log.info("Start read configuration from file, and write to FPGA FIFO...")
            for line in fp:
                data = int(line, 2)
                row, col = self.calc_row_col(cnt)
                log.debug("JadePix config Row {} Col {} : {:#05b}".format(row, col, data))
                self.w_cfg_fifo(data=data, go_dispatch=False)
                self.wr_en_fifo(go_dispatch=True)
                cnt += 1
        log.info("...write to FPGA FIFO....\nEnding!")
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

    def is_busy_rs(self):
        reg_name = "rs_busy"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        rs_busy = node.read()
        self.hw.dispatch()
        rs_busy_val = rs_busy.value()
        if rs_busy_val == 1:
            log.debug("RS is busy")
            return True
        else:
            log.debug("RS is NOT busy")
            return False

    def is_busy_gs(self):
        reg_name = "gs_busy"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        gs_busy = node.read()
        self.hw.dispatch()
        gs_busy_val = gs_busy.value()
        if gs_busy_val == 1:
            log.debug("GS is busy")
            return True
        else:
            log.debug("GS is NOT busy")
            return False

    @staticmethod
    def calc_row_col(cnt):
        row = int(cnt / COL)
        col = int(cnt % COL)
        return row, col

    def start_rs(self, go_dispatch=True):
        if self.is_busy_rs():
            log.error("RS is busy now! Stop!")
        else:
            log.info("Start rolling shutter")
            reg_name = "rs_start"
            node_name = self.reg_name_base + reg_name
            node = self.hw.getNode(node_name)
            node.write(0)
            node.write(1)
            node.write(0)
            if go_dispatch:
                self.hw.dispatch()

    def set_rs_frame_number(self, frame_number, go_dispatch=True):
        log.info("Set RS frame number: {}".format(frame_number))
        reg_name = "rs_frame_number"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(frame_number)
        if go_dispatch:
            self.hw.dispatch()

    def cache_bit_set(self, cache_bit, go_dispatch):
        log.info("Set CACHE_BIT_SET to {:#03x}".format(cache_bit))
        if cache_bit < 0 or cache_bit > 15:
            log.error("CACHE_BIT_SET error, should between 0x0 - 0xF!")
        reg_name = "CACHE_BIT_SET"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(cache_bit)
        if go_dispatch:
            self.hw.dispatch()

    def set_pdb(self, pdb, go_dispatch):
        log.info("Set PDB to {:}".format(pdb))
        reg_name = "PDB"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(pdb)
        if go_dispatch:
            self.hw.dispatch()

    def set_matrix_grst(self, matrix_grst, go_dispatch):
        log.info("Set MATRIX_GRST to {:}".format(matrix_grst))
        reg_name = "MATRIX_GRST"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(matrix_grst)
        if go_dispatch:
            self.hw.dispatch()

    def set_hitmap_addr(self, hitmap_col_low, hitmap_col_high, go_dispatch):
        if hitmap_col_high > 351 or hitmap_col_high < 340 or hitmap_col_low > 351 or hitmap_col_low < 340 or hitmap_col_low > hitmap_col_high:
            log.error("Hitmap address set error, the address should be between 340 and 351. Low = {}, High = {}".format(
                hitmap_col_low, hitmap_col_high))
        else:
            log.info("Set Hitmap col address: {} to {}".format(hitmap_col_low, hitmap_col_high))
        reg_name = "hitmap.col_low"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(hitmap_col_low)
        reg_name = "hitmap.col_high"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(hitmap_col_high)

        # set hitmap_number here?
        hitmap_num = hitmap_col_high - hitmap_col_low + 1
        self.set_hitmap_num(hitmap_num=hitmap_num, go_dispatch=go_dispatch)
        if go_dispatch:
            self.hw.dispatch()

    def hitmap_en(self, enable, go_dispatch):
        log.info("Enabel Hitmap")
        reg_name = "hitmap.en"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        if enable:
            node.write(1)
        else:
            node.write(0)
        if go_dispatch:
            self.hw.dispatch()

    def set_hitmap_num(self, hitmap_num, go_dispatch):
        if hitmap_num > 12 or hitmap_num < 1:
            log.error("Hitmap number should be between 1 and 12, set: {}!".format(hitmap_num))
        reg_name = "hitmap.num"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(hitmap_num)
        if go_dispatch:
            self.hw.dispatch()

    def start_gs(self, go_dispatch=True):
        if self.is_busy_gs():
            log.error("GS is busy now! Stop!")
        else:
            log.info("Start GS...")
            reg_name = "gs_start"
            node_name = self.reg_name_base + reg_name
            node = self.hw.getNode(node_name)
            node.write(0)
            node.write(1)
            node.write(0)
            if go_dispatch:
                self.hw.dispatch()

    def set_gs_pulse_delay(self, pulse_delay, go_dispatch=True):
        reg_name = "gs_pulse_delay_cnt"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(pulse_delay)
        if go_dispatch:
            self.hw.dispatch()

    def set_gs_width_low(self, width_low, go_dispatch=True):
        reg_name = "gs_pulse_width_cnt_low"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(width_low)
        if go_dispatch:
            self.hw.dispatch()

    def set_gs_width_high(self, width_high, go_dispatch=True):
        reg_name = "gs_pulse_width_cnt_high"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(width_high)
        if go_dispatch:
            self.hw.dispatch()

    def set_gs_pulse_deassert(self, pulse_deassert, go_dispatch=True):
        reg_name = "gs_pulse_deassert_cnt"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(pulse_deassert)
        if go_dispatch:
            self.hw.dispatch()

    def set_gs_deassert(self, deassert, go_dispatch=True):
        reg_name = "gs_deassert_cnt"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(deassert)
        if go_dispatch:
            self.hw.dispatch()

    def set_gs_col(self, col, go_dispatch=True):
        reg_name = "gs_col"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(col)
        if go_dispatch:
            self.hw.dispatch()

    def rs_config(self, cache_bit, hitmap_col_low, hitmap_col_high, hitmap_en, frame_number):
        self.cache_bit_set(cache_bit=cache_bit, go_dispatch=True)
        self.set_hitmap_addr(hitmap_col_low=hitmap_col_low, hitmap_col_high=hitmap_col_high, go_dispatch=True)
        self.set_rs_frame_number(frame_number=frame_number)
        self.hitmap_en(enable=hitmap_en, go_dispatch=True)

    def gs_config(self, pulse_delay, width_low, width_high, pulse_deassert, deassert, col):
        self.set_gs_pulse_delay(pulse_delay=pulse_delay)
        self.set_gs_width_low(width_low=width_low)
        self.set_gs_width_high(width_high=width_high)
        self.set_gs_pulse_deassert(pulse_deassert=pulse_deassert)
        self.set_gs_deassert(deassert=deassert)
        self.set_gs_col(col=col)
