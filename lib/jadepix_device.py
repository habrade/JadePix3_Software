import time

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
    def __init__(self, ipbus_link):
        self._ipbus_link = ipbus_link
        self.reg_name_base = "jadepix_dev."
        self.spi_dev = SpiDevice(self._ipbus_link)
        self.spi_reg = bitarray(200 * "0")

        self._gs_exposure_time = 0
        self._gs_time = 0

    def w_reg(self, reg_name, reg_val, is_pulse, go_dispatch):
        """
        The register write function for Jadepix device.

        :param reg_name:
        :param reg_val:
        :param is_pulse:
        :param go_dispatch:
        :return:
        """
        self._ipbus_link.w_reg(self.reg_name_base, reg_name, reg_val, is_pulse, go_dispatch)

    def r_reg(self, reg_name):
        """
        The register read function for Jadepix device.

        :param reg_name:
        :return:
        """
        return self._ipbus_link.r_reg(self.reg_name_base, reg_name)

    @staticmethod
    def get_spi_reg():
        """
        Reading SPI configuration from defines file...

        :return:
        """
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
        spi_reg.reverse()
        return spi_reg

    def update_spi_reg(self):
        self.spi_reg = self.get_spi_reg()

    def get_spi_data(self):
        self.update_spi_reg()
        spi_data = []
        for i in range(0, 6):
            low = i * 32
            high = (i + 1) * 32
            spi_data.append(int(self.spi_reg[low:high].to01()[::-1], base=2))
        spi_data.append(int((self.spi_reg[6 * 32:200] + 24 * bitarray("0")).to01()[::-1], base=2))
        spi_data.append(0)
        for i in range(0, 8):
            log.debug("SPI Send Data Ch: {:d} Val: {:#010x}".format(i, spi_data[i]))
        return spi_data

    def load_config_soft(self):
        log.info("Loading spi configuration...")
        reg_name = "LOAD"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def set_spi(self, data_len=200, ie=False, ass=True, lsb=True, rx_neg=False, tx_neg=False, div=0, ss=0x01):
        """
        SPI configuration.

        @param data_len: Number of characters to be sent, default=200.
        @param ie: The interrupt output is set active after a transfer is finished.
        @param ass: Set how ss signal is generated.
        @param lsb: LSB or MSB send first.
        @param rx_neg: Receive data at which edge.
        @param tx_neg: Send data at which edge.
        @param div: Clock division.
        @param ss: Write to ss register.
        @return:
        """
        self.spi_dev.set_data_len(data_len)
        self.spi_dev.set_ie(ie)
        self.spi_dev.set_ass(ass)
        self.spi_dev.set_lsb(lsb)
        self.spi_dev.set_rx_neg(rx_neg)
        self.spi_dev.set_tx_neg(tx_neg)
        self.spi_dev.w_div(div)
        self.spi_dev.w_ctrl()
        self.spi_dev.w_ss(ss)

    def is_busy_spi(self):
        """
        Check whether spi us busy.

        :return:
        """
        reg_name = "spi_busy"
        spi_busy = self.r_reg(reg_name)
        if spi_busy == 1:
            return True
        else:
            return False

    def start_spi_config(self):
        """
        Config SPI.

        :return:
        """
        if self.is_busy_spi():
            log.error("SPI is busy now! Stop!")
        else:
            spi_data = self.get_spi_data()
            self.spi_dev.w_data_regs(spi_data=spi_data)
            self.spi_dev.w_ctrl()
            self.spi_dev.start()

    def w_cfg_fifo(self, data, go_dispatch):
        # log.debug("Write data to JadePix configuration FIFO: {}".format(data))
        reg_name = "cfg_fifo.data"
        self.w_reg(reg_name, data, is_pulse=False, go_dispatch=go_dispatch)

    def wr_en_fifo(self, go_dispatch):
        reg_name = "cfg_fifo.wr_en"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=go_dispatch)

    def reset_spi(self, go_dispatch=True):
        """
        Reset SPI.

        :param go_dispatch:
        :return:
        """
        reg_name = "spi_rst"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=go_dispatch)

    def g_cfg_fifo_empty(self):
        """
        Check config FIFO empty status.

        :return:
        """
        reg_name = "cfg_fifo_status.empty"
        return self.r_reg(reg_name)

    def g_cfg_fifo_pfull(self):
        """
        Check config FIFO program-full status.

        :return:
        """
        reg_name = "cfg_fifo_status.prog_full"
        return self.r_reg(reg_name)

    def g_cfg_fifo_count(self):
        """
        Get how many data in the config FIFO.

        :return:
        """
        reg_name = "cfg_fifo_status.data_count"
        return self.r_reg(reg_name)

    def reset_wfifo(self):
        """
        Clear config FIFO.

        :param go_dispatch:
        :return:
        """
        log.debug("Clear jadepix configuration FIFO!")
        reg_name = "cfg_fifo_rst"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=True)

    def w_cfg(self, configs):
        """
        Send all configurations to FIFO.

        :return:
        """
        # Write to fifo
        self.reset_wfifo()
        # Chech Status
        fifo_empty = self.g_cfg_fifo_empty()
        fifo_pfull = self.g_cfg_fifo_pfull()
        fifo_count = self.g_cfg_fifo_count()
        log.debug("Fifo status: empty {} \t prog_full {}, count {}".format(fifo_empty, fifo_pfull, fifo_count))
        log.info("Send configurations to FPGA FIFO...")
        config_list = []
        for i in range(ROW):
            for j in range(COL):
                one_config = configs[i, j]
                con_data = int(one_config[0])
                con_selp = int(one_config[1])
                con_selm = int(one_config[2])
                data = (con_data << 0) + (con_selp << 1) + (con_selm << 2)
                config_list.append(data)
        self.write_ipb_data_fifo(config_list)
        log.info("...write to FPGA FIFO....\nEnd!")
        fifo_empty = self.g_cfg_fifo_empty()
        fifo_pfull = self.g_cfg_fifo_pfull()
        fifo_count = self.g_cfg_fifo_count()
        log.debug("Fifo status: empty {} \t prog_full {} \t count {}".format(fifo_empty, fifo_pfull, fifo_count))

    def start_cfg(self, go_dispatch):
        """
        Send a start pulse to trigger FSM in FPGA.

        :param go_dispatch:
        :return:
        """
        log.info("Read configuration from FIFO, and write to JadePix3")
        reg_name = "cfg_start"
        self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=go_dispatch)

    def is_busy_cfg(self):
        """
         Check config status.

         :return:
         """
        reg_name = "cfg_busy"
        return self.r_reg(reg_name) == 1

    def is_busy_rs(self):
        """

        Check rolling shutter status.
        :return:
        """
        reg_name = "rs_busy"
        return self.r_reg(reg_name) == 1

    def is_busy_gs(self):
        """
        Check global shutter status.

        :return:
        """
        reg_name = "gs_busy"
        return self.r_reg(reg_name) == 1

    @staticmethod
    def calc_row_col(cnt):
        """
        Calculate the row and the col of each pixel by its index count.

        :param cnt:
        :return:
        """
        row = int(cnt / COL)
        col = int(cnt % COL)
        return row, col

    def start_rs(self, go_dispatch=True):
        """
        Start rolling shutter.

        :param go_dispatch:
        :return:
        """
        if self.is_busy_rs():
            log.error("RS is busy now! Stop!")
            return False
        else:
            log.info("Start rolling shutter")
            reg_name = "rs_start"
            self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=go_dispatch)
            return True

    def set_rs_frame_number(self, frame_number, go_dispatch=True):
        """
        Set the frame number of rolling shutter.

        :param frame_number: 22 bits.
        :param go_dispatch:
        :return:
        """
        log.info("Set RS frame number: {}".format(frame_number))
        reg_name = "rs_frame_number"
        self.w_reg(reg_name, frame_number, is_pulse=False, go_dispatch=go_dispatch)

    def set_cache_bit(self, cache_bit, go_dispatch=True):
        """
        Set CACHE_BIT.

        :param cache_bit: range from 0 to 15
        :param go_dispatch:
        :return:
        """
        log.info("Set CACHE_BIT_SET to {:#03x}".format(cache_bit))
        if cache_bit < 0 or cache_bit > 15:
            log.error("CACHE_BIT_SET error, should between 0x0 - 0xF!")
        reg_name = "CACHE_BIT_SET"
        self.w_reg(reg_name, cache_bit, is_pulse=False, go_dispatch=go_dispatch)

    def set_clk_sel(self, clk_sel, go_dispatch):
        """
        Set CLK_SEL.

        :param clk_sel:
        :param go_dispatch:
        :return:
        """
        log.info("Set CLK_SEL to {:}".format(clk_sel))
        reg_name = "CLK_SEL"
        self.w_reg(reg_name, clk_sel, is_pulse=False, go_dispatch=go_dispatch)

    def set_d_rst(self, d_rst, go_dispatch):
        """
        Set digital reset.

        :param d_rst:
        :param go_dispatch:
        :return:
        """
        log.info("Set D_RST to {:}".format(d_rst))
        reg_name = "D_RST"
        self.w_reg(reg_name, d_rst, is_pulse=False, go_dispatch=go_dispatch)

    def set_s_rst(self, s_rst, go_dispatch):
        """
        Set serializer reset.

        :param s_rst:
        :param go_dispatch:
        :return:
        """
        log.info("Set SERIALIZER_RST to {:}".format(s_rst))
        reg_name = "SERIALIZER_RST"
        self.w_reg(reg_name, s_rst, is_pulse=False, go_dispatch=go_dispatch)

    def set_pdb(self, pdb, go_dispatch):
        """
        Set PDB.

        :param pdb:
        :param go_dispatch:
        :return:
        """
        log.info("Set PDB to {:}".format(pdb))
        reg_name = "PDB"
        self.w_reg(reg_name, pdb, is_pulse=False, go_dispatch=go_dispatch)

    def set_sn_oen(self, sn_oen, go_dispatch):
        """
        Output Enable of SN74AVC2T244 (Shift voltage level of rx_fpga, 1.8V to 3.3V).

        :param sn_oen:
        :param go_dispatch:
        :return:
        """
        log.info("Set SN_OEn to {:}".format(sn_oen))
        reg_name = "SN_OEn"
        self.w_reg(reg_name, sn_oen, is_pulse=False, go_dispatch=go_dispatch)

    def set_por(self, por, go_dispatch):
        """
        Set por of ???.

        :param por:
        :param go_dispatch:
        :return:
        """
        log.info("Set POR to {:}".format(por))
        reg_name = "POR"
        self.w_reg(reg_name, por, is_pulse=False, go_dispatch=go_dispatch)

    def set_en_diff(self, en_diff, go_dispatch):
        """
        The ADN4665 is a quad-channel, CMOS, low voltage differential signaling (LVDS) line driver offering data rates of over 400 Mbps (200 MHz) and ultralow power consumption.
        Output enable of single-end to difference signal chip (ADN4665).

        :param en_diff:
        :param go_dispatch:
        :return:
        """
        log.info("Set EN_diff to {:}".format(en_diff))
        reg_name = "EN_diff"
        self.w_reg(reg_name, en_diff, is_pulse=False, go_dispatch=go_dispatch)

    def set_refclk_1G(self, refclk_1G, go_dispatch):
        """
        The LMK1C110x is a modular, high-performance, low-skew, general-purpose clock buffer family from Texas Instruments.
        A synchronous output enable control (1G) which switches the outputs into a low state when 1G is low.

        :param refclk_1G:
        :param go_dispatch:
        :return:
        """
        log.info("Set Ref_clk_1G_f to {:}".format(refclk_1G))
        reg_name = "Ref_clk_1G_f"
        self.w_reg(reg_name, refclk_1G, is_pulse=False, go_dispatch=go_dispatch)

    def set_matrix_grst(self, matrix_grst, go_dispatch):
        """
        Set MATRIX_GRST.

        :param matrix_grst:
        :param go_dispatch:
        :return:
        """
        log.info("Set MATRIX_GRST to {:}".format(matrix_grst))
        reg_name = "MATRIX_GRST"
        self.w_reg(reg_name, matrix_grst, is_pulse=False, go_dispatch=go_dispatch)

    def set_hitmap_addr(self, hitmap_col_low, hitmap_col_high, go_dispatch=True):
        """
        Set hitmap address.

        :param hitmap_col_low: Range 340 to 351.
        :param hitmap_col_high: Range 340 to 351.
        :param go_dispatch:
        :return:
        """
        if hitmap_col_high > 351 or hitmap_col_high < 340 or hitmap_col_low > 351 or hitmap_col_low < 340 or hitmap_col_low > hitmap_col_high:
            log.error("Hitmap address set error, the address should be between 340 and 351. Low = {}, High = {}".format(
                hitmap_col_low, hitmap_col_high))
        else:
            log.info("Set Hitmap col address: {} to {}".format(hitmap_col_low, hitmap_col_high))
        reg_name = "hitmap.col_low"
        self.w_reg(reg_name, hitmap_col_low, is_pulse=False, go_dispatch=go_dispatch)
        reg_name = "hitmap.col_high"
        self.w_reg(reg_name, hitmap_col_high, is_pulse=False, go_dispatch=go_dispatch)
        """set hitmap_number here"""
        hitmap_num = hitmap_col_high - hitmap_col_low + 1
        self.set_hitmap_num(hitmap_num=hitmap_num, go_dispatch=go_dispatch)

    def hitmap_en(self, enable, go_dispatch=True):
        """
        Enable hitmap.

        :param enable:
        :param go_dispatch:
        :return:
        """
        reg_name = "hitmap.en"
        if enable:
            log.info("Enabel Hitmap")
            self.w_reg(reg_name, 1, is_pulse=False, go_dispatch=go_dispatch)
        else:
            log.info("Disable Hitmap")
            self.w_reg(reg_name, 0, is_pulse=False, go_dispatch=go_dispatch)

    def set_hitmap_num(self, hitmap_num, go_dispatch):
        """
        Set hitmap number.

        :param hitmap_num: Range 1 to 12.
        :param go_dispatch:
        :return:
        """
        if hitmap_num > 12 or hitmap_num < 1:
            log.error("Hitmap number should be between 1 and 12, set: {}!".format(hitmap_num))
        reg_name = "hitmap.num"
        self.w_reg(reg_name, hitmap_num, is_pulse=False, go_dispatch=go_dispatch)

    def start_gs(self, go_dispatch=True):
        """
        Start global shutter.

        :param go_dispatch:
        :return:
        """
        if self.is_busy_gs():
            log.error("Global shutter is busy now! Stop!")
        else:
            log.info("Start global shutter...")
            reg_name = "gs_start"
            self.w_reg(reg_name, 0, is_pulse=True, go_dispatch=go_dispatch)
            log.info("Waiting for global shutter end...")
            time.sleep(self._gs_time / pow(10, 9))
            while self.is_busy_gs():
                continue
            log.info("Global shutter end!")

    def set_gs_pulse_delay(self, pulse_delay, go_dispatch=True):
        """
        Set global shutter pulse delay counter.

        :param pulse_delay: 9 bits.
        :param go_dispatch:
        :return:
        """
        reg_name = "gs_pulse_delay_cnt"
        self.w_reg(reg_name, pulse_delay, is_pulse=False, go_dispatch=go_dispatch)

    def set_gs_width_low(self, width_low, go_dispatch=True):
        """
        Set global shutter width, lower part.

        :param width_low: 32 bits.
        :param go_dispatch:
        :return:
        """
        reg_name = "gs_pulse_width_cnt_low"
        self.w_reg(reg_name, width_low, is_pulse=False, go_dispatch=go_dispatch)

    def set_gs_width_high(self, width_high, go_dispatch=True):
        """
        Set global shutter width, higher part.

        :param width_high: 2 bits.
        :param go_dispatch:
        :return:
        """
        reg_name = "gs_pulse_width_cnt_high"
        self.w_reg(reg_name, width_high, is_pulse=False, go_dispatch=go_dispatch)

    def set_gs_pulse_deassert(self, pulse_deassert, go_dispatch=True):
        """
        Set global shutter de-assert counter.

        :param pulse_deassert: 9 bits
        :param go_dispatch:
        :return:
        """
        reg_name = "gs_pulse_deassert_cnt"
        self.w_reg(reg_name, pulse_deassert, is_pulse=False, go_dispatch=go_dispatch)

    def set_gs_deassert(self, deassert, go_dispatch=True):
        """
        Global shutter de-assert.

        :param deassert:
        :param go_dispatch:
        :return:
        """
        reg_name = "gs_deassert_cnt"
        self.w_reg(reg_name, deassert, is_pulse=False, go_dispatch=go_dispatch)

    def set_gs_plse(self, is_dplse, go_dispatch=True):
        """
        Set global shutter pulse type.

        :param is_dplse: Ture: Digital pulse; False: Analog pulse.
        :param go_dispatch:
        :return:
        """
        reg_name = "gs_sel_pulse"
        if is_dplse:
            self.w_reg(reg_name, 1, is_pulse=False, go_dispatch=go_dispatch)
        else:
            self.w_reg(reg_name, 0, is_pulse=False, go_dispatch=go_dispatch)

    def set_gs_col(self, col, go_dispatch=True):
        """
        Set global shutter col.

        :param col: 9 bits.
        :param go_dispatch:
        :return:
        """
        reg_name = "gs_col"
        self.w_reg(reg_name, col, is_pulse=False, go_dispatch=go_dispatch)

    def rs_config(self, cache_bit, hitmap_col_low, hitmap_col_high, hitmap_en, frame_number):
        """
        Rolling shutter configuration.

        :param cache_bit: 4 bits.
        :param hitmap_col_low: 340 to 351.
        :param hitmap_col_high: 340 to 351.
        :param hitmap_en: Enable hitmap.
        :param frame_number:  Frame number, 22 bits.
        :return:
        """
        self.set_cache_bit(cache_bit=cache_bit)
        self.set_hitmap_addr(hitmap_col_low=hitmap_col_low, hitmap_col_high=hitmap_col_high)
        self.set_rs_frame_number(frame_number=frame_number)
        self.hitmap_en(enable=hitmap_en)

    def gs_config(self, pulse_delay, width_low, width_high, pulse_deassert, deassert, col):
        """
        Global shutter configuration.

        :param pulse_delay: 9 bits.
        :param width_low: 32 bits.
        :param width_high: 2 bits.
        :param pulse_deassert: 1 bit.
        :param deassert: 9 bits.
        :param col: 9 bits.
        :return:
        """
        self._gs_exposure_time = (width_low + (width_high << 32)) * SYS_CLK_PERIOD  # Unit: ns
        self._gs_time = (pulse_delay + pulse_deassert + deassert) * SYS_CLK_PERIOD + self._gs_exposure_time
        log.info("Global shutter setting: exposure time: {} ns. total time: {} ns".format(self._gs_exposure_time,
                                                                                          self._gs_time))

        self.set_gs_pulse_delay(pulse_delay=pulse_delay)
        self.set_gs_width_low(width_low=width_low)
        self.set_gs_width_high(width_high=width_high)
        self.set_gs_pulse_deassert(pulse_deassert=pulse_deassert)
        self.set_gs_deassert(deassert=deassert)
        self.set_gs_col(col=col)

    def send_slow_ctrl_cmd(self, cmd):
        """
        Write to WFIFO.

        :param cmd: Data list.
        :return:
        """
        self._ipbus_link.send_slow_ctrl_cmd(self.reg_name_base, "SLCTRL_FIFO", cmd)

    def write_ipb_data_fifo(self, data_list):
        """
        Write to WFIFO (Block write).

        :param data_list:
        :return:
        """
        self._ipbus_link.write_ipb_slow_ctrl_fifo(self.reg_name_base, "SLCTRL_FIFO", data_list)

    def read_ipb_data_fifo(self, num, safe_mode):
        """
        Read from RFIFO.

        :param num:
        :param safe_style: True: safe read. False: not safe read for fast speed.
        :return:
        """
        return self._ipbus_link.read_ipb_data_fifo(self.reg_name_base, "DATA_FIFO", num, safe_mode)

    def reset_rfifo(self):
        """
        Reset RFIFO.

        :return:
        """
        log.info("Reset readout FIFO.")
        self.w_reg("rst_rfifo", 0, is_pulse=True, go_dispatch=True)

    def digsel_en(self, enable):
        self.w_reg("digsel_en", enable, is_pulse=False, go_dispatch=True)

    def anasel_en(self, enable):
        self.w_reg("anasel_en", enable, is_pulse=False, go_dispatch=True)

    def set_dplse_soft(self, enable):
        self.w_reg("dplse_soft", enable, is_pulse=False, go_dispatch=True)

    def set_aplse_soft(self, enable):
        self.w_reg("aplse_soft", enable, is_pulse=False, go_dispatch=True)

    def set_gshutter_soft(self, enable):
        self.w_reg("gshutter_soft", enable, is_pulse=False, go_dispatch=True)

    def set_inquiry(self, inquiry):
        """
        Set chip code output

        :param inquiry:
        :return: 00-K28.5, 01-FIFO, 10-FIFO Status, 11-Reserved
        """
        log.debug("Set INQUIRY : {:}".format(inquiry))
        self.w_reg("INQUIRY", inquiry, is_pulse=False, go_dispatch=True)

    def is_debug(self, enable):
        log.warning(
            "DEBUG mode is {:}, DPLSE, APLSE, DIGSEL_EN, ANASEL_EN, GSHUTTER, CA, CA_EN will set by software.".format(
                enable))
        self.w_reg("DEBUG", enable, is_pulse=False, go_dispatch=True)

    def set_ca_soft(self, ca_soft):
        self.w_reg("CA_SOFT", ca_soft, is_pulse=False, go_dispatch=True)

    def set_ca_en_soft(self, ca_soft):
        self.w_reg("CA_EN_SOFT", ca_soft, is_pulse=False, go_dispatch=True)

    def set_hit_rst_soft(self, hit_rst_soft):
        log.warning("Hit reset software: {:}".format(hit_rst_soft))
        self.w_reg("HIT_RST_SOFT", hit_rst_soft, is_pulse=False, go_dispatch=True)

    def set_chip_clk(self, sel):
        if sel == 0:
            log.warning("Selec")
        log.warning("Chip system clock select: {:}".format(sel))
        self.w_reg("SEL_CHIP_CLK", sel, is_pulse=False, go_dispatch=True)

    def set_blk_sel_def(self, blk_sel_def):
        self.w_reg("BLK_SEL_DEF", blk_sel_def, is_pulse=False, go_dispatch=True)

    def set_cfg_add_factor_t0(self, t0_factor):
        self.w_reg("CFG_ADD_FACTOR_T0", t0_factor, is_pulse=False, go_dispatch=True)

    def set_cfg_add_factor_t1(self, t1_factor):
        self.w_reg("CFG_ADD_FACTOR_T1", t1_factor, is_pulse=False, go_dispatch=True)

    def set_cfg_add_factor_t2(self, t2_factor):
        self.w_reg("CFG_ADD_FACTOR_T2", t2_factor, is_pulse=False, go_dispatch=True)
