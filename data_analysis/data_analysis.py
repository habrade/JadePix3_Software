import coloredlogs
import logging

import ROOT

from array import array

from lib import jadepix_defs

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
coloredlogs.install(level='DEBUG')
coloredlogs.install(level='DEBUG', logger=log)


class DataAnalysis:
    def __init__(self, data_txt_file, frame_num, is_save_png):
        self._data_txt_file = data_txt_file
        self._is_save_png = is_save_png
        self._frame_num = frame_num

        self.data_root_file = "data/data.root"
        self.hfile = ROOT.gROOT.FindObject(self.data_root_file)
        if self.hfile:
            self.hfile.Close()
        self.hfile = ROOT.TFile(self.data_root_file, 'RECREATE', 'Data ROOT file')

    def load_data_to_root(self):
        log.info("Write data to .root ...")
        data = array("I", [0])
        d_tree = ROOT.TTree('root_tree', 'Data_Stream')
        d_tree.Branch('data', data, 'data/i')
        with open(self._data_txt_file, 'r') as fo:
            for line in fo.readlines():
                data[0] = int(line, 10)
                d_tree.Fill()
        d_tree.Write()
        self.hfile.Close()
        log.info("Write to .root end.")

    def draw_data(self):
        log.info("Start drawing plots...")

        ''' Going parallel '''
        ROOT.EnableImplicitMT()

        drawing_file = "data/drawing.root"
        dfile = ROOT.gROOT.FindObject(drawing_file)
        if dfile:
            dfile.Close()
        dfile = ROOT.TFile(drawing_file, 'RECREATE', 'Drawing plots')

        ''' Try DataFrame '''
        df = ROOT.RDataFrame("root_tree", self.data_root_file)
        d_valid = df.Filter("data < 0x1FFFFFF").Define("data_stream", "data")

        d_dummy_data = d_valid.Filter("data == 0xFFFFFFFF").Define("dummy_data", "data - 1")
        d_head = d_valid.Filter("(data >> 23) == 1").Define("head", "data")

        d_fifo_status = d_head.Filter("(data >> 23) == 1").Define("fifo_status", "(head >> 15) & 0xFF").Define(
            "fifo_status_ch0", "(fifo_status & 0xc0)").Define("fifo_status_ch1", "(fifo_status & 0x30)").Define(
            "fifo_status_ch2", "(fifo_status & 0x0c)").Define("fifo_status_ch3", "(fifo_status & 0x03)")
        d_rbof = d_head.Filter("(data >> 23) == 1").Define("rbof", "head & 0x7FFF")
        d_tail = d_valid.Filter("(data >> 23) == 0").Define("frame_index", "data & 0x3FFFF")
        d_ch_data = d_valid.Filter("(data >> 23) == 2").Define("ch_data", "data").Define("fifo_oc",
                                                                                         "((ch_data >> 18) & 0x1F)")

        d_ch0_data = d_ch_data.Filter("((ch_data >> 16) & 0x3 ) == 0").Define("ch0_data", "(ch_data & 0xFFFF)")
        d_ch1_data = d_ch_data.Filter("((ch_data >> 16) & 0x3 ) == 1").Define("ch1_data", "(ch_data & 0xFFFF)")
        d_ch2_data = d_ch_data.Filter("((ch_data >> 16) & 0x3 ) == 2").Define("ch2_data", "(ch_data & 0xFFFF)")
        d_ch3_data = d_ch_data.Filter("((ch_data >> 16) & 0x3 ) == 3").Define("ch3_data", "(ch_data & 0xFFFF)")

        d_rfifo_oc = d_valid.Filter("((data >> 23) == 3) && (data != 0xFFFFFFFF)").Define("rfifo_oc", "data")

        h_stream = d_valid.Histo1D("data_stream")
        h_dummy_data = d_dummy_data.Histo1D(("", "", 2, 2 ** 16 - 1, 2 ** 16 + 1), "dummy_data")
        h_head = d_head.Histo1D("head")
        h_fifo_satus = d_fifo_status.Histo1D("fifo_status")
        h_fifo_satus_ch0 = d_fifo_status.Histo1D("fifo_status_ch0")
        h_fifo_satus_ch1 = d_fifo_status.Histo1D("fifo_status_ch1")
        h_fifo_satus_ch2 = d_fifo_status.Histo1D("fifo_status_ch2")
        h_fifo_satus_ch3 = d_fifo_status.Histo1D("fifo_status_ch3")
        h_rbof = d_rbof.Histo1D("rbof")
        h_frame_index = d_tail.Histo1D(("frame_index", "frame_index", self._frame_num, 1, self._frame_num + 1),
                                       "frame_index")
        h_ch_data = d_ch_data.Histo1D("ch_data")
        h_fifo_oc = d_ch_data.Histo1D("fifo_oc")

        h_ch0_data = d_ch0_data.Histo1D(("ch0_data", "ch0_data", self._frame_num, 1, self._frame_num + 1), "ch0_data")
        h_ch1_data = d_ch1_data.Histo1D(("ch1_data", "ch1_data", self._frame_num, 1, self._frame_num + 1), "ch1_data")
        h_ch2_data = d_ch2_data.Histo1D(("ch2_data", "ch2_data", self._frame_num, 1, self._frame_num + 1), "ch2_data")
        h_ch3_data = d_ch3_data.Histo1D(("ch3_data", "ch3_data", self._frame_num, 1, self._frame_num + 1), "ch3_data")
        h_rfifo_oc = d_rfifo_oc.Histo1D(("rfifo_oc", "rfifo_oc", 2 ** 15, 1, 2 ** 15 + 1), "rfifo_oc")

        h_stream.Write()
        h_dummy_data.Write()
        h_head.Write()
        h_fifo_satus.Write()
        h_fifo_satus_ch0.Write()
        h_fifo_satus_ch1.Write()
        h_fifo_satus_ch2.Write()
        h_fifo_satus_ch3.Write()
        h_rbof.Write()
        # h_frame_index.SetLineColor(5);
        # h_frame_index.SetMarkerColor(4);
        # h_frame_index.SetOption("b")
        # h_frame_index.Draw()
        h_frame_index.Write()
        h_ch_data.Write()
        h_fifo_oc.Write()

        h_ch0_data.Write()
        h_ch1_data.Write()
        h_ch2_data.Write()
        h_ch3_data.Write()
        h_rfifo_oc.Write()

        ''' Picture Output '''
        if self._is_save_png:
            c0 = ROOT.TCanvas()
            h_head.Draw()
            c0.SaveAs("data/fig/frame_head.png")

            c1 = ROOT.TCanvas()
            h_frame_index.Draw()
            c1.SaveAs("data/fig/frame_index.png")

            c2 = ROOT.TCanvas()
            c2.Divide(2, 2, 0, 0)
            c2.cd(1)
            h_ch0_data.Draw()
            c2.cd(2)
            h_ch1_data.Draw()
            c2.cd(3)
            h_ch2_data.Draw()
            c2.cd(4)
            h_ch3_data.Draw()
            c2.SaveAs("data/fig/data.png")

            c3 = ROOT.TCanvas()
            h_rbof.Draw()
            c3.SaveAs("data/fig/rbof.png")

            c4 = ROOT.TCanvas()
            h_dummy_data.Draw()
            c4.SaveAs("data/fig/dummy_data.png")

            c5 = ROOT.TCanvas()
            h_fifo_oc.Draw()
            c5.SaveAs("data/fig/fifo_oc.png")

            c6 = ROOT.TCanvas()
            h_rfifo_oc.Draw()
            c6.SaveAs("data/fig/rfifo_oc.png")

            c7 = ROOT.TCanvas()
            h_ch_data.Draw()
            c7.SaveAs("data/fig/ch_data.png")

        num_frame_lost = 0
        for i in range(self._frame_num):
            if h_frame_index.GetBinContent(i) == 0:
                num_frame_lost += 1
                log.debug(
                    "Frame Index {:} Entries: {:}, Center: {:}, Width: {:}".format(i, h_frame_index.GetBinContent(i),
                                                                                   h_frame_index.GetBinCenter(i),
                                                                                   h_frame_index.GetBinWidth(i)))
        log.info("Num of frame lost: {:}".format(num_frame_lost))

        ''' Write file and close file '''
        dfile.Write()
        dfile.Close()
        self.hfile.Close()
        log.info("Drawing plots end.")

        data_num = h_ch_data.GetEntries()
        return num_frame_lost, data_num


if __name__ == "__main__":
    test_valid_pattern = 1
    frame_per_slice = 64
    num_token = 1000

    frame_number = frame_per_slice * num_token
    num_data = frame_number * jadepix_defs.ROW * jadepix_defs.BLK * test_valid_pattern
    num_valid_data_stream = num_data + 2 * frame_number - 1

    rfifo_depth_width = 17
    rfifo_depth = pow(2, rfifo_depth_width)

    slice_size = int(rfifo_depth)  # try largest slice as possible
    num_data_wanted = num_token * slice_size
    data_size = num_data_wanted * 32  # Unit: bit
    data_file = "data/data.txt"
    data_ana = DataAnalysis(data_file, frame_num=6400, is_save_png=True)
    data_ana.load_data_to_root()
    data_ana.draw_data()
    lost_tmp, data_num_got = data_ana.draw_data()
    data_lost = num_data - data_num_got
    log.info("lost data num: {:}".format(data_lost))
