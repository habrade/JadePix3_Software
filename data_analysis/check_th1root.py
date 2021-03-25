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


if __name__ == '__main__':
    test()
