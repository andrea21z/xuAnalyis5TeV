import os, sys
from plotterconf import *
basepath = os.path.abspath(__file__).rsplit('/xuAnalysis/',1)[0]+'/xuAnalysis/'
sys.path.append(basepath)
from ROOT.TMath import Sqrt as sqrt
from ROOT import kRed, kOrange, kBlue, kTeal, kGreen, kGray, kAzure, kPink, kCyan, kBlack, kSpring, kViolet, kYellow
from ROOT import TCanvas, gROOT
gROOT.SetBatch(1)
from plotter.WeightReader import WeightReader
from scripts.DrellYanDataDriven import DYDD

outpath = '/nfs/fanae/user/juanr/CMSSW_10_2_13/src/tt5TeV/histos/'

def CreateDatacard(name = 'ttxsec_ElMu', verbose = True):
  sig = 'tt'
  pathToFile = '/nfs/fanae/user/juanr/CMSSW_10_2_5/src/xuAnalysis/modules/CreateDatacards.py'
  pathOut    = outpath
  #unc = 'MuonEff, ElecEff, Trig, Pref, MuonES, Btag, MisTag, TopPt, FSR, ISR, UE, PU, Uncl, JESCor, JESUnCor, JER' # mtop, hdamp
  #unc = 'MuonEff, ElecEff, Trig, Pref, MuonES, Btag, MisTag, TopPt, FSR, ISR, UE,  Uncl, JESCor, JESUnCor, hdamp' # mtop, hdamp
  unc = "MuonEff, ElecEff, TrigEff, Prefire, JES, JER, Prefire, PU, PDF, Scale, ISR, FSR, hdamp, UE"
  bkg  = 'VV, tW, Nonprompt, DY'
  norm = '1.30, 1.20, 1.50, 1.30, 1'
  signal = 'tt'
  command = 'python %s %s -p %s -s %s -u "%s" -b "%s" -n "%s"'%(pathToFile, name, pathOut, signal, unc, bkg, norm)
  if verbose: print 'Executing %s ...'%command
  os.system(command)

def SaveHisto(name, chan, level, outname='', rebin=1):
  hname = '%s_%s_%s'%(name, chan, level)
  if outname == '': outname = hname
  honame = hname if level != '2jetsnomet' else '%s_%s_%s'%(name, chan, '2jets')

  thr = TopHistoReader(path)
  thr.SetLumi(296.1)
  systematics = 'MuonEff, ElecEff, TrigEff, JES, JER, PU, Prefire, hdamp, UE'

  processes = processDic.keys()
  hm = HistoManager(processes, systematics, '', path=path, processDic=processDic, lumi=Lumi)
  hm.SetHisto(hname, rebin)

  if level == '2jetsnomet': level = '2jets'
  d = DYDD(path,outpath,chan,level, DYsamples=processDic['DY'], DataSamples=processDic['data'], lumi=Lumi, histonameprefix='', hname = 'DYHistoElMu')# if chan == 'ElMu' else 'DYHisto')
  DYy, DYerr = d.GetDYDD()
  DYMC = hm.indic['DY'][hname].Integral()
  #hm.indic['DY'][hname].Scale(DYy/DYMC if DYMC!=0 else 1)

  # Add ISR, FSR
  nom   = hm.indic['tt'][hname].Clone('nom')
  ynom  = thr.GetNamedHisto(honame, 'TTPS').Integral()
  isrup = thr.GetNamedHisto(honame+'_ISRUp', 'TTPS').Integral()
  isrdo = thr.GetNamedHisto(honame+'_ISRDown', 'TTPS').Integral()
  fsrup = thr.GetNamedHisto(honame+'_FSRUp', 'TTPS').Integral()
  fsrdo = thr.GetNamedHisto(honame+'_FSRDown', 'TTPS').Integral()

  hisrup = nom.Clone('isrup'); hisrup.Scale(1+(isrup-ynom)/ynom)
  hisrdo = nom.Clone('isrdo'); hisrdo.Scale(1+(isrdo-ynom)/ynom)
  hfsrup = nom.Clone('fsrup'); hfsrup.Scale(1+(fsrup-ynom)/ynom)
  hfsrdo = nom.Clone('fsrdo'); hfsrdo.Scale(1+(fsrdo-ynom)/ynom)
  hm.indic['tt'][hname+'_'+'ISRUp'  ] = hisrup
  hm.indic['tt'][hname+'_'+'ISRDown'] = hisrdo
  hm.indic['tt'][hname+'_'+'FSRUp'  ] = hfsrup
  hm.indic['tt'][hname+'_'+'FSRDown'] = hfsrdo

  # Add PDF, Scale ME
  pathToTrees = '/pool/phedexrw/userstorage/juanr/5TeV5apr2020/'
  motherfname = 'TT_TuneCP5_5p02TeV'
  w = WeightReader(path, '',chan, level, sampleName='TT', pathToTrees=pathToTrees, motherfname=motherfname, PDFname='PDFweights', ScaleName='ScaleWeights', lumi=296.1, histoprefix='')
  pdfunc   = w.GetPDFandAlphaSunc()
  scaleunc = w.GetMaxRelUncScale()

  hpdfup = nom.Clone('pdfup'); hpdfup.Scale(1+pdfunc)
  hpdfdo = nom.Clone('pdfdo'); hpdfdo.Scale(1-pdfunc)
  hmeup  = nom.Clone('meup' ); hmeup .Scale(1+scaleunc)
  hmedo  = nom.Clone('medo' ); hmedo .Scale(1-scaleunc)
  hm.indic['tt'][hname+'_'+'PDFUp'    ] = hpdfup
  hm.indic['tt'][hname+'_'+'PDFDown'  ] = hpdfdo
  hm.indic['tt'][hname+'_'+'ScaleUp'  ] = hmeup
  hm.indic['tt'][hname+'_'+'ScaleDown'] = hmedo

  hm.Save(outpath+'%s'%(outname))

# Create xsec datacards
level = '2jets'
for chan in ['ElMu', 'MuMu', 'ElEl']:
  SaveHisto('Lep0Eta', chan, level, outname='ttxsec_%s'%chan, rebin=50)
  CreateDatacard(name = 'ttxsec_%s'%chan)
exit()

# Save rootfiles with final histograms
level = 'dilepton'
SaveHisto('DYMass', 'ElEl', level, rebin=5)
SaveHisto('DYMass', 'MuMu', level, rebin=5)

# 2jets but no met for ee, mumu
level = '2jetsnomet'
SaveHisto('MET', 'ElEl', level, rebin=5)
SaveHisto('MET', 'MuMu', level, rebin=5)

# Electron and muon for ElMu
chan = 'ElMu'
for level in ['dilepton', '2jets']:
  for tag in ['Elec', 'Muon']:
    SaveHisto(tag+'Pt', chan, level, rebin=5)
    SaveHisto(tag+'Eta', chan, level, rebin=5)
    SaveHisto(tag+'Phi', chan, level, rebin=5)

# Kinematic variables
# NJets, HT, MET, Lep0Pt, Lep1Pt, Lep0Eta, Lep1Eta, Lep0Phi, Lep1Phi, DilepPt, InvMass, Jet0Pt, Jet1Pt, JetAllPt
for level in ['dilepton', '2jets']:
  for chan in ['ElEl', 'MuMu', 'ElMu']:
    SaveHisto('NJets', chan, level, rebin=1)
    SaveHisto('HT', chan, level, rebin=1)
    SaveHisto('MET', chan, level, rebin=1)
    SaveHisto('Lep0Pt', chan, level, rebin=1)
    SaveHisto('Lep1Pt', chan, level, rebin=1)
    SaveHisto('Lep0Eta', chan, level, rebin=1)
    SaveHisto('Lep1Eta', chan, level, rebin=1)
    SaveHisto('DilepPt', chan, level, rebin=1)
    SaveHisto('InvMass', chan, level, rebin=1)
    SaveHisto('Jet0Pt', chan, level, rebin=1)
    SaveHisto('Jet1Pt', chan, level, rebin=1)
    #SaveHisto('JetAllPt', chan, level, rebin=1)
