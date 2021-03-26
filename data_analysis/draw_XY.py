#!/usr/bin/env python3
import os, sys
import glob
from array import array
from ROOT import TCanvas, TGraphErrors, TLine, gROOT, TGaxis, gPad, TLegend, TH1F, TH1D, TChain, gDirectory, TFile
from datetime import datetime
import time
import numpy as np
from ROOT import kBlue, kRed, kBlack, kGreen
import math
from rootUtil3 import waitRootCmdX


def test(filename="total_test.root"):
    filename = sys.argv[1]
    f1 = TFile(filename)
    for key1 in f1.GetListOfKeys():
        tp1 = f1.Get(key1.GetName())
        print(f"{key1.GetName()} {tp1.GetRMS()}")

def GetEntries(filename, histname):
    f1 = TFile(filename)
#    print(filename, f1.Get("th1resiXprojXall").GetEntries()) 
    return f1.Get(histname).GetEntries() 

def draw_X():
    filenamesX = glob.glob("Outfiles/test_rs_0326_tune94p1_x*.root")
    filenamesX = sorted(filenamesX, key=lambda x:x)

    grs = TGraphErrors()
    index = 0
    for filename in filenamesX:
        X = float(os.path.basename(filename).split('.')[0][-4:])
        NEntries = GetEntries(filename, "th1resiXprojXall")
        print(filename, X, NEntries)
        grs.SetPoint(index, X, NEntries)
        grs.SetPointError(index, 0, 0)
        index += 1

    c1 = TCanvas("c1","c1",0,0,800,600)
    grs.Draw("APL")
    grs.GetXaxis().SetTitle("Laser Position X (#mum)")
    grs.GetYaxis().SetTitle("Entries")
    c1.Update()
    os.makedirs("./Plots", exist_ok=True)
    c1.Print("./Plots/EntriesVSX.pdf")
    waitRootCmdX()


def draw_Y():
    filenamesY = glob.glob("Outfiles/test_rs_0326_tune94p2_y*.root")
    filenamesY = sorted(filenamesY, key=lambda x:x)

    grs = TGraphErrors()
    index = 0
    for filename in filenamesY:
        Y = float(os.path.basename(filename).split('.')[0][-4:])
        NEntries = GetEntries(filename, "th1resiYprojYall")
        print(filename, Y, NEntries)
        grs.SetPoint(index, Y, NEntries)
        grs.SetPointError(index, 0, 0)
        index += 1

    c1 = TCanvas("c1","c1",0,0,800,600)
    grs.Draw("APL")
    grs.GetYaxis().SetTitle("Laser Position Y (#mum)")
    grs.GetYaxis().SetTitle("Entries")
    c1.Update()
    os.makedirs("./Plots", exist_ok=True)
    c1.Print("./Plots/EntriesVSY.pdf")
    waitRootCmdX()

if __name__ == '__main__':
    #test()
    gROOT.LoadMacro("AtlasStyle.C")
    gROOT.ProcessLine("SetAtlasStyle()")
    #draw_X()
    draw_Y()
