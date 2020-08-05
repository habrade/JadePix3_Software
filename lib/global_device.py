import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class GlobalDevice:
    def __init__(self, hw):
        self.hw = hw
        self.reg_name_base = "global_dev."
        log.info("Gloabl device")

    def set_bit(self, reg):
        reg_name = self.reg_name_base + reg
        node = self.hw.getNode(reg_name)
        node.write(0)
        node.write(1)
        node.write(0)
        self.hw.dispatch()
        return True

    def set_nuke(self):
        return self.set_bit("nuke")

    def set_soft_rst(self):
        return self.set_bit("soft_rst")