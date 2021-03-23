#!/usr/bin/env python3
from ROOT import gROOT, gPad, TIter, gStyle
import sys, os
class bcolors:
    '''Show colored messages:
    bcolors.show(LEWEL, TEXT)'''

    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''
    def show(self, level, text):
        try:
            print(getattr(self, level) + text + self.ENDC)
        except AttributeError as e:
            self.show('FAIL', e.args[0])
            print(text)

def get_default_fig_dir():
    from datetime import date
    return date.today().strftime('figs_%Y%b%d/')

def textValue(v, ndig=0):
    return ('{0:.'+'{0:d}'.format(ndig)+'f}').format(abs(v)).replace('.', 'm' if v<0 else 'p')

def get_pre(val):
    s = '{0:.3e}'.format(val).split('e')
    p = -int(s[1])
    if float(s[0]) < 3.55: p+=1
    if p<0: p=0
    return '{0:d}'.format(p)

def getValuePDG(s, sp='+/-'):
    '''s = 0.2212 +/- 0.42423'''
    fs = s.split('+/-')
    v = float(fs[0])
    e = float(fs[1])
    p = get_pre(e)
    fmt = '{0:.'+p+'f}'+sp+'{1:.'+p+'f}'
#     print fmt
    return fmt.format(v,e)

def get_pre2(val):
    s = '{0:.3e}'.format(val).split('e')
    p = -int(s[1])+1
#     if float(s[0]) < 3.55: p+=1
    if p<0: p=0
    return '{0:d}'.format(p)

def to_precision(val):
    n=2
    s = '{0:.3e}'.format(val).split('e')
    p = -int(s[1])+n-1
    if p<0: p=0
    return ('{0:.'+'{0:d}'.format()+'f}').format(val)

def listContentOfPad(c1):
    next = TIter(c1.GetListOfPrimitives())
    while True:
        obj = next()
        if not obj: break
        print(obj.ClassName(), obj.GetName(), obj.GetTitle())

def useStyle0(obj, mark=True):
    pass

def useStyle1(obj, mark=True):
    obj.SetLineColor(2)
    obj.SetLineWidth(2)
    if mark:
        obj.SetMarkerStyle(24)
        obj.SetMarkerColor(2)
#         obj.SetFillColor(2)

def useStyle2(obj, mark=True):
    obj.SetLineColor(4)
    obj.SetLineWidth(2)
    obj.SetLineStyle(2)
    if mark:
        obj.SetMarkerStyle(25)
        obj.SetMarkerColor(4)
#         obj.SetFillColor(4)

def useStyle3(obj, mark=True):
    obj.SetLineColor(3)
    obj.SetLineWidth(2)
    obj.SetLineStyle(9)
    if mark:
        obj.SetMarkerStyle(26)
        obj.SetMarkerColor(3)
#         obj.SetFillColor(3)

def useStyle4(obj, mark=True):
    obj.SetLineColor(6)
    obj.SetLineWidth(2)
    obj.SetLineStyle(5)
    if mark:
        obj.SetMarkerStyle(27)
        obj.SetMarkerColor(6)
#         obj.SetFillColor(6)

def useStyle5(obj, mark=True):
    obj.SetLineColor(5)
    obj.SetLineWidth(2)
    obj.SetLineStyle(7)
    if mark:
        obj.SetMarkerStyle(28)
        obj.SetMarkerColor(5)
#         obj.SetFillColor(5)

def useStyle6(obj, mark=True):
    obj.SetLineColor(7)
    obj.SetLineWidth(2)
    obj.SetLineStyle(3)
    if mark:
        obj.SetMarkerStyle(29)
        obj.SetMarkerColor(7)
#         obj.SetFillColor(7)


def useStyleX(i, obj, opt=None):
    styles1 = [(1,1,2,20,0),
            (2,1,2,24),
            (4,2,2,25),
            (3,9,2,26),
            (5,7,2,28),
            (6,5,2,27),
            (7,3,2,29),
            ]
    mkupHistSimple(obj, styles1[i], opt)
    pass

def useStyle(i, obj, mark=True):
    globals()["useStyle"+str(i)](obj, mark)

def makeupHist(h1, lc, ls, lw, mc, ms, mz=1):
    h1.SetLineColor(lc)
    h1.SetLineStyle(ls)
    h1.SetLineWidth(lw)
    h1.SetMarkerColor(mc)
    h1.SetMarkerStyle(ms)
    h1.SetMarkerSize(mz)

def mkHist(h1, c, ms=None, ls=None, lw=None, mz=None):
    h1.SetLineColor(c)
    h1.SetMarkerColor(c)
    if ls: h1.SetLineStyle(ls)
    if lw: h1.SetLineWidth(lw)
    if ms: h1.SetMarkerStyle(ms)
    if mz: h1.SetMarkerSize(mz)

def mkupHist(h1, t):
    h1.SetLineColor(t[0])
    h1.SetLineStyle(t[1])
    h1.SetLineWidth(t[2])
    h1.SetMarkerColor(t[3])
    h1.SetMarkerStyle(t[4])
    h1.SetMarkerSize(t[5])

def mkupHistSimple(h1, t, opt=None):
    h1.SetLineColor(t[0])
    h1.SetMarkerColor(t[0])
    h1.SetMarkerStyle(t[3])
    if opt and opt.find('f')!=-1:
        h1.SetFillColor(t[0] if len(t)<5 else t[4])
    else:
        h1.SetLineStyle(t[1])
        h1.SetLineWidth(t[2])

def waitRootCmd2(defaultSaveName='test', saveDirectly=0):
    if saveDirectly==1: return savePad(defaultSaveName)
    elif saveDirectly==-1: return

    print('defaultSaveName:', defaultSaveName)

    code = 0
    while True:
        x = input('root: ').rstrip()
        if x.lower() == 'e' or x.lower() == 'end' or x.lower() == 'q' or x.lower() == 'quit' or x.lower() == '.q': sys.exit()
        elif x=='' or x.lower() == 'n' or x.lower() == 'next': break
        args = x.split()
        if args[0]=='s' or args[0]=='save':
            if len(args)<2: args.append(defaultSaveName)
            savePad(args[1:])
            code |= (1<<1)
            continue
        elif args[0]=='p' or args[0]=='pass': return args[1:]
        try:
            print('root processing "'+x+'"')
            gROOT.ProcessLine(x)
        except:
            print('command not recognized')
            continue
    return code


def waitRootCmdX(defaultSaveName='test', saveDirectly=False, updateFirst=True,  pad=gPad):
    if updateFirst: pad.Update()
    if saveDirectly: return savePad(defaultSaveName, pad)

    print('defaultSaveName:', defaultSaveName)
    ### code records if the figure is saved. 
    code = 0
    while True:
        x = input('root: ').rstrip()
        if x.lower() == 'e' or x.lower() == 'end' or x.lower() == 'q' or x.lower() == 'quit' or x.lower() == '.q': sys.exit()
        elif x=='' or x.lower() == 'n' or x.lower() == 'next': break
        args = x.split()
        if args[0]=='s' or args[0]=='save':
            if len(args)<2: args.append(defaultSaveName)
            savePad(args[1:], pad)
            code |= (1<<1)
            continue
        elif args[0]=='p' or args[0]=='pass': return args[1:]
        try:
            print('root processing "'+x+'"')
            gROOT.ProcessLine(x)
        except:
            print('command not recognized')
            continue
    return code

def waitRootCmd(defaultSaveName='test', saveDirectly=False):
    if saveDirectly: return savePad(defaultSaveName)
    print('defaultSaveName:', defaultSaveName)

    code = 0
    while True:
        x = input('root: ').rstrip()
        if x.lower() == 'e' or x.lower() == 'end' or x.lower() == 'q' or x.lower() == 'quit' or x.lower() == '.q': sys.exit()
        elif x=='' or x.lower() == 'n' or x.lower() == 'next': break
        args = x.split()
        if args[0]=='s' or args[0]=='save':
            if len(args)<2: args.append(defaultSaveName)
            savePad(args[1:])
            code |= (1<<1)
            continue
        elif args[0]=='p' or args[0]=='pass': return args[1:]
        try:
            print('root processing "'+x+'"')
            gROOT.ProcessLine(x)
        except:
            print('command not recognized')
            continue
    return code

def waitRootCmdMore(padlist, saveDirectly=False):
    '''padList is a dict: {pad, name} # means one pad can only save by one name? Maybe use list of tuple?'''
    if saveDirectly:
        for p,c in padlist.items():
            savePad(p, c)
        return
    while True:
        x = input('root: ')
        if x.lower() == 'e' or x.lower() == 'end' or x.lower() == 'q' or x.lower() == 'quit' or x.lower() == '.q': sys.exit()
        elif x=='' or x.lower() == 'n' or x.lower() == 'next': break
        args = x.split()
        if args[0]=='s' or args[0]=='save':
            if len(args)<2:
                for p,c in padlist.items(): savePad(p, c)
            else: savePad(args[1:], gPad)
            continue
        try:
            gROOT.ProcessLine(x)
        except:
            print('command not recognized')
            continue

def savePad(args, c1=gPad, saveC=False):
    for arg in args if not isinstance(args, str) else [args]:
#         if arg.find('.') != -1: c1.SaveAs(arg)
        if os.path.basename(arg).find('.') != -1: c1.SaveAs(arg)
        else:
            dname = os.path.dirname(arg)
            if not dname: dname = '.'
            if not os.path.isdir(dname+'/png'):
                os.makedirs(dname+'/png')
            arg1 = dname+'/png/'+os.path.basename(arg)
            c1.SaveAs(arg1+'.png')
            c1.SaveAs(arg+'.eps')
            c1.SaveAs(arg+'.pdf')
            if saveC: c1.SaveAs(arg+'.C')
    return 1

def setStyle(style):
    style.SetOptStat(0)
    style.SetPadTickX(1)
    style.SetPadTickY(1)
    style.SetOptTitle(0)
    style.SetPadTopMargin(0.02)
    style.SetPadRightMargin(0.02)
    style.SetPadBottomMargin(0.10)
    style.SetPadLeftMargin(0.10)


def useDefaultStyle():
    useLHCbStyle()
def useLHCbStyle():
    gROOT.ProcessLine(".x lhcbStyle.C")
    gStyle.SetNdivisions(506, 'XYZ')

def useAtlasStyle():
    gROOT.LoadMacro("AtlasStyle.C")
    from ROOT import SetAtlasStyle
    SetAtlasStyle()
    gStyle.SetNdivisions(506, 'XYZ')

def useNxStyle():
    try:
        gROOT.LoadMacro("NvDExStyle.C")
        from ROOT import SetNvDExStyle
        SetNvDExStyle()
    except ImportError as e:
        print(e)
        gStyle.SetPadLeftMargin(0.16)
        gStyle.SetOptStat(0)
        gStyle.SetCanvasBorderMode(0);
        gStyle.SetPadBorderMode(0);
        gStyle.SetPadColor(0);
        gStyle.SetCanvasColor(0);
        gStyle.SetPadRightMargin(0.05);
        gStyle.SetPadTopMargin(0.05);
#       //   gStyle.SetTitleColor(0);
        gStyle.SetStatColor(0);
        gStyle.SetOptTitle(0);
        gStyle.SetOptStat(0);
        gStyle.SetOptFit(1111);
        gStyle.SetLegendBorderSize(0);
        gStyle.SetPadTickX(1)
        gStyle.SetPadTickY(1)
#       //   gStyle.SetHistFillStyle(0);
#       //   gStyle.SetHistFillColor(2);
        gStyle.SetFillStyle(0);
        gStyle.SetLineWidth(1);
        gStyle.SetHistLineWidth(2);
        gStyle.SetMarkerStyle(4);
        gStyle.SetNdivisions(506, "XYZ");
        gStyle.SetPalette(55);
        pass

def savehistory(dir1=os.environ["HOME"]):
    import rlcompleter, readline
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set show-all-if-ambiguous On')
 
    import atexit
    f = os.path.join(dir1, ".python_history")
    try:
        readline.read_history_file(f)
    except IOError:
        pass
    atexit.register(readline.write_history_file, f)

def getRDF(pattern, treeName=None):
    '''Take the pattern and return a TChain and a RDataFrame'''
    from ROOT import TChain, RDataFrame
    import glob

    if treeName is None: treeName = 'tuple0/DecayTree'
    patterns = [pattern] if isinstance(pattern, str) else pattern

    ch1 = TChain(treeName)
    for pn in patterns:
        for f in glob.glob(pn): ch1.Add(f)

    return ch1, RDataFrame(ch1)


if __name__ == '__main__':
    print('test')
    tc = bcolors()
    tc.show('WARNING','testing')
    tc.show('blue','testing')
