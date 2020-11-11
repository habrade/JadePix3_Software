import time

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

    def send_slow_ctrl_cmd(self, reg_name_base, fifo_name, cmd):
        for i in range(len(cmd)):
            self._hw.getNode(reg_name_base + fifo_name + ".WFIFO_DATA").write(cmd[i])
            self._hw.dispatch()
            valid_len = 0
            while valid_len != 1:
                valid_len = self._hw.getNode(reg_name_base + fifo_name + ".WVALID_LEN").read()
                self._hw.dispatch()
                valid_len = valid_len & 0x7fffffff
            print("Slow ctrl cmd {:#08x} has been sent".format(cmd[i]))
            time.sleep(0.2)
            
    def read_ipb_data_fifo(self, reg_name_base, fifo_name, num):
        left = num
        mem = []
        while left > 0:
            read_len = self._hw.getNode(reg_name_base + fifo_name + ".RFIFO_LEN").read()
            self._hw.dispatch()
            # time.sleep(0.01)
            if read_len == 0:
                continue
            read_len = min(left, int(read_len))
            mem0 = self._hw.getNode(reg_name_base + fifo_name + ".RFIFO_DATA").readBlock(read_len)
            self._hw.dispatch()
            #      print read_len
            mem.extend(mem0)
            left = left - read_len
        return mem
