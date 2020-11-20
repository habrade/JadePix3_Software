import coloredlogs
import logging

from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1D, TH2D, TTree, TGraph
from ROOT import gROOT, gBenchmark, gRandom, gSystem

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

    data_stream = array("I", [0])
    # Head couters
    head = array("I", [0])
    fifo_status = array("I", [0])
    rbof = array("I", [0])

    # Data couters
    data = array("I", [0])
    oc = array("I", [0])
    ch0 = array("I", [0])
    ch1 = array("I", [0])
    ch2 = array("I", [0])
    ch3 = array("I", [0])

    # Tail couters
    tail = array("I", [0])
    frame_index = array("I", [0])

    # rfifo overflow
    rfifo_oc = array("I", [0])

    # Head Branch
    head_t = TTree("Frame_Head", "HEAD")
    head_t.Branch("Frame_Head", head, 'Frame_Index/i')
    fifo_status_t = TTree("FIFO_Status", "fifo_status")
    fifo_status_t.Branch("FIFO_Status", fifo_status, 'FIFO_Status/i')
    rbof_t = TTree("RBOF", "rbof")
    rbof_t.Branch("RBOF", rbof, 'RBOF/i')

    # Tail Branch
    tail_t = TTree("Frame_Tail", "tail")
    tail_t.Branch("Frame_Tail", tail, 'Frame_Tail/i')
    frame_index_t = TTree("Frame_index", "frame_index")
    frame_index_t.Branch("Frame_index", frame_index, 'Frame_index/i')

    # Data Branch
    data_t = TTree("Frame_Data", "data")
    data_t.Branch("Frame_Data", data, 'Frame_Data/i')
    ch0_t = TTree("CH0", "ch0")
    ch0_t.Branch("CH0", ch0, 'CH0/i')
    ch1_t = TTree("CH1", "ch1")
    ch1_t.Branch("CH1", ch1, 'CH1/i')
    ch2_t = TTree("CH2", "ch2")
    ch2_t.Branch("CH2", ch2, 'CH2/i')
    ch3_t = TTree("CH3", "ch3")
    ch3_t.Branch("CH3", ch3, 'CH3/i')

    # rfifo branch
    rfifo_oc_t = TTree("rfifo_oc", "rfifo_oc")
    rfifo_oc_t.Branch("rfifo_oc", rfifo_oc, 'rfifo_oc/i')

    # histogrames
    h_data = TH1D("Data_Hist", "Data count in frame", 10000, 0, 10000)
    h_data_ch0 = TH1D("Data_CH0", "Channel 0 data count in frame", 10000, 0, 10000)
    h_data_ch1 = TH1D("Data_CH1", "Channel 1 data count in frame", 10000, 0, 10000)
    h_data_ch2 = TH1D("Data_CH2", "Channel 2 data count in frame", 10000, 0, 10000)
    h_data_ch3 = TH1D("Data_CH3", "Channel 3 data count in frame", 10000, 0, 10000)
    h_frame_index = TH1D("Frame_Num", "Frame distribution", 10000, 0, 10000)

    h_data_in_frame = TH2D("Data_Quantity", "Data quantity in frame", 10000, 0, 10000, 10000, 0, 10000*512)
    h_oc_in_frame = TH2D("OC_Quantity", "OC quantity in frame", 10000, 0, 10000, 10000, 0, 10000*512)
    h_rbof_in_frame = TH2D("RBOF_Quantity", "RBOF quantity in frame", 10000, 0, 10000, 10000, 0, 10000*512)

    real_frame_index = array("I", [0])

    data_in_t.Print()
    for event in data_in_t:
        data_stream = event.data
        frame_type = (data_stream >> 23)
        if frame_type == 0:  # Tail
            tail[0] = data_stream
            tail_t.Fill()
            frame_index[0] = data_stream & 0x3FFFF
            h_frame_index.Fill(frame_index[0])
            frame_index_t.Fill()
            h_data_in_frame.Fill(frame_index[0], ch0_t.GetEntries())

        elif frame_type == 1:  # Head
            real_frame_index[0] = frame_index[0] + 1
            head[0] = data_stream
            head_t.Fill()
            fifo_status[0] = (data_stream >> 15) & 0xFF
            rbof[0] = data_stream & 0x7FFF
            fifo_status_t.Fill()
            h_rbof_in_frame.Fill(real_frame_index[0], rfifo_oc[0])
            # if rbof[0] > 0:
            #     rbof_t.Fill()

        elif frame_type == 2:  # Data
            data[0] = data_stream
            data_t.Fill()
            h_data.Fill(real_frame_index[0])
            ch = (data_stream >> 16) & 0x3
            oc[0] = (data_stream >> 18) & 0x1F
            h_oc_in_frame.Fill(real_frame_index[0], oc[0])

            if ch == 0:  # Ch 0
                ch0[0] = data_stream
                h_data_ch0.Fill(real_frame_index[0])
                ch0_t.Fill()
            elif ch == 1:  # Ch 1
                ch1[0] = data_stream
                h_data_ch1.Fill(real_frame_index[0])
                ch1_t.Fill()
            elif ch == 2:  # Ch 2
                ch2[0] = data_stream
                h_data_ch2.Fill(real_frame_index[0])
                ch2_t.Fill()
            elif ch == 3:  # Ch 3
                ch3[0] = data_stream
                h_data_ch3.Fill(real_frame_index[0])
                ch3_t.Fill()

        elif frame_type == 3:  # rfifo overflow
            rfifo_oc[0] = data_stream
            if rfifo_oc[0] > 0:
                rfifo_oc_t.Fill()

    hfile.Close()

    # Histograms
    h_data.GetXaxis().SetTitle("Frame Index")

    h_data_ch0.GetXaxis().SetTitle("Frame Index")
    h_data_ch1.GetXaxis().SetTitle("Frame Index")
    h_data_ch2.GetXaxis().SetTitle("Frame Index")
    h_data_ch3.GetXaxis().SetTitle("Frame Index")
    h_frame_index.GetXaxis().SetTitle("Frame Index")

    dfile.Write()
    dfile.Close()
    log.info("Drawing plots end.")


if __name__ == "__main__":
    data_file = "data/data.root"
    draw_data(data_file)
