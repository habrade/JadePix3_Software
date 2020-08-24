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
    def __init__(self, hw):
        self.hw = hw
        self.reg_name_base = "spi_dev."

        self.char_len = 0
        self.go_busy = 0
        self.rx_neg = 0
        self.tx_neg = 0
        self.lsb = 0
        self.ie = 0
        self.ass = 1

        self.ctrl = 0x00000000

    def set_char_len(self, char_len):
        if char_len not in range(0, 256):
            raise ValueError('Unexpected char_len number: {0}, should be less than 256'.format(char_len))
        self.char_len = char_len
        log.debug("Set how many bits are transmitted in one transfer: {}".format(char_len))
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

    def set_go_busy(self, enabled):
        if not isinstance(enabled, bool):
            raise ValueError('Unexpected parameter, it must be boolean: {}'.format(enabled))
        if enabled:
            self.go_busy = 1
            log.debug("Starts the transfer")
        else:
            self.go_busy = 0
            log.warning("Writing 0 to this bit has no effect")
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
            log.warning("Writing 0 to this bit has no effect")
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
                self.go_busy << 8) + self.char_len
        log.debug("Control register is updated to: {:#010x}".format(self.ctrl))

    def w_data(self, data, chn):
        ## Write to data reg
        if chn not in range(0, 8):
            raise ValueError('Unexpected chn number: {0}, should be 0-7'.format(chn))
        reg_name = "d" + chn
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(data)
        self.hw.dispatch()

    def r_data(self, chn):
        ## Read to data reg
        if chn not in range(0, 8):
            raise ValueError('Unexpected chn number: {0}, should be 0-7'.format(chn))
        reg_name = "d" + chn
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        data = node.read()
        self.hw.dispatch()
        return data

    def w_ctrl(self):
        ## Write to Ctrl reg
        reg_name = "ctrl"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(self.ctrl)
        self.hw.dispatch()

    def r_ctrl(self):
        ## Write to Ctrl reg
        reg_name = "ctrl"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        ctrl = node.read()
        self.hw.dispatch()
        return ctrl

    def w_div(self, divider):
        ## Write to divider reg
        reg_name = "divider"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(divider)
        self.hw.dispatch()

    def r_div(self):
        ## Write to divider reg
        reg_name = "divider"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        divider = node.read()
        self.hw.dispatch()
        return divider

    def w_ss(self, ss):
        ## Write to ss reg
        reg_name = "ss"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(ss)
        self.hw.dispatch()

    def r_ss(self):
        ## Write to ss reg
        reg_name = "ss"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        ss = node.read()
        self.hw.dispatch()
        return ss
