import coloredlogs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class SpiDevice:
    def __init__(self, ipbus_link):
        self._ipbus_link = ipbus_link
        self.reg_name_base = "spi_dev."

        self.data_len = 0
        self.go_busy = 0
        self.rx_neg = 0
        self.tx_neg = 0
        self.lsb = 0
        self.ie = 0
        self.ass = 1

        self.ctrl = 0x00000000

    def w_reg(self, reg_name, reg_val, is_pulse, go_dispatch):
        self._ipbus_link.w_reg(self.reg_name_base, reg_name, reg_val, is_pulse, go_dispatch)

    def r_reg(self, reg_name):
        return self._ipbus_link.r_reg(self.reg_name_base, reg_name)

    def set_data_len(self, data_len):
        if data_len not in range(0, 256):
            raise ValueError('Unexpected char_len number: {0}, should be less than 256'.format(data_len))
        self.data_len = data_len
        log.debug("Set how many bits are transmitted in one transfer: {}".format(data_len))
        self.update_ctrl()

    def set_rx_neg(self, enabled):
        if not isinstance(enabled, bool):
            raise ValueError('Unexpected parameter, it must be boolean: {}'.format(enabled))
        if enabled:
            self.rx_neg = 1
            log.debug("The miso_pad_i signal is latched on the falling edge of a sclk_pad_o clock signal")
        else:
            self.rx_neg = 0
            log.debug("The miso_pad_i signal is latched on the rising edge of a sclk_pad_o clock signal")
        self.update_ctrl()

    def set_tx_neg(self, enabled):
        if not isinstance(enabled, bool):
            raise ValueError('Unexpected parameter, it must be boolean: {}'.format(enabled))
        if enabled:
            self.tx_neg = 1
            log.debug("The mosi_pad_o signal is changed on the falling edge of a sclk_pad_o clock signal")
        else:
            self.tx_neg = 0
            log.debug("The mosi_pad_o signal is changed on the rising edge of a sclk_pad_o clock signal")
        self.update_ctrl()

    def set_go_busy(self, enabled=True):
        if not isinstance(enabled, bool):
            raise ValueError('Unexpected parameter, it must be boolean: {}'.format(enabled))
        if enabled:
            self.go_busy = 1
            log.debug("Starts the transfer")
        else:
            self.go_busy = 0
            log.warning("set_go_busy: Writing 0 to this bit has no effect")
        self.update_ctrl()

    def set_lsb(self, enabled):
        if not isinstance(enabled, bool):
            raise ValueError('Unexpected parameter, it must be boolean: {}'.format(enabled))
        if enabled:
            self.lsb = 1
            log.debug(
                "The LSB is sent first on the line, and the first bit received from the line will be put in the LSB position in the Rx register ")
        else:
            self.lsb = 0
            log.debug(
                "The MSB is sent first on the line, and the first bit received from the line will be put in the MSB position in the Rx register ")
        self.update_ctrl()

    def set_ie(self, enabled):
        if not isinstance(enabled, bool):
            raise ValueError('Unexpected parameter, it must be boolean: {}'.format(enabled))
        if enabled:
            self.ie = 1
            log.debug("The interrupt output is set active after a transfer is finished.")
        else:
            self.ie = 0
            log.warning("set_ie: Writing 0 to this bit has no effect")
        self.update_ctrl()

    def set_ass(self, enabled):
        if not isinstance(enabled, bool):
            raise ValueError('Unexpected parameter, it must be boolean: {}'.format(enabled))
        if enabled:
            self.ass = 1
            log.debug("ss_pad_o signals are generated automatically")
        else:
            self.ass = 0
            log.warning("Slave select signals are asserted and de-aserted by writing and clearing bits in SS register")
        self.update_ctrl()

    def update_ctrl(self):
        self.ctrl = (self.ass << 13) + (self.ie << 12) + (self.lsb << 11) + (self.tx_neg << 10) + (self.rx_neg << 9) + (
                self.go_busy << 8) + self.data_len
        log.debug("Control register is updated to: {:#010x}".format(self.ctrl))

    def w_data(self, data, chn):
        """Write to data reg"""
        if chn not in range(0, 8):
            raise ValueError('Unexpected chn number: {0}, should be 0-7'.format(chn))
        reg_name = "d" + chn
        self.w_reg(reg_name, data, is_pulse=False, go_dispatch=True)

    def r_data(self, chn):
        """Read to data reg"""
        if chn not in range(0, 8):
            raise ValueError('Unexpected chn number: {0}, should be 0-7'.format(chn))
        reg_name = "d" + str(chn)
        data_val = self.r_reg(reg_name)
        log.debug("SPI data register channel {:d} val: {:#010x}".format(chn, data_val))
        return data_val

    def w_ctrl(self, go_dispatch=True):
        """Write to Ctrl reg"""
        reg_name = "ctrl"
        self.w_reg(reg_name, self.ctrl, is_pulse=False, go_dispatch=go_dispatch)

    def r_ctrl(self):
        """Read ctrl reg"""
        reg_name = "ctrl"
        ctrl_val = self.r_reg(reg_name)
        log.debug("SPI control register is: {:#010x}".format(ctrl_val))
        return ctrl_val

    def w_div(self, divider, go_dispatch=True):
        """Write to divider reg"""
        reg_name = "divider"
        self.w_reg(reg_name, reg_val=divider, is_pulse=False, go_dispatch=go_dispatch)

    def r_div(self):
        """Write to divider reg"""
        reg_name = "divider"
        divider_val = self.r_reg(reg_name)
        log.debug("SPI clock divider val: {:d}".format(divider_val))
        return divider_val

    def w_ss(self, ss, go_dispatch=True):
        """Write to ss reg"""
        reg_name = "ss"
        self.w_reg(reg_name, reg_val=ss, is_pulse=False, go_dispatch=go_dispatch)

    def r_ss(self):
        """Write to ss reg"""
        reg_name = "ss"
        ss_val = self.r_reg(reg_name)
        log.debug("SPI ss val: {:d}".format(ss_val))
        return ss_val

    def start(self):
        self.set_go_busy()
        self.w_ctrl(go_dispatch=True)

    def w_data_regs(self, spi_data, go_dispatch=True):
        log.info("Writing SPI configuration data to SPI data registers...")
        for i in range(0, 8):
            reg_name = "d" + str(i)
            data = spi_data[i]
            self.w_reg(reg_name, reg_val=data, is_pulse=False, go_dispatch=go_dispatch)
            log.debug("Write d{:d} : {:#010x}".format(i, data))
