#!/usr/bin/env python3
from ROOT import TGraphErrors, TChain, RDataFrame, EnableImplicitMT, TFile, gDirectory
from ROOT import TCanvas, TF1
from rootUtil3 import getRDF, waitRootCmdX
import numpy as np
import sys

def test(filename="total_test.root"):
    filename = sys.argv[1]
    f1 = TFile(filename)
    for key1 in f1.GetListOfKeys():
        tp1 = f1.Get(key1.GetName())
        print(f"{key1.GetName()} {tp1.GetRMS()}")

def GetEntries(filename="total_test.root"):
    f1 = TFile(filename)
    print(filename, f1.Get("th1resiXprojXall").GetEntries()) 


if __name__ == '__main__':
    #test()
    for f in range(720, 743):
        GetEntries(f"Outfiles/test_rs_0326_tune94p1_x0{f}.root")


    for f in range(608, 623):
        GetEntries(f"Outfiles/test_rs_0326_tune94p1_y5{f}.root")
