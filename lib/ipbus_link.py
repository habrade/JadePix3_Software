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
        self.device_ip = "192.168.3.18"
        # self.device_uri = "chtcp-2.0://localhost:10203?target=192.168.3.18:50001"
        # < connection id = "JadePix3.udp.0" uri = "chtcp-2.0://localhost:10203?target=127.0.0.1:50001" address_table = "file://address.xml" / >
        self.device_uri = "ipbusudp-2.0://" + self.device_ip + ":50001"
        self.address_table_name = "etc/address.xml"
        self.address_table_uri = "file://" + self.address_table_name
        self._hw = self.get_hw()
        # self._hw.setTimeoutPeriod(1000)
        log.info("IPbus timeout period: {:}".format(self._hw.getTimeoutPeriod()))

        self._quit_reading = False

    def get_hw(self):
        """

        :return: IPbus Device
        """
        # uhal.setLogLevelTo(uhal.LogLevel.DEBUG)
        uhal.disableLogging()
        hw = uhal.getDevice("JadePix3.udp.0", self.device_uri, self.address_table_uri)
        return hw

    def w_reg(self, reg_name_base, reg_name, reg_val, is_pulse, go_dispatch=True):
        """

        :param reg_name_base: Register name base, usually device name.
        :param reg_name: Register name.
        :param reg_val: Value be to send.
        :param is_pulse: Whether generate pulse.
        :param go_dispatch: Whether send this command. Defalut = True
        :return: None
        """
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
        """

        :param reg_name_base:
        :param reg_name:
        :return:
        """
        node_name = reg_name_base + reg_name
        node = self._hw.getNode(node_name)
        ret = node.read()
        self._hw.dispatch()
        ret_val = ret.value()
        return ret_val

    def send_slow_ctrl_cmd(self, reg_name_base, fifo_name, cmd):
        """

        :param reg_name_base:
        :param fifo_name:
        :param cmd:
        :return:
        """
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

    def write_ipb_slow_ctrl_fifo(self, reg_name_base, fifo_name, data_list):
        """

        :param reg_name_base:
        :param fifo_name:
        :param data_list:
        :return:
        """
        self._hw.getNode(reg_name_base + fifo_name + ".WFIFO_DATA").writeBlock(data_list)

    def read_ipb_data_fifo(self, reg_name_base, fifo_name, num, safe_mode):
        """

        :param reg_name_base:
        :param fifo_name:
        :param num:
        :param safe_mode: True: safe read data from FIFO. False: Just read, error may happen, but the speed is fast!
        :param try_time: how many times to try to read
        :return:
        """
        mem = []
        if safe_mode:
            read_len = self._hw.getNode(reg_name_base + fifo_name + ".RFIFO_LEN").read()
            self._hw.dispatch()
            mem = self._hw.getNode(reg_name_base + fifo_name + ".RFIFO_DATA").readBlock(read_len)
            self._hw.dispatch()
            return mem
        else:
            try:
                mem = self._hw.getNode(reg_name_base + fifo_name + ".RFIFO_DATA").readBlock(num)
                self._hw.dispatch()
                return mem
            except KeyboardInterrupt:
                raise


