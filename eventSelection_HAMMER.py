import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from collections import OrderedDict

from HAMMER.Tools import CMS_lumi
from HAMMER.Tools.Common import *
from HAMMER.Analyzer import *

parser = OptionParser()

parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')

parser.add_option('-s',"--sig", action="store_true",  dest="isSignal")
parser.add_option('-b',"--bkg", action="store_false", dest="isSignal")

parser.add_option('-c', '--config', metavar='FILE', type='string', action='store',
                default   =   'config.json',
                dest      =   'config',
                help      =   'Configuration file in json format that is interpreted as a python dictionary')


(options, args) = parser.parse_args()
start_time = time.time()

commonc = CommonCscripts()
customc = CustomCscripts()
a = analyzer(options.input)


totalOutFile        = "total.root"
preselectionOutFile = "preselection.root"
selection1OutFile   = "selection1.root"
selection2OutFile   = "selection2.root"


out_vars = ['nFatJet','FatJet_pt']
a.GetActiveNode().Snapshot(out_vars,totalOutFile,'total',lazy=False,openOption='RECREATE')


newcolumns = VarGroup("newcolumns")
newcolumns.Add("deltaEta","FatJet_eta[0]-FatJet_eta[1]")
newcolumns.Add("Jet0_HPass","FatJet_pt[0]>300 && FatJet_msoftdrop[0]<140 && FatJet_msoftdrop[0]>110 && FatJet_btagHbb[0]>0.7")
newcolumns.Add("Jet1_HPass","FatJet_pt[1]>300 && FatJet_msoftdrop[1]<140 && FatJet_msoftdrop[1]>110 && FatJet_btagHbb[1]>0.7")

preselectionCuts    = CutGroup("preselectionCuts")
preselectionCuts.Add("nFatJet","nFatJet>1")
preselectionCuts.Add("Leading jets eta","abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4")
preselectionCuts.Add("Leading jets delta eta","abs(FatJet_eta[0] - FatJet_eta[1]) < 1.5")
preselectionCuts.Add("Leading jets Pt","FatJet_pt[0] > 200 && FatJet_pt[1] > 200")

a.Apply([newcolumns,preselectionCuts])
out_vars = ['nFatJet','Jet0_HPass','Jet1_HPass','FatJet_pt','FatJet_etat','deltaEta']
a.GetActiveNode().Snapshot(out_vars,preselectionOutFile,'preselection',lazy=False)

selection1Cuts = CutGroup("selection1Cuts")
selection1Cuts.Add("Higgs requirement","Jet0_HPass || Jet1_HPass")
a.Apply([selection1Cuts])
a.GetActiveNode().Snapshot(out_vars,selection1OutFile,'selection1',lazy=False)

selection2Cuts      = CutGroup("selection2Cuts")
otherJetCut         = "(Jet0_HPass==1 && FatJet_msoftdrop[1]>50 && FatJet_btagHbb[1]>0.7) || (Jet1_HPass==1 && FatJet_msoftdrop[0]>50 && FatJet_btagHbb[0]>0.7)"
selection2Cuts.Add("Loose H requirement",otherJetCut)
a.Apply([selection2Cuts])
a.GetActiveNode().Snapshot(out_vars,selection2OutFile,'selection2',lazy=False)

mergeRootF      = "hadd -f {0} preselection.root selection1.root selection2.root total.root".format(options.output)
cleanUp         = "rm preselection.root selection1.root selection2.root total.root"
print(mergeRootF)
os.system(mergeRootF)
print(cleanUp)
os.system(cleanUp) 


print("Total time: "+str((time.time()-start_time)/60.) + ' min')