import coloredlogs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class GlobalDevice:
    def __init__(self, ipbus_link):
        self._ipbus_link = ipbus_link
        self.reg_name_base = "global_dev."

    def set_bit(self, reg_name):
        self._ipbus_link.w_reg(self.reg_name_base, reg_name, 0, is_pulse=True, go_dispatch=True)

    def set_nuke(self):
        return self.set_bit("nuke")

    def set_soft_rst(self):
        return self.set_bit("soft_rst")
