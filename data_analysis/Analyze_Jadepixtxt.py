#!/usr/bin/env python3
import os, sys
import glob
from array import array
from ROOT import TCanvas, TGraphErrors, TLine, gROOT, TGaxis, gPad, TLegend, TH1F, TH1D, TH2F, TH2D, TFile, gStyle
from datetime import datetime
import time
import numpy as np
from rootUtil3 import waitRootCmdX

def test(filename="../data/data_rs.txt", outrootname = "./outth2f.root"):

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
                #th2clone.GetXaxis().SetRangeUser(xbinlow-5, xbinhigh+5)
                th2clone.GetXaxis().SetRangeUser(102, 110)
                #th2clone.GetYaxis().SetRangeUser(ybinlow-5, ybinhigh+5)
                th2clone.GetYaxis().SetRangeUser(256, 266)
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
                #th2clone.GetXaxis().SetRangeUser(xbinlow-5, xbinhigh+5)
                th2clone.GetXaxis().SetRangeUser(102, 110)
                #th2clone.GetYaxis().SetRangeUser(ybinlow-5, ybinhigh+5)
                th2clone.GetYaxis().SetRangeUser(256, 266)
                th2clone.Draw("colz")
                c2.Update()

                outfile.cd()
                th2.Write()
                a = input("aaa")
    outfile.Close()


def testresidual(filename="../data/data_rs.txt", outrootname = "./outth1f.root", laserxpoi=0.700, laserypoi=5.600, doperbin=False):

    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="inputTxtFileName", help="the name of input txt file")
    parser.add_option("-o", "--out", dest="outputRootFileName", help="the name of output root file")
    parser.add_option("-x", "--x", dest="laserX", help="laser x position")
    parser.add_option("-y", "--y", dest="laserY", help="laser y position")
    (options, args) = parser.parse_args()
    if(options.inputTxtFileName): filename = options.inputTxtFileName
    if(options.outputRootFileName): outrootname = options.outputRootFileName
    if(options.laserX): laserxpoi = float(options.laserX)
    if(options.laserY): laserypoi = float(options.laserY)

    print(f"filename: {filename}, outrootname: {outrootname}, laserxpoi {laserxpoi}, laserypoi {laserypoi}")

    outfile = TFile(outrootname,'recreate')

    th1resiXraw = TH1F("th1resiXraw","th1resiXraw",100000,0,1000)
    th1centerXraw = TH1F("th1centerXraw","th1centerXraw",100000,0,10000)
    th1resiXprojXall = TH1F("th1resiXprojXall","th1resiXprojXall",100000,0,1000)

    th1resiYraw = TH1F("th1resiYraw","th1resiYraw",100000,0,1000)
    th1centerYraw = TH1F("th1centerYraw","th1centerYraw",100000,0,10000)
    th1resiYprojYall = TH1F("th1resiYprojYall","th1resiYprojYall",100000,0,1000)

    if doperbin:
            lth1resiXperbin = []
            for i in range(0,512):
                th1resiXperbintmp = TH1F(f"lth1resiXperbin{i}",f"lth1resiXperbin{i}",100000,0,1000)
                lth1resiXperbin.append(th1resiXperbintmp)

            lth1resiYperbin = []
            for i in range(0,192):
                th1resiYperbintmp = TH1F(f"lth1resiYperbin{i}",f"lth1resiYperbin{i}",100000,0,1000)
                lth1resiYperbin.append(th1resiYperbintmp)

    th1Nbinsabove0p1 = TH1F("th1Nbinsabove0p1","th1Nbinsabove0p1",1000,0,1000)
    th1Nrowsabove0p1 = TH1F("th1Nrowsabove0p1","th1Nrowsabove0p1",1000,0,1000)
    th1Ncolsabove0p1 = TH1F("th1Ncolsabove0p1","th1Ncolsabove0p1",1000,0,1000)

    with open(filename,'r') as fin:
        lines = fin.readlines()
        lineindex = 0
        framenumber = 0
        framestart = False
        frameend = False
        for line in lines:
            lineindex +=1
            raw16 = int(line, 16)
            flag = (raw16 >> 30)
            if flag !=1 and (not framestart) and (not frameend):
                continue

            if flag == 1: 
                framestart = True
                frameend = False
                th2tag = f"TH2_{framenumber}"
                #print(th2tag)
                #th2 = TH2F(th2tag,th2tag,512,0,512,192,0,192);
                th2 = TH2F(th2tag,th2tag,192,0,192,512,0,512);
                th2.GetXaxis().SetTitle("Column")
                th2.GetYaxis().SetTitle("Row")
                framenumber += 1
            elif flag == 0 and framestart:
                frameend = True
                framestart = False
                print(f"Eventnumber: {framenumber}, framenumber: {raw16}")
                
                laseroffsetX = (0.7-laserxpoi)*1000 + 100.*23.11
                laseroffsetY = (5.6-laserypoi)*1000 + 230.*16
		#calculaate residual from 2D hist
                xbinlow = th2.FindFirstBinAbove(0.1, 1)
                xbinhigh = th2.FindLastBinAbove(0.1, 1)
                ybinlow = th2.FindFirstBinAbove(0.1, 2)
                ybinhigh = th2.FindLastBinAbove(0.1, 2)
                print(f"xbinlow {xbinlow}, xbinhigh {xbinhigh}, ybinlow {ybinlow}, ybinhigh {ybinhigh}")

                # cut 
                if xbinlow < 192*2./4 or xbinlow > 192*3./4 or ybinlow < 200 or ybinlow > 300:
                    continue


                xbincenterraw = (xbinlow-0.5+xbinhigh-0.5)*0.5*23.11
                #xbincenterraw = (xbinlow+xbinhigh)*0.5*23.
                residuXraw =  xbincenterraw - laseroffsetX
                th1resiXraw.Fill(residuXraw)
                th1centerXraw.Fill(xbincenterraw)
                print(f"xbincenterraw {xbincenterraw}, residuXraw {residuXraw}")

                ybincenterraw = (ybinlow-0.5+ybinhigh-0.5)*0.5*16.
                #ybincenterraw = (ybinlow+ybinhigh)*0.5*23.
                residuYraw =  ybincenterraw - laseroffsetY
                th1resiYraw.Fill(residuYraw)
                th1centerYraw.Fill(ybincenterraw)
                print(f"ybincenterraw {ybincenterraw}, residuYraw {residuYraw}")

                th1projXall = th2.ProjectionX("th1projXall")
                #th1projXall.Draw()
                residuXprojXall = th1projXall.GetMean()*23.11 - laseroffsetX
                print(f"th1projXall.GetMean() {th1projXall.GetMean()}, residuXprojXall {residuXprojXall}")
                th1resiXprojXall.Fill(residuXprojXall)

                th1projYall = th2.ProjectionY("th1projYall")
                #th1projYall.Draw()
                residuYprojYall = th1projYall.GetMean()*16. - laseroffsetY
                print(f"th1projYall.GetMean() {th1projYall.GetMean()}, residuYprojYall {residuYprojYall}")
                th1resiYprojYall.Fill(residuYprojYall)
 
                if doperbin:
                        for i in range(0, 512):
                            th1projXperbintmp = th2.ProjectionX(f"lth1projXperbin{i}",i+1,i+1)
                            residuXprojXperbintmp = th1projXperbintmp.GetMean()*23 - laseroffsetX
                            #print(f"i {i}, th1projXperbintmp.GetMean() {th1projXperbintmp.GetMean()}, residuXprojXperbintmp {residuXprojXperbintmp}")
                            lth1resiXperbin[i].Fill(residuXprojXperbintmp)    
                        for i in range(0, 192):
                            th1projYperbintmp = th2.ProjectionY(f"lth1projYperbin{i}",i+1,i+1)
                            residuYprojYperbintmp = th1projYperbintmp.GetMean()*23 - laseroffsetY
                            #print(f"i {i}, th1projYperbintmp.GetMean() {th1projYperbintmp.GetMean()}, residuYprojYperbintmp {residuYprojYperbintmp}")
                            lth1resiYperbin[i].Fill(residuYprojYperbintmp)

#                Nbinsabove0p1 = 0;
#                for ix in range(0,192):
#                    for iy in range(0,512):
#                        if th2.GetBinContent(ix+1, iy+1)>0.1: Nbinsabove0p1 += 1
                Nbinswithhit = th2.Integral()
#                print(f"Nbinsabove0p1 {Nbinsabove0p1}, Nbinswithhit {Nbinswithhit}")
#                th1Nbinsabove0p1.Fill(Nbinsabove0p1)
                th1Nbinsabove0p1.Fill(Nbinswithhit)

                Nrowswithhit =0;
                for iy in range(ybinlow,ybinhigh+1):
                    if th1projYall.GetBinContent(iy)>0.1: Nrowswithhit += 1
                th1Nrowsabove0p1.Fill(Nrowswithhit)

                Ncolswithhit =0;
                for ix in range(xbinlow,xbinhigh+1):
                    if th1projXall.GetBinContent(ix)>0.1: Ncolswithhit += 1
                th1Ncolsabove0p1.Fill(Ncolswithhit)
                

                #waitRootCmdX(f"Eventnumber: {framenumber}, framenumber: {raw16}")

            elif flag == 2 and framestart and (not frameend): #data
                sec = (raw16 >> 16) & 0x3 #0-3
                data = (raw16 & 0xFFFF)
                datarow = (data >> 7) #0-511
                datablk = (data >> 3) & 0xF #0-15
                databit2 = (data >> 2) & 0x1
                databit1 = (data >> 1) & 0x1
                databit0 = (data & 0x1)
                datacolumn = sec * 48 + datablk * 3 
                #print(hex(raw16), flag, sec, bin(data), datarow, datablk, databit0, databit1, databit2, datacolumn)
                th2.SetBinContent(datacolumn, datarow, databit0);
                th2.SetBinContent(datacolumn+1, datarow, databit1);
                th2.SetBinContent(datacolumn+2, datarow, databit2);
   
            if lineindex == len(lines):
                print(f"end of file, do not process the last event, for now...")

    #th1resi.Draw()
    #th1center.Draw()
    #waitRootCmdX(f"residual and center")
    th1resiXraw.Write()
    th1centerXraw.Write()
    th1resiXprojXall.Write()
    th1resiYraw.Write()
    th1centerYraw.Write()
    th1resiYprojYall.Write()

    if doperbin:
            for i in range(0,512):
                lth1resiXperbin[i].Write()
            for i in range(0,192):
                lth1resiYperbin[i].Write()

    th1Nbinsabove0p1.Write()
    th1Nrowsabove0p1.Write()
    th1Ncolsabove0p1.Write()

    print(f"Summmary: th1resiXraw.GetRMS() {th1resiXraw.GetRMS()}, th1resiXprojXall.GetRMS() {th1resiXprojXall.GetRMS()}, th1resiYraw.GetRMS() {th1resiYraw.GetRMS()}, th1resiYprojYall.GetRMS() {th1resiYprojYall.GetRMS()}, th1Nbinsabove0p1.GetMean(), {th1Nbinsabove0p1.GetMean()}")
    outfile.Close()


if __name__ == '__main__':
    gROOT.LoadMacro("AtlasStyle.C")
    gROOT.ProcessLine("SetAtlasStyle()")
    gStyle.SetPalette(55)
    test()
    # testresidual()
