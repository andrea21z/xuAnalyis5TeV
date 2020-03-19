import os, sys
#from config import *
from config import GetLumi, path, pathBS
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from plotter.TopHistoReader import TopHistoReader, HistoManager
from plotter.Plotter import Stack, HistoComp
from framework.looper import looper
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT, TLegend, TCanvas
gROOT.SetBatch(1)
import argparse

parser = argparse.ArgumentParser(description='To select masses and year')
parser.add_argument('--year',         default=2018   , help = 'Year')
parser.add_argument('--mStop',        default=275  , help = 'Stop mass')
parser.add_argument('--mLSP',         default=100  , help = 'Neutralino mass')
parser.add_argument('--BS',          action='store_true'  , help = 'Do BS region')
parser.add_argument('--SR',          action='store_true'  , help = 'Do signal region')
#parser.add_argument('--verbose', '-v'    , default=0     , help = 'Activate the verbosing')
#parser.add_argument('--process', '-p'    , default=''    , help = 'Run a given process')
#parser.add_argument('--nSlots','-n'      , default=1           , help = 'Number of slots')
parser.add_argument('--sendJobs','-j'   , action='store_true'  , help = 'Send jobs!')
 
#args = parser.parse_args()
args, unknown = parser.parse_known_args()

ms   = int(args.mStop)
ml   = int(args.mLSP)
year = int(args.year) if args.year.isdigit() else args.year
sendJobs = args.sendJobs
#nSlots = args.nSlots
#argprocess = args.process
#if   ',' in argprocess: argprocess = argprocess.replace(' ', '').split(',')
#elif argprocess != '' : argprocess = [argprocess]



region = 'SR'
if args.BS: region = 'BS'
if args.SR: region = 'SR'
#Tm_LSP, Tm_stop
treeName="MiniTree"

GetOutPath = lambda year, region : '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/stop/SS/%s/%s/'%(str(year), region)
outpath = GetOutPath(year, region) 
model = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/TopPlots/DrawMiniTrees/NNtotal_model2.h5'

vardic = {
'mt2'      : 'm_{T2} (GeV)',
'mt2_4bins': 'm_{T2} (GeV)',
'met'      : 'MET (GeV)',
'mll'      : 'm_{e#mu} (GeV)',
'dnn'      : 'DNN score',
'count'    : 'Counts',
'dileppt'  : 'p_{T}^{e#mu} (GeV)',
'deltaphi' : '#Delta#phi (rad/#pi)',
'deltaeta' : '#Delta#eta',
'ht'       : 'H_{T} (GeV)',
'lep0pt'   : 'Leading lepton p_{T} (GeV)',
'lep1pt'   : 'Subleading lepton p_{T} (GeV)',
'lep0eta'  : 'Leading lepton #eta',
'lep1eta'  : 'Subleading lepton #eta',
'njets'    : 'Jet multiplicity',
'nbtags'   : 'b-tag multiplicity',
}
#vardic = { 'nbtags'    : 'b-tag multiplicity'}

processDic = {
2018 : {
       'Chargeflips' : 'TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad',
       'PromptSS' : 'TTWJetsToLNu, TTWJetsToQQ, WZTo3LNu, ZZTo4L, TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
       'Semileptonictt' : 'TTToSemiLeptonic',
       'Othernonprompt':'WJetsToLNu_MLM,TTTo2L2Nu, TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, ZZTo2L2Nu, ZZTo2L2Q',
       'data' : 'SingleMuon_2018, EGamma_2018, MuonEG_2018', #DoubleMuon_2018
     },
2017 : {
       'Chargeflips' : 'TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad',
       'PromptSS' : 'TTWJetsToLNu, TTWJetsToQQ, WZTo3LNu, ZZTo4L, TTZToLL_M_1to10, TTZToLLNuNu_M_10_a, TTZToQQ',
       'Semileptonictt' : 'TTToSemiLeptonic',
       'Othernonprompt':'WJetsToLNu_MLM,TTTo2L2Nu, TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad, DYJetsToLL_M_10to50_MLM, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, ZZTo2L2Nu, ZZTo2L2Q',
       'data' : 'MuonEG_2017,SingleElectron_2017,SingleMuon_2017',#,DoubleEG_2017,DoubleMuon_2017',
     },
2016 : {
       'Chargeflips' : 'TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad',
       'PromptSS' : 'TTWJetsToLNu, TTWJetsToQQ, WZTo3LNu, ZZTo4L, TTZToLL_M_1to10_MLM, TTZToLLNuNu_M_10_a, TTZToQQ',
       'Semileptonictt' : 'TTToSemiLeptonic',
       'Othernonprompt':'WJetsToLNu_MLM,TTTo2L2Nu, TTTo2L2Nu, tbarW_noFullHad, tW_noFullHad, DYJetsToLL_M_10to50, DYJetsToLL_M_50_a, WWTo2L2Nu, WZTo2L2Q, ZZTo2L2Nu, ZZTo2L2Q',
       'data' : 'MuonEG_2016,SingleElectron_2016,SingleMuon_2016',#,DoubleEG_2017,DoubleMuon_2017',
      },
}


legendNames = {
'Chargeflips' : 'Charge flips',
'PromptSS' : 'Prompt SS',
'Semileptonictt' : 'Semileptonic t#bar{t}',
'Othernonprompt' : 'Other nonprompt',
}

colors = {
'Chargeflips' : kAzure+2,
'PromptSS' : kAzure+3,
'Semileptonictt' : kRed-9,
'Othernonprompt': kGray,
'data' : 1,
}

selection = ''

loopcode = '''
values = [%i,  %i, t.TDilep_Pt, t.TDeltaPhi, t.TDeltaEta, t.TLep0Pt, t.TLep0Eta, t.TLep1Pt, vmet, t.TLep1Eta, vmll, vmt2, vht]
prob1 = self.pd1.GetProb(values)
'''%(ms, ml)


def GetHistosFromLooper(year, ecut = '(t.TStatus == 1 or t.TStatus == 22)', processes = ['Chargeflips','PromptSS'], outfolder = '/'):
#l = looper(path=path[year], nSlots = 6, treeName = 'MiniTree', options = 'merge', nEvents = 1000, outpath=outpath+'tempfiles/')
  l = looper(path=path[year] if not region=='BS' else pathBS[year], nSlots = 20, treeName = 'MiniTree', options = 'merge', outpath = GetOutPath(year, region)+'/'+outfolder+'/tempfiles/', readOutput=True)
  l.AddHeader('from framework.mva import ModelPredict\n')
  l.AddInit('      self.pd1 = ModelPredict("%s")\n'%model)

  for p in processes: l.AddSample(p,  processDic[year][p])

  syst = 'MuonEff, ElecEff, Trig, JES, JER, MuonES, Uncl, Btag, MisTag, PU, TopPt'
  #if year != 2018: syst += ', Pref'
  systlist = [x+y for x in syst.replace(' ','').split(',') for y in ['Up','Down']]
  l.AddSyst(systlist)
  l.AddLoopCode(loopcode)

  l.AddExpr('deltaphi', 'TDeltaPhi', 'abs(TDeltaPhi)/3.141592')
  l.AddExpr('deltaeta', 'TDeltaEta', 'abs(TDeltaEta)')
  l.AddExpr('weight1', [], '1')
  l.AddExpr('vpd', '', 'prob1', True) # True because prob1 has to be defined before
  l.AddExpr('vmet', ['TMET'], 'TMET')
  l.AddExpr('vmt2', ['TMT2'], 'TMT2')
  l.AddExpr('vht',  ['THT' ], 'THT')
  l.AddExpr('vmll', ['TMll'], 'TMll')
  l.AddExpr('exprW', ['TWeight'], 'TWeight')

  l.AddSelection(selection)
  weight = 'exprW'
  #cut = 'TMET > 50 and TMT2 > 80 and TNJets >= 2 and TNBtags >= 1 and TPassDilep and %s'%ecut
  #l.AddCut(cut, ['TMET', 'TMT2', 'TNJets', 'TNBtags', 'TPassDilep'])

  l.AddCut('TPassDilep == 1', 'TPassDilep')
  if region != 'BS':
    l.AddCut('TMET >= 50', 'TMET')
    l.AddCut('TMT2 >= 80', 'TMT2')
  l.AddCut('TNJets >= 2', 'TNJets')
  l.AddCut('TNBtags >= 1', 'TNBtags')
  l.AddCut(ecut, [])
  cut = ''

  l.AddHisto('vpd',   'dnn',  5, 0, 1,   weight = weight, cut = '')
  l.AddHisto('vpd',   'count',  1, 0, 2,   weight = weight, cut = '')
  l.AddHisto('TMll', 'mll', 10, 0, 300, weight = weight, cut = '')
  l.AddHisto('TMET', 'met', 10, 50, 300, weight = weight, cut = '')
  l.AddHisto('TMT2', 'mt2', 8, 80, 160, weight = weight, cut = '')
  l.AddHisto('TMT2', 'mt2_4bins', 4, 80, 160, weight = weight, cut = '')
  l.AddHisto('TDilep_Pt', 'dileppt', 10, 0, 300, weight = weight, cut = '')
  l.AddHisto('TLep0Pt', 'lep0pt', 5, 0, 150, weight = weight, cut = '')
  l.AddHisto('TLep1Pt', 'lep1pt', 10, 0, 300, weight = weight, cut = '')
  l.AddHisto('TLep0Eta', 'lep0eta', 8, -2.4, 2.4, weight = weight, cut = '')
  l.AddHisto('TLep1Eta', 'lep1eta', 8, -2.4, 2.4, weight = weight, cut = '')
  l.AddHisto('deltaphi', 'deltaphi', 8, 0, 1, weight = weight, cut = '')
  l.AddHisto('deltaeta', 'deltaeta', 8, 0, 5, weight = weight, cut = '')
  l.AddHisto('TJet0Pt', 'jet0pt', 10, 0, 450, weight = weight, cut = '')
  l.AddHisto('TJet1Pt', 'jet1pt', 6, 0, 300, weight = weight, cut = '')
  l.AddHisto('TJet0Eta', 'jet0eta', 8, -2.4, 2.4, weight = weight, cut = '')
  l.AddHisto('TJet1Eta', 'jet1eta', 8, -2.4, 2.4, weight = weight, cut = '')
  l.AddHisto('THT', 'ht', 8, 0, 800, weight = weight, cut = '')
  l.AddHisto('TNJets', 'njets', 6, 1.5, 7.5, weight = weight, cut = '')
  l.AddHisto('TNBtags', 'nbtags', 3, 0.5, 3.5, weight = weight, cut = '')

  out = l.Run()
  return out

if isinstance(year, str):
  promptSS = {}; nonpromptSS = {}; nonpromptOS = {}
  for y in [2016, 2017, 2018]:
    promptSS   [y] = GetHistosFromLooper(y, ecut = 't.TIsSS and (t.TStatus == 1 or  t.TStatus == 22)', processes = ['Chargeflips','PromptSS', 'data'], outfolder='promptSS')
    nonpromptSS[y] = GetHistosFromLooper(y, ecut = 't.TIsSS and (t.TStatus != 1 and t.TStatus != 22)', processes = ['Semileptonictt','Othernonprompt'], outfolder='nonpromptSS')
    nonpromptOS[y] = GetHistosFromLooper(y, ecut = 'not t.TIsSS and (t.TStatus != 1 and t.TStatus != 22)', processes = ['Semileptonictt','Othernonprompt'], outfolder='nonpromptOS')
else:
  promptSS    = GetHistosFromLooper(year, ecut = 't.TIsSS and (t.TStatus == 1 or  t.TStatus == 22)', processes = ['Chargeflips','PromptSS', 'data'], outfolder='promptSS')
  nonpromptSS = GetHistosFromLooper(year, ecut = 't.TIsSS and (t.TStatus != 1 and t.TStatus != 22)', processes = ['Semileptonictt','Othernonprompt'], outfolder='nonpromptSS')
  nonpromptOS = GetHistosFromLooper(year, ecut = 'not t.TIsSS and (t.TStatus != 1 and t.TStatus != 22)', processes = ['Semileptonictt','Othernonprompt'], outfolder='nonpromptOS')
if sendJobs: exit()

ss = {}
if isinstance(year, str):
  for y in [2016, 2017, 2018]:
    ss[y] = {}
    for k in promptSS[y]  .keys(): ss[y][k] = promptSS[y][k]
    for k in nonpromptSS[y].keys(): ss[y][k] = nonpromptSS[y][k]
else: 
  for k in promptSS   .keys(): ss[k] = promptSS[k]
  for k in nonpromptSS.keys(): ss[k] = nonpromptSS[k]

def GetDDOS(year, ss, nonpromptOS):
  lumi = GetLumi(year)*1000
  hDDOSdic = {}
  for var in vardic.keys(): 
    hDDOS = ss['data'][var].Clone()
    nb = hDDOS.GetNbinsX()
    for ib in range(0, nb+1):
      dataSS   = ss['data'][var].GetBinContent(ib)
      promptSS = (ss['PromptSS'][var].GetBinContent(ib) + ss['Chargeflips'][var].GetBinContent(ib))*lumi
      mcOS     = (nonpromptOS['Semileptonictt'][var].GetBinContent(ib) + nonpromptOS['Othernonprompt'][var].GetBinContent(ib))*lumi
      mcSS     = (ss['Semileptonictt'][var].GetBinContent(ib) + ss['Othernonprompt'][var].GetBinContent(ib))*lumi
      #mcOS     = (nonpromptOS['Semileptonictt'][var].GetBinContent(ib))*lumi
      #mcSS     = (ss['Semileptonictt'][var].GetBinContent(ib))*lumi
      ddbin    = (dataSS - promptSS)*( (mcOS/mcSS if mcSS != 0 else 1) if region != 'SR' else 4.4)
      #print "[%i] : (dataSS [%1.2f] - promptSS [%1.2f])*(mcOS [%1.2f] / mcSS [%1.2f]) = %1.2f || R = %1.2f"%(ib, dataSS, promptSS, mcOS, mcSS, ddbin, mcOS/mcSS if mcSS != 0 else 0)
      hDDOS.SetBinContent(ib, ddbin)
    hDDOSdic[var] = hDDOS
    if var == 'count': print 'Count: ', hDDOSdic[var].Integral()
  return hDDOSdic

if isinstance(year, str):
  for y in [2016, 2017, 2018]:
    hDDOSdic = GetDDOS(y, ss[y], nonpromptOS[y]) 
    nonpromptOS[y]['DDOS'] = hDDOSdic
    #ss[y]['MCOS'] = nonpromptOS[y]['Semileptonictt']
else:
  hDDOSdic = GetDDOS(year, ss, nonpromptOS) 
  nonpromptOS['DDOS'] = hDDOSdic

prSS = ['PromptSS', 'Chargeflips', 'Othernonprompt', 'Semileptonictt']
if isinstance(year, str):
  hmSS16 = HistoManager(prSS, path = path[2016] if not region=='BS' else pathBS[2016], processDic = processDic[2016], lumi = GetLumi(2016)*1000, indic=ss[2016])
  hmSS17 = HistoManager(prSS, path = path[2017] if not region=='BS' else pathBS[2017], processDic = processDic[2017], lumi = GetLumi(2017)*1000, indic=ss[2017])
  hmSS   = HistoManager(prSS, path = path[2018] if not region=='BS' else pathBS[2018], processDic = processDic[2018], lumi = GetLumi(2018)*1000, indic=ss[2018])
  hmSS.ScaleByLumi(); hmSS16.ScaleByLumi(); hmSS17.ScaleByLumi();
  hmSS.SetHistoName("mt2")
  hmSS.Add(hmSS17).Add(hmSS16)
else:
  hmSS = HistoManager(prSS, path = path[year] if not region=='BS' else pathBS[year], processDic = processDic[year], lumi = GetLumi(year)*1000, indic=ss)
hmSS.SetDataName('data')

prOS = ['Othernonprompt', 'Semileptonictt']
#hmOS = HistoManager(prOS, path = path[year] if not region=='BS' else pathBS[year], processDic = processDic[year], lumi = GetLumi(year)*1000, indic=ss)
if isinstance(year, str):
  hmOS16 = HistoManager(prOS, path = path[2016] if not region=='BS' else pathBS[2016], processDic = processDic[2016], lumi = GetLumi(2016)*1000, indic=nonpromptOS[2016])
  hmOS17 = HistoManager(prOS, path = path[2017] if not region=='BS' else pathBS[2017], processDic = processDic[2017], lumi = GetLumi(2017)*1000, indic=nonpromptOS[2017])
  hmOS   = HistoManager(prOS, path = path[2018] if not region=='BS' else pathBS[2018], processDic = processDic[2018], lumi = GetLumi(2018)*1000, indic=nonpromptOS[2018])
  hmOS.SetDataName('DDOS');  hmOS16.SetDataName('DDOS'); hmOS17.SetDataName('DDOS')
  hmOS.ScaleByLumi(); hmOS16.ScaleByLumi(); hmOS17.ScaleByLumi();
  hmOS.SetHistoName("mt2")
  hmOS.Add(hmOS17).Add(hmOS16)
else: 
  hmOS = HistoManager(prOS, path = path[year] if not region=='BS' else pathBS[year], processDic = processDic[year], lumi = 1, indic=ss)
  hmOS.SetDataName('DDOS')

def save(name, hm, processes = [''], oname = ''):
  hm.SetHisto(name)
  opath = '/nfs/fanae/user/juanr/www/stoplegacy/SS/%s/%s/'%(year,region)
  if not isinstance(year, str): hm.Save(outname=outpath+'/'+name, htag = '')
  s = Stack(outpath=opath+'/plots%s/'%oname)
  s.SetLegendName(legendNames)
  s.SetColors(colors)
  s.SetProcesses(processes)
  s.SetLumi(GetLumi(year) if not isinstance(year, str) else GetLumi(2016)+GetLumi(2017)+GetLumi(2018))
  s.SetOutName(name)
  s.SetHistosFromMH(hm)
  s.DrawStack(vardic[name] if name in vardic.keys() else '', 'Events')

def saveOSSS(hname, hOS, hSS):
  opath = '/nfs/fanae/user/juanr/www/stoplegacy/SS/%s/%s/'%(year,region)
  s = HistoComp(outpath=opath+'/RatioOSSS/', doNorm = False, doRatio = True)
  s.autoRatio = True
  #s.SetTextLumi('Normalized distributions', texlumiX = 0.12)
  s.SetLumi(GetLumi(year) if not isinstance(year, str) else GetLumi(2016)+GetLumi(2017)+GetLumi(2018))
  hOS.SetFillColor(0)
  s.AddHisto(hOS,  'hist', 'hist', "Semileptonic t#bar{t} OS", color=kAzure+2)
  s.AddHisto(hSS,  'hist', 'hist', "Semileptonic t#bar{t} SS", color=kOrange+1)
  s.SetLegendPos(0.65, 0.80, 0.88, 0.90, ncol=1)
  s.SetRatioMin(0.); s.SetRatioMax(10)
  s.SetXtitle(vardic[hname])
  s.SetOutName(hname)
  s.Draw()

#for v in vardic.keys(): save(v, hmSS, prSS, 'SS')
for v in vardic.keys(): save(v, hmOS, prOS, 'OS')
for v in vardic.keys(): 
  hmOS.SetHisto(v)
  hmSS.SetHisto(v)
  hOS = hmOS.GetHisto('Semileptonictt', v); hOS.Add(hmOS.GetHisto('Othernonprompt',v))
  hSS = hmSS.GetHisto('Semileptonictt', v); hSS.Add(hmSS.GetHisto('Othernonprompt', v))
  saveOSSS(v, hOS, hSS )
#for v in vardic.keys(): saveOSSS(v, nonpromptOS['Semileptonictt'][v], ss['Semileptonictt'][v])
