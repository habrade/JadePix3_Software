#!/usr/bin/env python3
import time
import logging

import coloredlogs

from lib.global_device import GlobalDevice
from lib.dac70004_device import Dac70004Device
from lib.dac70004_defs import *
from lib.ipbus_link import IPbusLink
from lib.jadepix_device import JadePixDevice

from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH2F, TTree
from ROOT import gROOT, gBenchmark, gRandom, gSystem

import numpy as np

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)

__author__ = "Sheng Dong"
__email__ = "s.dong@mails.ccnu.edu.cn"

if __name__ == '__main__':
    ipbus_link = IPbusLink()

    jadepix_dev = JadePixDevice(ipbus_link)
    global_dev = GlobalDevice(ipbus_link)
    dac70004_dev = Dac70004Device(ipbus_link)

    # Soft global reset
    global_dev.set_soft_rst()

    # DAC70004 Config
    dac70004_dev.soft_reset()
    dac70004_dev.soft_clr()
    dac70004_dev.w_power_chn(DAC70004_PW_UP, 0xf)  # Power up all channels
    dac70004_dev.w_ana_chn_update_chn(
        DAC70004_CHN_A, 1.5)  # Set channle A to 1.5V
    dac70004_dev.w_ana_chn_update_chn(
        DAC70004_CHN_B, 2.0)  # Set channle B to 2.0V

    # SPI master config
    jadepix_dev.reset_spi()
    jadepix_dev.set_spi(data_len=200, ie=False, ass=True,
                        lsb=False, rx_neg=False, tx_neg=True, div=0, ss=0x01)
    # Set JadePix SPI configuration
    jadepix_dev.start_spi_config()
    # Load Config
    jadepix_dev.load_config_soft()

    # JadePix Control

    """ From here we can test configuration """
    # start = time.process_time()
    # jadepix_dev.w_cfg()
    # jadepix_dev.start_cfg(go_dispatch=True)
    # print("It takes {:} secends to write configurations to FIFO".format(time.process_time() - start))
    #
    # time.sleep(20)

    """ From here we can test rolling shutter """
    jadepix_dev.set_gs_plse(is_dplse=True)
    jadepix_dev.rs_config(cache_bit=0xf, hitmap_col_low=340,
                          hitmap_col_high=341, hitmap_en=False, frame_number=100000)
    jadepix_dev.start_rs()
    # time.sleep(2)

    """From here we can test global shutter """
    """sys_clk period = 12 ns, so width = Number * Period"""
    """For pulse width, width = (high<<32 + low) * Period"""
    """Will change to real time later"""
    # jadepix_dev.gs_config(pulse_delay=4, width_low=3, width_high=0, pulse_deassert=2, deassert=5, col=224)
    # jadepix_dev.start_gs()

    rfifo_depth_width = 17
    rfifo_depth = pow(2, rfifo_depth_width)
    data_file = "data/data.root"
    hfile = gROOT.FindObject(data_file)
    if hfile:
        hfile.Close()
    hfile = TFile(data_file, 'RECREATE', 'Data ROOT file')

    slice_size = rfifo_depth
    dataIn_array = np.empty(slice_size, dtype=np.uint32, order='F')
    # log.info("The number (word, 32bits) of data wanted: {:d}".format(slice_size))

    # remove data file before taking data
    num_token = 2
    data_amount = num_token * slice_size * 32

    tree = TTree('new_tree', 'Main_tree')

    # Head couters
    head = 0
    fifo_status = 0
    rbof = 0

    # Data couters
    data = 0
    oc = 0
    # blk_sel = 0
    ch0 = 0
    ch1 = 0
    ch2 = 0
    ch3 = 0

    # Tail couters
    tail = 0
    frame_index = 0

    # Head Branch
    head_branch = tree.Branch("Frame_Head", head, "num_of_head/i")
    fifo_status_branch = tree.Branch("FIFO_Status", fifo_status, "num_fifo_status/i")
    rbof_branch = tree.Branch("RBOF", rbof, "rbof/i")

    # Tail Branch
    tail_branch = tree.Branch("Frame_Tail", tail, "num_of_tail/i")
    frame_index_branch = tree.Branch("Frame_index", frame_index, "num_frame_index/i")

    # Data Branch
    data_branch = tree.Branch("Frame_Data", data, "num_of_data/i")
    oc_branch = tree.Branch("OC", oc, "num_oc/i")
    # blk_sel_branch = tree.Branch(data_branch, "blk_sel", 'i4')
    ch0_branch = tree.Branch("CH0", ch0, "num_ch0/i")
    ch1_branch = tree.Branch("CH1", ch1, "num_ch1/i")
    ch2_branch = tree.Branch("CH2", ch2, "num_ch2/i")
    ch3_branch = tree.Branch("CH3", ch3, "num_ch3/i")

    # Get Data Stream
    start = time.process_time()
    for i in range(num_token):
        dataIn_array = jadepix_dev.read_ipb_data_fifo(slice_size)

        for frame_data in dataIn_array:
            frame_type = (frame_data >> 23)

            if frame_type == 0:  # Tail
                frame_index = frame_data
                frame_index_branch.Fill()

            elif frame_type == 1:  # Head
                fifo_status = (frame_data >> 15) & 0xFF
                rbof = frame_data & 0x7FFF
                fifo_status_branch.Fill()
                rbof_branch.Fill()

            elif frame_type == 2:  # Data
                tree.Fill()
                ch = (frame_data >> 16) & 0x3
                oc = (frame_data >> 18) & 0x1F
                oc_branch.Fill()
                if ch == 0:  # Ch 0
                    ch0_branch.Fill()
                elif ch == 1:  # Ch 1
                    ch1_branch.Fill()
                elif ch == 2:  # Ch 2
                    ch2_branch.Fill()
                elif ch == 3:  # Ch 3
                    ch3_branch.Fill()

            elif frame_type == 3:  # Error
                tree.Fill()
                pass
        # del mem
    tree.Write()

    trans_time = time.process_time() - start
    trans_speed = int(data_amount / trans_time)  # Unit: bps
    log.info("Transfer time: {:f} s".format(trans_time))
    log.info("Transfer speed: {:f} Mbps".format(trans_speed/pow(10, 6)))
    # file_handler.close()
