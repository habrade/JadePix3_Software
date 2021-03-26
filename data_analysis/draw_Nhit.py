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

def GetNhit(filename):
    f = TFile(filename,"read")
    h1 = f.Get("th1Nbinsabove0p1")
    Nhit = (h1.GetMean(), h1.GetMeanError(), h1.GetRMS(), h1.GetRMS()/(h1.GetEntries()**0.5) )
    return Nhit

def test():
    print("test")
    Dir="./Outfiles/";
    filenamesZ = glob.glob(Dir+"test_rs_0325_z*.root")
    filenamesZ = sorted(filenamesZ, key=lambda x:x)

    grs = TGraphErrors()
    index = 0
    for filename in filenamesZ:
        Z = float(os.path.basename(filename).split('.')[0][-4:])
        Nhit = GetNhit(filename)
        print(filename, Z, Nhit) 
        grs.SetPoint(index, Z, Nhit[0])
        grs.SetPointError(index, 0, Nhit[1])
        index += 1
     
    c1 = TCanvas("c1","c1",0,0,800,600)
    grs.Draw("APL")
    grs.GetXaxis().SetTitle("Laser Position Z (#mum)")
    grs.GetYaxis().SetTitle("Number of Hits")
    c1.Update()
    os.makedirs("./Plots", exist_ok=True)
    c1.Print("./Plots/NhitsVSZ.pdf")
    waitRootCmdX()

if __name__ == '__main__':
    gROOT.LoadMacro("AtlasStyle.C")
    gROOT.ProcessLine("SetAtlasStyle()")
    test()
