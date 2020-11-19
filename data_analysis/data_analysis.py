import coloredlogs
import logging

import sys

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

def draw_data(data_file):
    log.info("Start drawing plots...")
    hfile = TFile.Open(data_file)
    data_in_t = hfile.Get("root_tree")

    drawing_file = "data/drawing.root"
    dfile = gROOT.FindObject(drawing_file)
    if dfile:
        dfile.Close()
    dfile = TFile(drawing_file, 'RECREATE', 'Drawing plots')

    data_stream = 0
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
    data_cnt_list_ch0 = array('d')
    data_cnt_list_ch1 = array('d')
    data_cnt_list_ch2 = array('d')
    data_cnt_list_ch3 = array('d')
    frame_index_list = array('d')

    # Tail couters
    tail = 0
    frame_index = 0

    # rfifo overflow
    rfifo_oc = 0

    # Head Branch
    head_t = TTree("Frame_Head", "HEAD")
    head_branch = head_t.Branch("Frame_Head", head, 'i')
    fifo_status_t = TTree("FIFO_Status", "fifo_status")
    fifo_status_branch = fifo_status_t.Branch("FIFO_Status", fifo_status, 'i')
    rbof_t = TTree("RBOF", "rbof")
    rbof_branch = rbof_t.Branch("RBOF", rbof, 'i')

    # Tail Branch
    tail_t = TTree("Frame_Tail", "tail")
    tail_branch = tail_t.Branch("Frame_Tail", tail, 'i')
    frame_index_t = TTree("Frame_index", "frame_index")
    frame_index_branch = frame_index_t.Branch("Frame_index", frame_index, 'i')

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
    h_data = TH1D("Data_Hist", "Data count in frame",
                  10000, 0, 10000)
    h_data_ch0 = TH1D("Data_CH0", "Channel 0 data count in frame",
                      10000, 0, 10000)
    h_data_ch1 = TH1D("Data_CH1", "Channel 1 data count in frame",
                      10000, 0, 10000)
    h_data_ch2 = TH1D("Data_CH2", "Channel 2 data count in frame",
                      10000, 0, 10000)
    h_data_ch3 = TH1D("Data_CH3", "Channel 3 data count in frame",
                      10000, 0, 10000)
    h_frame_index = TH1D("Frame_index", "Frame distribution",
                         10000, 0, 10000)
    h_rfifo_oc = TH1D("rfifo_oc", "rfifo overflow in frame",
                      10000, 0, 10000)

    real_frame_index = 0

    data_in_t.Print()
    for event in data_in_t:
        data_stream = int(event.data)
        # print(str(data_stream))

        frame_type = (data_stream >> 23)
        if frame_type == 0:  # Tail
            tail = data_stream
            tail_t.Fill()
            frame_index = data_stream & 0x3FFFF
            h_frame_index.Fill(frame_index)
            frame_index_list.append(frame_index)
            data_cnt_list_ch0.append(ch0_branch.GetEntries())
            data_cnt_list_ch1.append(ch1_branch.GetEntries())
            data_cnt_list_ch2.append(ch2_branch.GetEntries())
            data_cnt_list_ch3.append(ch3_branch.GetEntries())
            frame_index_t.Fill()

        elif frame_type == 1:  # Head
            real_frame_index = frame_index + 1
            head = data_stream
            head_t.Fill()
            fifo_status = (data_stream >> 15) & 0xFF
            rbof = data_stream & 0x7FFF
            fifo_status_t.Fill()
            if rbof > 0:
                rbof_t.Fill()

        elif frame_type == 2:  # Data
            data = data_stream
            data_t.Fill()
            h_data.Fill(real_frame_index)

            data_t.Fill()
            ch = (data_stream >> 16) & 0x3
            oc = (data_stream >> 18) & 0x1F
            if oc > 0:
                oc_t.Fill()
            if ch == 0:  # Ch 0
                ch0 = data_stream
                h_data_ch0.Fill(real_frame_index)
                ch0_t.Fill()
            elif ch == 1:  # Ch 1
                ch1 = data_stream
                h_data_ch1.Fill(real_frame_index)
                ch1_t.Fill()
            elif ch == 2:  # Ch 2
                ch2 = data_stream
                h_data_ch2.Fill(real_frame_index)
                ch2_t.Fill()
            elif ch == 3:  # Ch 3
                ch3 = data_stream
                h_data_ch3.Fill(real_frame_index)
                ch3_t.Fill()

        elif frame_type == 3:  # rfifo overflow
            rfifo_oc = data_stream
            if rfifo_oc > 0:
                rfifo_oc_t.Fill()
        
    # hfile.Close()

    # Graph
    # print("{:}, len: {:}".format(frame_index_list, len(frame_index_list)))
    # print("\n{:}, len: {:}".format(
        # data_cnt_list_ch0, len(data_cnt_list_ch0)))
    # data_dist_g = TGraph(283,frame_index_list,data_cnt_list_ch0)

    # Trees
    # root_tree.Write()
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

    # Histograms
    h_data.Write()
    h_data.GetXaxis().SetTitle("Frame Index")

    h_data_ch0.Write()
    h_data_ch0.GetXaxis().SetTitle("Frame Index")
    h_data_ch1.Write()
    h_data_ch1.GetXaxis().SetTitle("Frame Index")
    h_data_ch2.Write()
    h_data_ch2.GetXaxis().SetTitle("Frame Index")
    h_data_ch3.Write()
    h_data_ch3.GetXaxis().SetTitle("Frame Index")
    h_frame_index.Write()
    h_frame_index.GetXaxis().SetTitle("Frame Index")

    # Graph
    # data_dist_g = TGraph(len(frame_index_list),
    #                      frame_index_list, data_cnt_list_ch0)

    # data_dist_g.SetTitle("Data counter in Frame")
    # data_dist_g.GetXaxis().SetTitle("Frame Index")
    # data_dist_g.GetYaxis().SetTitle("Data Counters")
    # data_dist_g.SetMarkerStyle(6)
    # data_dist_g.SetLineColor(2)
    # data_dist_g.SetMarkerColor(4)
    # data_dist_g.Write()

    log.info("Drawing plots end.")

if __name__ == "__main__":
    data_file = "data/data.root"
    draw_data(data_file)
