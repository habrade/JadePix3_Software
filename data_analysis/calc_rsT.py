#!/usr/bin/env python3

import ROOT
import argparse
import sys
import array as arr

import numpy as np

ROW = 512

RS_PERIOD_IDLE = 98.304

y = arr.array('d')


def calc(pulse_period, frame_number, input_file, output_file):
    pulse_index = .0
    row_loc = 0
    pulse_loc = .0

    last_frame_number = 0

    frame_delta = pulse_period/RS_PERIOD_IDLE
    print("frame_delta: {}".format(frame_delta))

    with open(input_file, 'r') as fin:
        lines = fin.readlines()
        framestart = True

        pulse_ideal = int(frame_number * 98.304 / pulse_period) + 1
        print("Maximum pulse number can be catched is: {}".format(pulse_ideal))

        outfile = ROOT.TFile(output_file, 'recreate')
        c1 = ROOT.TCanvas("c1", "c1", 800, 600)

        # hpxpy = ROOT.TH2F('Pulse in Frame', 'Pulse vs Frame number', pulse_ideal, 1, pulse_ideal, pulse_ideal, 1,
        #                   frame_number)

        for line in lines:

            raw16 = int(line, 16)
            flag = (raw16 >> 30)

            if flag == 1:  # Frame Head
                framestart = True
            elif flag == 0:  # Frame tail

                last_frame_number = raw16
                framestart = False
                if row_loc > 0 or (row_loc == 0 and datarow == 511):
                    pulse_loc = raw16 + row_loc/ROW
                    pulse_index += 1.0
                    y.append(pulse_loc)

                    # print("{} {}".format(pulse_loc, pulse_index))
                    # hpxpy.Fill(pulse_index, pulse_loc)
            elif flag == 2:  # Frame Data
                data = (raw16 & 0xFFFF)
                datarow = (data >> 7)  # 0-511

                if framestart:
                    row_loc = datarow

                framestart = False


    if y[0] == .0:
        y.remove(y[0])
    
    while True: 
        for i in range(len(y)-1):
            if (y[i+1] - y[i] < frame_delta):
                y.remove(y[i+1])
                break
        break
        
    test_rs_period = pulse_period/((y[-1]-y[0])/(len(y)-1))

    print("Calc rs period (Tail - Head): {:}".format(test_rs_period))
    print("The diff: {:.4}%".format(((test_rs_period/98.304)-1)*100))


    delta_lst = []
    for i in range(len(y)-1):
        delta_lst.append(y[i+1]-y[i])

    delta_npa = np.array(delta_lst)

    mean = np.mean(delta_npa)
    std_val = np.std(delta_npa)
    print("mean: {}, std: {}".format(mean, std_val))
    print("Calc rs period (Mean): {:}".format(pulse_period/mean))

    tgra = ROOT.TGraph(len(y), arr.array('d', list(range(1, len(y)+1))), y)
    tgra.Draw("*")
    tgra.SetTitle("Pulse location in frame")
    tgra.GetXaxis().SetTitle("Pulse Index"); 
    tgra.GetYaxis().SetTitle("Pulse Location"); 
    tgra.Fit("pol1")
    slope = tgra.GetFunction("pol1").GetParameter(1)
    print("Fit slope: {:}".format(slope))
    t_legend = ROOT.TLegend(0.1,0.7,0.48,0.9)
    t_legend.SetHeader("Slope: {:}".format(slope))
    t_legend.Draw()


    frame_delta_err = []
    th1_mean = ROOT.TH1F("h1","The width of pulse", 10240 , mean-1, mean+1)
    for frame_delta in delta_lst:
        if frame_delta > 6:
            frame_delta_err.append(frame_delta)
        th1_mean.Fill(frame_delta)
    
    print(frame_delta_err)
    print("len larger than 6: {:}".format(len(frame_delta_err)))
    tgra.Write()
    # th1_mean.Write()
    outfile.Write()
    outfile.Close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pulse_period',
                        type=int,
                        help="The pulse period injected")
    parser.add_argument('-f', '--frame_number',
                        type=int,
                        help="How many frame number you set")
    parser.add_argument('-i', '--input_file',
                        default="data/data_rs.txt",
                        help="The input file path")
    parser.add_argument('-o', '--output_file',
                        default="rsT.root",
                        help="The output file path")

    args = parser.parse_args()
    calc(pulse_period=args.pulse_period, frame_number=args.frame_number, input_file=args.input_file, output_file=args.output_file)
