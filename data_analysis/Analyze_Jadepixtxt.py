#!/usr/bin/env python3
import os, sys
import glob
from array import array
from ROOT import TCanvas, TGraphErrors, TLine, gROOT, TGaxis, gPad, TLegend, TH1F, TH1D, TH2F, TH2D, TFile, gStyle
from datetime import datetime
import time
import numpy as np
from rootUtil3 import waitRootCmdX

def test(filename="../Data/data/data_rs.txt", outrootname = "./outth2f.root"):

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputTxtFileName", help="the name of input txt file")
    parser.add_option("-o", "--out", dest="outputRootFileName", help="the name of output root file")
    (options, args) = parser.parse_args()
    if(options.inputTxtFileName): filename = options.inputTxtFileName
    if(options.outputRootFileName): outrootname = options.outputRootFileName

    print(f"filename: {filename}, outrootname: {outrootname}")

    outfile = TFile(outrootname,'recreate')
    with open(filename,'r') as fin:
        lines = fin.readlines()
        lineindex = 0
        framenumber = 0
        framestart = False
        frameend = False
        c1 = TCanvas("c1","c1",800,600)
        c2 = TCanvas("c2","c2",800,600)
        for line in lines:
#             print(lineindex)
            lineindex +=1
#             if lineindex > 20:
#                 break
            raw16 = int(line, 16)
            flag = (raw16 >> 30)
#             print(hex(raw16), flag)
            if flag !=1 and (not framestart) and (not frameend):
#                 print(flag, framestart, frameend)
                continue

            if flag == 1: 
                framestart = True
                frameend = False
                th2tag = f"TH2_{framenumber}"
                print(th2tag)
                #th2 = TH2F(th2tag,th2tag,512,0,512,192,0,192);
                th2 = TH2F(th2tag,th2tag,192,0,192,512,0,512);
                th2.GetXaxis().SetTitle("Column")
                th2.GetYaxis().SetTitle("Row")
                framenumber += 1
            elif flag == 0 and framestart:
                frameend = True
                framestart = False
                print(f"framenumber: {raw16}")
                c1.cd()
                th2.Draw("colz")
                c1.Update()
               
                xbinlow = th2.FindFirstBinAbove(0.1, 1)
                xbinhigh = th2.FindLastBinAbove(0.1, 1)
                ybinlow = th2.FindFirstBinAbove(0.1, 2)
                ybinhigh = th2.FindLastBinAbove(0.1, 2)
                print(f"xbinlow {xbinlow}, xbinhigh {xbinhigh}, ybinlow {ybinlow}, ybinhigh {ybinhigh}")
             
                th2clone = th2.Clone("th2clone")
                c2.cd()
                th2clone.GetXaxis().SetRangeUser(xbinlow-5, xbinhigh+5)
                th2clone.GetYaxis().SetRangeUser(ybinlow-5, ybinhigh+5)
                th2clone.Draw("colz")
                c2.Update()

                outfile.cd()
                th2.Write()
#                 a = input("aaa")
                waitRootCmdX(f"Eventnumber: {framenumber}, framenumber: {raw16}")

            elif flag == 2 and framestart and (not frameend): #data
                sec = (raw16 >> 16) & 0x3 #0-3
                data = (raw16 & 0xFFFF)
                datarow = (data >> 7) #0-511
                datablk = (data >> 3) & 0xF #0-15
                databit2 = (data >> 2) & 0x1
                databit1 = (data >> 1) & 0x1
                databit0 = (data & 0x1)
                datacolumn = sec * 48 + datablk * 3 
                print(hex(raw16), flag, sec, bin(data), datarow, datablk, databit0, databit1, databit2, datacolumn)
                th2.SetBinContent(datacolumn, datarow, databit0);
                th2.SetBinContent(datacolumn+1, datarow, databit1);
                th2.SetBinContent(datacolumn+2, datarow, databit2);
   
            if lineindex == len(lines):
                print(f"end of file")
                th2.Draw("colz")
                c1.Update()

                xbinlow = th2.FindFirstBinAbove(0.1, 1)
                xbinhigh = th2.FindLastBinAbove(0.1, 1)
                ybinlow = th2.FindFirstBinAbove(0.1, 2)
                ybinhigh = th2.FindLastBinAbove(0.1, 2)
                print(f"xbinlow {xbinlow}, xbinhigh {xbinhigh}, ybinlow {ybinlow}, ybinhigh {ybinhigh}")

                th2clone = th2.Clone("th2clone")
                c2.cd()
                th2clone.GetXaxis().SetRangeUser(xbinlow-5, xbinhigh+5)
                th2clone.GetYaxis().SetRangeUser(ybinlow-5, ybinhigh+5)
                th2clone.Draw("colz")
                c2.Update()

                outfile.cd()
                th2.Write()
                a = input("aaa")
    outfile.Close()


if __name__ == '__main__':
    gROOT.LoadMacro("AtlasStyle.C")
    gROOT.ProcessLine("SetAtlasStyle()")
    gStyle.SetPalette(55)
    test()
