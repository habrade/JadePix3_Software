import uhal
import coloredlogs
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"


class IPbusLink:
    def __init__(self):
        self.device_ip = "192.168.3.17"
        self.device_uri = "ipbusudp-2.0://" + self.device_ip + ":50001"
        self.address_table_name = "etc/address.xml"
        self.address_table_uri = "file://" + self.address_table_name
        self._hw = self.get_hw()

    def get_hw(self):
        uhal.setLogLevelTo(uhal.LogLevel.INFO)
        hw = uhal.getDevice("JadePix3.udp.0", self.device_uri, self.address_table_uri)
        return hw

    def w_reg(self, reg_name_base, reg_name, reg_val, is_pulse, go_dispatch=True):
        node_name = reg_name_base + reg_name
        node = self._hw.getNode(node_name)
        if is_pulse:
            node.write(0)
            node.write(1)
            node.write(0)
        else:
            node.write(reg_val)
        if go_dispatch:
            self._hw.dispatch()

    def r_reg(self, reg_name_base, reg_name):
        node_name = reg_name_base + reg_name
        node = self._hw.getNode(node_name)
        ret = node.read()
        self._hw.dispatch()
        ret_val = ret.value()
        return ret_val
