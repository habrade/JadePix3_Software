#!/usr/bin/env python3

import coloredlogs
import logging

from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1D, TTree
from ROOT import gROOT, gBenchmark, gRandom, gSystem

import numpy as np

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)


class DataAnalysis:
    def __init__(self, dataIn_array):
        self._dataIn_array = dataIn_array
        self.data_file = "data/data.root"
        self.hfile = gROOT.FindObject(self.data_file)
        if self.hfile:
            self.hfile.Close()
        self.hfile = TFile(self.data_file, 'RECREATE', 'Data ROOT file')

    def w_data(self):
        data_stream = 0
        root_tree = TTree('root_tree', 'Data_Stream')
        root_branch = root_tree.Branch('root_tree', data_stream, 'i')

        # Head couters
        head = 0
        fifo_status = 0
        rbof = 0

        # Data couters
        data = 0
        oc = 0
        ch0 = 0
        ch1 = 0
        ch2 = 0
        ch3 = 0

        # Tail couters
        tail = 0
        frame_index = 0

        # rfifo overflow
        rfifo_oc = 0

        # Head Branch
        head_t = TTree("Frame_Head", "HEAD")
        head_branch = head_t.Branch("Frame_Head", head, 'i')
        fifo_status_t = TTree("FIFO_Status", "fifo_status")
        fifo_status_branch = fifo_status_t.Branch(
            "FIFO_Status", fifo_status, 'i')
        rbof_t = TTree("RBOF", "rbof")
        rbof_branch = rbof_t.Branch("RBOF", rbof, 'i')

        # Tail Branch
        tail_t = TTree("Frame_Tail", "tail")
        tail_branch = tail_t.Branch("Frame_Tail", tail, 'i')
        frame_index_t = TTree("Frame_index", "frame_index")
        frame_index_branch = frame_index_t.Branch(
            "Frame_index", frame_index, 'i')

        # Data Branch
        data_t = TTree("Frame_Data", "data")
        data_branch = data_t.Branch("Frame_Data", data, 'i')
        oc_t = TTree("OC", "oc")
        oc_branch = oc_t.Branch("OC", oc, 'i')
        ch0_t = TTree("CH0", "ch0")
        ch0_branch = ch0_t.Branch("CH0", ch0, 'i')
        ch1_t = TTree("CH1", "ch1")
        ch1_branch = ch1_t.Branch("CH1", ch1, 'i')
        ch2_t = TTree("CH2", "ch2")
        ch2_branch = ch2_t.Branch("CH2", ch2, 'i')
        ch3_t = TTree("CH3", "ch3")
        ch3_branch = ch3_t.Branch("CH3", ch3, 'i')

        # rfifo branch
        rfifo_oc_t = TTree("rfifo_oc", "rfifo_oc")
        rfifo_oc_branch = rfifo_oc_t.Branch("rfifo_oc", rfifo_oc, 'i')

        # histogrames
        h_data = TH1D("Data_Hist", "Data amount in each frame",
                      200, 0.0, 200.0)
        h_data_ch0 = TH1D("Data_CH0", "Channel 0 data amount in each frame",
                      200, 0.0, 200.0)
        h_data_ch1 = TH1D("Data_CH1", "Channel 1 data amount in each frame",
                      200, 0.0, 200.0)
        h_data_ch2 = TH1D("Data_CH2", "Channel 2 data amount in each frame",
                      200, 0.0, 200.0)
        h_data_ch3 = TH1D("Data_CH3", "Channel 3 data amount in each frame",
                      200, 0.0, 200.0)

        log.info("Start writing to .root file...")
        for frame_data in self._dataIn_array:
            data_stream = frame_data
            root_tree.Fill()

            frame_type = (frame_data >> 23)
            if frame_type == 0:  # Tail
                tail = frame_data
                tail_t.Fill()
                frame_index = frame_data & 0x3FFFF
                frame_index_t.Fill()

            elif frame_type == 1:  # Head
                head = frame_data
                head_t.Fill()
                fifo_status = (frame_data >> 15) & 0xFF
                rbof = frame_data & 0x7FFF
                fifo_status_t.Fill()
                if rbof > 0:
                    rbof_t.Fill()

            elif frame_type == 2:  # Data
                data = frame_data
                data_t.Fill()
                h_data.Fill(tail_branch.GetEntries())
                data_t.Fill()
                ch = (frame_data >> 16) & 0x3
                oc = (frame_data >> 18) & 0x1F
                if oc > 0:
                    oc_t.Fill()
                if ch == 0:  # Ch 0
                    ch0 = frame_data
                    h_data_ch0.Fill(tail_branch.GetEntries())
                    ch0_t.Fill()
                elif ch == 1:  # Ch 1
                    ch1 = frame_data
                    h_data_ch1.Fill(tail_branch.GetEntries())
                    ch1_t.Fill()
                elif ch == 2:  # Ch 2
                    ch2 = frame_data
                    h_data_ch2.Fill(tail_branch.GetEntries())
                    ch2_t.Fill()
                elif ch == 3:  # Ch 3
                    ch3 = frame_data
                    h_data_ch3.Fill(tail_branch.GetEntries())
                    ch3_t.Fill()

            elif frame_type == 3:  # rfifo overflow
                rfifo_oc = frame_data
                if rfifo_oc > 0:
                    rfifo_oc_t.Fill()

        root_tree.Write()
        head_t.Write()
        fifo_status_t.Write()
        rbof_t.Write()
        oc_t.Write()
        data_t.Write()
        ch0_t.Write()
        ch1_t.Write()
        ch2_t.Write()
        ch3_t.Write()
        tail_t.Write()
        frame_index_t.Write()
        h_data.Write()
        h_data_ch0.Write()
        h_data_ch1.Write()
        h_data_ch2.Write()
        h_data_ch3.Write()

        del self._dataIn_array
        log.info("Write to .root end.")
