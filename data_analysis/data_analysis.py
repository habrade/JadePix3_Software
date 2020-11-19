#!/usr/bin/env python3

import coloredlogs
import logging

from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1D, TTree, TGraph
from ROOT import gROOT, gBenchmark, gRandom, gSystem

import numpy as np
from array import array

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)


class DataAnalysis:
    def __init__(self):
        self.data_file = "data/data.root"
        self.hfile = gROOT.FindObject(self.data_file)
        if self.hfile:
            self.hfile.Close()
        self.hfile = TFile(self.data_file, 'RECREATE', 'Data ROOT file')

        self.data_stream = 0
        self.root_tree = TTree('root_tree', 'Data_Stream')
        self.root_branch = self.root_tree.Branch('root_tree', self.data_stream, 'i')

        # Head couters
        self.head = 0
        self.fifo_status = 0
        self.rbof = 0

        # Data couters
        self.data = 0
        self.oc = 0
        self.ch0 = 0
        self.ch1 = 0
        self.ch2 = 0
        self.ch3 = 0
        self.data_cnt_list_ch0 = array('d')
        self.data_cnt_list_ch1 = array('d')
        self.data_cnt_list_ch2 = array('d')
        self.data_cnt_list_ch3 = array('d')
        self.frame_index_list = array('d')

        # Tail couters
        self.tail = 0
        self.frame_index = 0

        # rfifo overflow
        self.rfifo_oc = 0

        # Head Branch
        self.head_t = TTree("Frame_Head", "HEAD")
        self.head_branch = self.head_t.Branch("Frame_Head", self.head, 'i')
        self.fifo_status_t = TTree("FIFO_Status", "fifo_status")
        self.fifo_status_branch = self.fifo_status_t.Branch("FIFO_Status", self.fifo_status, 'i')
        self.rbof_t = TTree("RBOF", "rbof")
        self.rbof_branch = self.rbof_t.Branch("RBOF", self.rbof, 'i')

        # Tail Branch
        self.tail_t = TTree("Frame_Tail", "tail")
        self.tail_branch = self.tail_t.Branch("Frame_Tail", self.tail, 'i')
        self.frame_index_t = TTree("Frame_index", "frame_index")
        self.frame_index_branch = self.frame_index_t.Branch("Frame_index", self.frame_index, 'i')

        # Data Branch
        self.data_t = TTree("Frame_Data", "data")
        self.data_branch = self.data_t.Branch("Frame_Data", self.data, 'i')
        self.oc_t = TTree("OC", "oc")
        self.oc_branch = self.oc_t.Branch("OC", self.oc, 'i')
        self.ch0_t = TTree("CH0", "ch0")
        self.ch0_branch = self.ch0_t.Branch("CH0", self.ch0, 'i')
        self.ch1_t = TTree("CH1", "ch1")
        self.ch1_branch = self.ch1_t.Branch("CH1", self.ch1, 'i')
        self.ch2_t = TTree("CH2", "ch2")
        self.ch2_branch = self.ch2_t.Branch("CH2", self.ch2, 'i')
        self.ch3_t = TTree("CH3", "ch3")
        self.ch3_branch = self.ch3_t.Branch("CH3", self.ch3, 'i')

        # rfifo branch
        self.rfifo_oc_t = TTree("rfifo_oc", "rfifo_oc")
        self.rfifo_oc_branch = self.rfifo_oc_t.Branch("rfifo_oc", self.rfifo_oc, 'i')

        # histogrames
        self.h_data = TH1D("Data_Hist", "Data count in frame",
                           10000, 0, 10000)
        self.h_data_ch0 = TH1D("Data_CH0", "Channel 0 data count in frame",
                               10000, 0, 10000)
        self.h_data_ch1 = TH1D("Data_CH1", "Channel 1 data count in frame",
                               10000, 0, 10000)
        self.h_data_ch2 = TH1D("Data_CH2", "Channel 2 data count in frame",
                               10000, 0, 10000)
        self.h_data_ch3 = TH1D("Data_CH3", "Channel 3 data count in frame",
                               10000, 0, 10000)
        self.h_frame_index = TH1D("Frame_index", "Frame distribution",
                                  10000, 0, 10000)
        self.h_rfifo_oc = TH1D("rfifo_oc", "rfifo overflow in frame",
                               10000, 0, 10000)

        self.data_dist_g = TGraph(len(self.frame_index_list),
                             self.frame_index_list, self.data_cnt_list_ch0)

    def w_data(self, dataIn_arr):
        log.info("Start writing to .root file...")
        real_frame_index = 0
        for frame_data in dataIn_arr:
            data_stream = int(frame_data)
            self.root_tree.Fill()

            frame_type = (data_stream >> 23)
            if frame_type == 0:  # Tail
                tail = data_stream
                self.tail_t.Fill()
                frame_index = data_stream & 0x3FFFF
                self.h_frame_index.Fill(frame_index)
                self.frame_index_list.append(frame_index)
                self.data_cnt_list_ch0.append(self.ch0_branch.GetEntries())
                self.data_cnt_list_ch1.append(self.ch1_branch.GetEntries())
                self.data_cnt_list_ch2.append(self.ch2_branch.GetEntries())
                self.data_cnt_list_ch3.append(self.ch3_branch.GetEntries())
                self.frame_index_t.Fill()

            elif frame_type == 1:  # Head
                real_frame_index = frame_index + 1
                self.head = data_stream
                self.head_t.Fill()
                self.fifo_status = (data_stream >> 15) & 0xFF
                self.rbof = data_stream & 0x7FFF
                self.fifo_status_t.Fill()
                if self.rbof > 0:
                    self.rbof_t.Fill()

            elif frame_type == 2:  # Data
                data = data_stream
                self.data_t.Fill()
                self.h_data.Fill(real_frame_index)

                self.data_t.Fill()
                ch = (data_stream >> 16) & 0x3
                oc = (data_stream >> 18) & 0x1F
                if oc > 0:
                    self.oc_t.Fill()
                if ch == 0:  # Ch 0
                    self.ch0 = data_stream
                    self.h_data_ch0.Fill(real_frame_index)
                    self.ch0_t.Fill()
                elif ch == 1:  # Ch 1
                    self.ch1 = data_stream
                    self.h_data_ch1.Fill(real_frame_index)
                    self.ch1_t.Fill()
                elif ch == 2:  # Ch 2
                    self.ch2 = data_stream
                    self.h_data_ch2.Fill(real_frame_index)
                    self.ch2_t.Fill()
                elif ch == 3:  # Ch 3
                    self.ch3 = data_stream
                    self.h_data_ch3.Fill(real_frame_index)
                    self.ch3_t.Fill()

            elif frame_type == 3:  # rfifo overflow
                self.rfifo_oc = data_stream
                if self.rfifo_oc > 0:
                    self.rfifo_oc_t.Fill()

        # Graph
        # print("{:}, len: {:}".format(frame_index_list, len(frame_index_list)))
        # print("\n{:}, len: {:}".format(
            # data_cnt_list_ch0, len(data_cnt_list_ch0)))
        # data_dist_g = TGraph(283,frame_index_list,data_cnt_list_ch0)

        # Trees
        self.root_tree.Write()
        self.head_t.Write()
        self.fifo_status_t.Write()
        self.rbof_t.Write()
        self.oc_t.Write()
        self.data_t.Write()
        self.ch0_t.Write()
        self.ch1_t.Write()
        self.ch2_t.Write()
        self.ch3_t.Write()
        self.tail_t.Write()
        self.frame_index_t.Write()

        # Histograms
        self.h_data.Write()
        self.h_data.GetXaxis().SetTitle("Frame Index")

        self.h_data_ch0.Write()
        self.h_data_ch0.GetXaxis().SetTitle("Frame Index")
        self.h_data_ch1.Write()
        self.h_data_ch1.GetXaxis().SetTitle("Frame Index")
        self.h_data_ch2.Write()
        self.h_data_ch2.GetXaxis().SetTitle("Frame Index")
        self.h_data_ch3.Write()
        self.h_data_ch3.GetXaxis().SetTitle("Frame Index")
        self.h_frame_index.Write()
        self.h_frame_index.GetXaxis().SetTitle("Frame Index")

        # Graph
        self.data_dist_g.SetTitle("Data counter in Frame")
        self.data_dist_g.GetXaxis().SetTitle("Frame Index")
        self.data_dist_g.GetYaxis().SetTitle("Data Counters")
        self.data_dist_g.SetMarkerStyle(6)
        self.data_dist_g.SetLineColor(2)
        self.data_dist_g.SetMarkerColor(4)
        self.data_dist_g.Write()

        log.info("Write to .root end.")
