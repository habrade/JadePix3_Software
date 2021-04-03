#!/usr/bin/env python3

import ROOT
import argparse
import sys
import array as arr


def calc(pulse_period, frame_number, output_file):
    pulse_index = .0
    row_loc = 0
    pulse_loc = .0

    with open(data_file, 'r') as fin:
        lines = fin.readlines()
        framestart = True

        pulse_ideal = int(frame_number * 98.304 / pulse_period) + 1
        print("Maximum pulse number can be catched is: {}".format(pulse_ideal))

        outfile = ROOT.TFile(output_file, 'recreate')
        c1 = ROOT.TCanvas("c1", "c1", 800, 600)

        hpxpy = ROOT.TH2F('Pulse in Frame', 'Pulse vs Frame number', pulse_ideal, 1, pulse_ideal, pulse_ideal, 1,
                          frame_number)

        for line in lines:

            raw16 = int(line, 16)
            flag = (raw16 >> 30)

            if flag == 1:  # Frame Head
                framestart = True
            elif flag == 0:  # Frame tail
                framestart = False
                if row_loc > 0 or (row_loc == 0 and datarow == 511):
                    pulse_loc = raw16 + row_loc/ROW
                    pulse_index += 1.0
                    x.append(pulse_index)
                    y.append(pulse_loc)
                    #print("{} {}".format(pulse_loc, pulse_index))
                    #hpxpy.Fill(pulse_index, pulse_loc)
            elif flag == 2:  # Frame Data
                data = (raw16 & 0xFFFF)
                datarow = (data >> 7)  # 0-511

                if framestart:
                    row_loc = datarow

            framestart = False

    test_rs_period = pulse_period/((y[-1]-y[0])/(x[-1]-x[0]))
    print("Calc rs period: {:}, should be 98.304.".format(test_rs_period))
    print("The diff: {:.4}%".format((test_rs_period/98.304)-1))
    #c1.cd()
    #hpxpy.Draw("colz")
    #c1.Update()
    #hpxpy.write()
    #outfile.Close()


if __name__ == '__main__':
    data_file = "data/data_rs.txt"

    ROW = 512

    x = arr.array('d')
    y = arr.array('d')

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pulse_period',
                        type=int,
                        help="The pulse period injected")
    parser.add_argument('-f', '--frame_number',
                        type=int,
                        help="How many frame number you set")
    parser.add_argument('-o', '--output_file',
                        default="rsT.root",
                        help="The output file path")

    args = parser.parse_args()
    calc(pulse_period=args.pulse_period, frame_number=args.frame_number, output_file=args.output_file)
