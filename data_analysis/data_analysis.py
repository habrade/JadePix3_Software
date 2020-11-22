import coloredlogs
import logging

import ROOT

from array import array

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)


def draw_data(data_file):
    log.info("Start drawing plots...")

    ## Going parallel
    ROOT.EnableImplicitMT()

    drawing_file = "data/drawing.root"
    dfile = ROOT.gROOT.FindObject(drawing_file)
    if dfile:
        dfile.Close()
    dfile = ROOT.TFile(drawing_file, 'RECREATE', 'Drawing plots')

    ## Try DataFrame
    df = ROOT.RDataFrame("root_tree", data_file)
    d_valid = df.Filter("data < 0x1FFFFFF")

    d_dummy_data = d_valid.Filter("(data >> 25) > 0").Define("dummy_data", "data")
    d_head = d_valid.Filter("(data >> 23) == 1").Define("head", "data")

    d_fifo_status = d_head.Filter("(data >> 23) == 1").Define("fifo_status", "(head >> 15) & 0xFF").Define(
        "fifo_status_ch0", "(fifo_status & 0xc0)").Define("fifo_status_ch1", "(fifo_status & 0x30)").Define(
        "fifo_status_ch2", "(fifo_status & 0x0c)").Define("fifo_status_ch3", "(fifo_status & 0x03)")
    d_rbof = d_head.Filter("(data >> 23) == 1").Define("rbof", "head & 0x7FFF").Filter("rbof > 0 ")
    d_tail = d_valid.Filter("(data >> 23) == 0").Define("tail", "data")
    d_ch_data = d_valid.Filter("(data >> 23) == 2").Define("ch_data", "data").Define("fifo_oc",
                                                                                     "((ch_data >> 18) & 0x1F)")

    d_ch0_data = d_ch_data.Filter("((ch_data >> 16) & 0x3 ) == 0").Define("ch0_data", "(ch_data & 0xFFFF)")
    d_ch1_data = d_ch_data.Filter("((ch_data >> 16) & 0x3 ) == 1").Define("ch1_data", "(ch_data & 0xFFFF)")
    d_ch2_data = d_ch_data.Filter("((ch_data >> 16) & 0x3 ) == 2").Define("ch2_data", "(ch_data & 0xFFFF)")
    d_ch3_data = d_ch_data.Filter("((ch_data >> 16) & 0x3 ) == 3").Define("ch3_data", "(ch_data & 0xFFFF)")

    h_stream = d_valid.Histo1D("data")
    h_dummy_data = d_dummy_data.Histo1D("dummy_data")
    h_head = d_head.Histo1D("head")
    h_fifo_satus = d_fifo_status.Histo1D("fifo_status")
    h_fifo_satus_ch0 = d_fifo_status.Histo1D("fifo_status_ch0")
    h_fifo_satus_ch1 = d_fifo_status.Histo1D("fifo_status_ch1")
    h_fifo_satus_ch2 = d_fifo_status.Histo1D("fifo_status_ch2")
    h_fifo_satus_ch3 = d_fifo_status.Histo1D("fifo_status_ch3")
    h_rbof = d_rbof.Histo1D("rbof")
    h_tail = d_tail.Histo1D("tail")
    h_ch_data = d_ch_data.Histo1D("ch_data")
    h_fifo_oc = d_ch_data.Histo1D("fifo_oc")
    h_ch0_data = d_ch0_data.Histo1D("ch0_data")
    h_ch1_data = d_ch1_data.Histo1D("ch1_data")
    h_ch2_data = d_ch2_data.Histo1D("ch2_data")
    h_ch3_data = d_ch3_data.Histo1D("ch3_data")

    h_stream.Write()
    h_dummy_data.Write()
    h_head.Write()
    h_fifo_satus.Write()
    h_fifo_satus_ch0.Write()
    h_fifo_satus_ch1.Write()
    h_fifo_satus_ch2.Write()
    h_fifo_satus_ch3.Write()
    h_rbof.Write()
    h_tail.Write()
    h_ch_data.Write()
    h_fifo_oc.Write()
    h_ch0_data.Write()
    h_ch1_data.Write()
    h_ch2_data.Write()
    h_ch3_data.Write()

    dfile.Write()
    dfile.Close()
    log.info("Drawing plots end.")


if __name__ == "__main__":
    data_file = "data/data.root"
    draw_data(data_file)
