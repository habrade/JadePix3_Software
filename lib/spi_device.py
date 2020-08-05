import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class SpiDevice:
    def __init__(self, hw):
        self.hw = hw
        self.reg_name_base = "spi_dev."

    def w_data(self, data, chn):
        ## Write to data reg
        if chn > 3 or chn < 0:
            raise ValueError('Unexpected chn number: {0}, should be 0-3'.format(chn))
        reg_name = "d" + chn
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(data)
        self.hw.dispatch()

    def r_data(self, chn):
        ## Read to data reg
        if chn > 3 or chn < 0:
            raise ValueError('Unexpected chn number: {0}, should be 0-3'.format(chn))
        reg_name = "d" + chn
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        data = node.read()
        self.hw.dispatch()
        return data

    def w_ctrl(self, ctrl):
        ## Write to Ctrl reg
        reg_name = "ctrl"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(ctrl)
        self.hw.dispatch()

    def r_ctrl(self):
        ## Write to Ctrl reg
        reg_name = "ctrl"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        ctrl = node.read()
        self.hw.dispatch()
        return ctrl

    def w_divider(self, divider):
        ## Write to divider reg
        reg_name = "divider"
        node_name = self.reg_name_base + reg_name
        node = self.hw.getNode(node_name)
        node.write(divider)
        self.hw.dispatch()

    def r_divider(self):
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