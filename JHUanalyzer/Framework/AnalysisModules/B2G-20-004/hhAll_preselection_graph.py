import ROOT
ROOT.ROOT.EnableImplicitMT(4)

import time, os
from optparse import OptionParser
from  array import array

from JHUanalyzer.Analyzer.analyzer import analyzer, Group, VarGroup, CutGroup, Nminus1
from JHUanalyzer.Tools.Common import openJSON,CutflowHist
from JHUanalyzer.Analyzer.Cscripts import CommonCscripts, CustomCscripts
commonc = CommonCscripts()
customc = CustomCscripts()

parser = OptionParser()

parser.add_option('-i', '--input', metavar='F', type='string', action='store',
                default   =   '',
                dest      =   'input',
                help      =   'A root file or text file with multiple root file locations to analyze')
parser.add_option('-o', '--output', metavar='FILE', type='string', action='store',
                default   =   'output.root',
                dest      =   'output',
                help      =   'Output file name.')
parser.add_option('-c', '--config', metavar='FILE', type='string', action='store',
                default   =   'config.json',
                dest      =   'config',
                help      =   'Configuration file in json format that is interpreted as a python dictionary')
parser.add_option('-y', '--year', metavar='FILE', type='string', action='store',
                default   =   '',
                dest      =   'year',
                help      =   'Year (16,17,18)')
parser.add_option('-d', '--doublebtagger', metavar='F', type='string', action='store',
                default   =   'btagHbb',
                dest      =   'doublebtagger',
                help      =   'Variable name in NanoAOD for double b tagger to be used. btagHbb (default), deepTagMD_HbbvsQCD, deepTagMD_ZHbbvsQCD, btagDDBvL')
parser.add_option('-J', '--JES', metavar='F', type='string', action='store',
                default   =   'nom',
                dest      =   'JES',
                help      =   'nom, up, or down')
parser.add_option('-R', '--JER', metavar='F', type='string', action='store',
                default   =   'nom',
                dest      =   'JER',
                help      =   'nom, up, or down')
parser.add_option('-a', '--JMS', metavar='F', type='string', action='store',
                default   =   'nom',
                dest      =   'JMS',
                help      =   'nom, up, or down')
parser.add_option('-b', '--JMR', metavar='F', type='string', action='store',
                default   =   'nom',
                dest      =   'JMR',
                help      =   'nom, up, or down')

(options, args) = parser.parse_args()

start_time = time.time()

# Initialize
print("Start analyzer....")
a = analyzer(options.input)

# Example of how to calculate MC normalization for luminosity
if '_loc.txt' in options.input: setname = options.input.split('/')[-1].split('_loc.txt')[0]
elif '.root' in options.input: setname = options.input.split('/')[-1].split('_hh'+options.year+'.root')[0]
else: setname = ''
if os.path.exists(options.config):
    print('JSON config imported')
    c = openJSON(options.config)
    if setname != '' and not a.isData:
        xsec = c['XSECS'][setname]
        lumi = c['lumi']
    else: 
        xsec = 1.
        lumi = 1.
if not a.isData: norm = (xsec*lumi)/a.genEventCount
else: norm = 1.

##JECs for actual values.
lead = {}
sublead = {}
if not a.isData:
    if options.JES != 'nom':
        lead['JEScorr'] = 'FatJet_corr_JES_Total'+options.JES.capitalize()+"[0]"
        sublead['JEScorr'] = 'FatJet_corr_JES_Total'+options.JES.capitalize()+"[1]"
    else:
        lead['JEScorr'] = "1.0"
        sublead['JEScorr'] = "1.0"
    lead['JERcorr'] = 'FatJet_corr_JER_'+options.JER+"[0]"
    sublead["JERcorr"] = 'FatJet_corr_JER_'+options.JER+"[1]"
    lead["JMScorr"] = 'FatJet_corr_JMS_'+options.JMS+"[0]"
    sublead["JMScorr"] = 'FatJet_corr_JMS_'+options.JMS+"[1]"
    lead["JMRcorr"] = 'FatJet_groomed_corr_JMR_'+options.JMR+"[0]"
    sublead["JMRcorr"] = 'FatJet_groomed_corr_JMR_'+options.JMR+"[1]"
if not a.isData:
    lead['pt'] = "*"+lead['JEScorr']+"*"+lead['JERcorr']
    sublead['pt'] = "*"+sublead['JEScorr']+"*"+sublead['JERcorr']
    lead['SDmass'] = "*"+lead['JEScorr']+"*"+lead['JERcorr']
    sublead['SDmass'] = "*"+sublead['JEScorr']+"*"+sublead['JERcorr']
    if 'ttbar' not in setname:
        lead['SDmass'] += "*"+lead['JMScorr']+"*"+lead['JMRcorr']
        sublead['SDmass'] += "*"+sublead['JMScorr']+"*"+sublead['JMRcorr']
###Apply corrections
# if not a.isData:
#     mass0 = "FatJet_msoftdrop_nom[0]"+lead['SDmass']
#     mass1 = "FatJet_msoftdrop_nom[1]"+sublead['SDmass']
#     pt0 = "FatJet_pt_nom[0]"+lead['pt']
#     pt1 = "FatJet_pt_nom[1]"+sublead['pt']
# else:
#     mass0 = "FatJet_msoftdrop_nom[0]"
#     mass1 = "FatJet_msoftdrop_nom[1]"
#     pt0 = "FatJet_pt_nom[0]"
#     pt1 = "FatJet_pt_nom[1]"
# eta0 = "FatJet_eta[0]"
# eta1 = "FatJet_eta[1]"
# phi0 = "FatJet_phi[0]"
# phi1 = "FatJet_phi[1]"

if not a.isData:
    mass1 = "FatJet_msoftdrop_nom[0]"+lead['SDmass']
    mass0 = "FatJet_msoftdrop_nom[1]"+sublead['SDmass']
    pt1 = "FatJet_pt_nom[0]"+lead['pt']
    pt0 = "FatJet_pt_nom[1]"+sublead['pt']

else:
    mass1 = "FatJet_msoftdrop_nom[0]"
    mass0 = "FatJet_msoftdrop_nom[1]"
    pt1 = "FatJet_pt_nom[0]"
    pt0 = "FatJet_pt_nom[1]"

eta0 = "FatJet_eta[1]"
eta1 = "FatJet_eta[0]"
phi0 = "FatJet_phi[1]"
phi1 = "FatJet_phi[0]"

print("mass 0 = "+ mass0)
print("mass 1 = "+ mass1)
print("pt 0 = "+ pt0)
print("pt 1 = "+ pt1)

cutsDict = {
    'doubleBtag':[0.8,1.0],
    'doubleBtagTight':[0.8,1.0],
    'doubleBtagLoose':[0.3,1.0],
    'DeepDBtag':[0.86,1.0],
    'DeepDBtagTight':[0.86,1.0],
    #'DeepDBtagTight':[0.6,1.0],
    'DeepDBtagLoose':[0.7,1.0],
    #'DeepDBtagLoose':[0.3,1.0],
    'dak8MDZHbbtag':[0.95,1.0],
    'dak8MDZHbbtagTight':[0.95,1.0],
    'dak8MDZHbbtagLoose':[0.8,1.0],
    'dak8MDHbbtag':[0.9,1.0],
    'dak8MDHbbtagTight':[0.9,1.0],
    'dak8MDHbbtagLoose':[0.8,1.0],
}

doubleB_titles = {'btagHbb':'Double b',
                  'deepTagMD_HbbvsQCD': 'DeepAK8 MD Hbb',
                  'deepTagMD_ZHbbvsQCD': 'DeepAK8 MD ZHbb',
                  'btagDDBvL': 'Deep Double b'}
doubleB_abreviations = {'btagHbb':'doubleB',
                  'deepTagMD_HbbvsQCD': 'dak8MDHbb',
                  'deepTagMD_ZHbbvsQCD': 'dak8MDZHbb',
                  'btagDDBvL': 'DeepDB'}
doubleB_name = options.doublebtagger
doubleB_title = doubleB_titles[doubleB_name]
doubleB_short = doubleB_abreviations[doubleB_name]

if not a.isData:
### The following loads the btag calibration code in c++ so that it is available to RDF
    ROOT.gInterpreter.Declare('string year = string(TPython::Eval("options.year"));')
    btagLoadCode = '''
        string btagfilename;
        if (year == "16"){
              btagfilename = "JHUanalyzer/data/OfficialSFs/DeepCSV_2016LegacySF_V1.csv";
          }else if (year == "17"){
              btagfilename = "JHUanalyzer/data/OfficialSFs/DeepCSV_94XSF_V4_B_F.csv";
          }else if (year ==  "18"){
              btagfilename = "JHUanalyzer/data/OfficialSFs/DeepCSV_102XSF_V1.csv";
          }
        BTagCalibration calib("DeepCSV", btagfilename);

        BTagCalibrationReader reader(BTagEntry::OP_LOOSE,  // operating point
                                 "central",             // central sys type
                                 {"up", "down"});      // other sys types

        reader.load(calib,                // calibration instance
                BTagEntry::FLAV_B,    // btag flavour
                "incl");
    '''

    ROOT.gInterpreter.ProcessLine(btagLoadCode)
    print ("Btag files load time: "+str((time.time()-start_time)/60.) + ' min')

## Sets custom functions for use by RDF

a.SetCFunc(commonc.deltaPhi)
a.SetCFunc(commonc.vector)
a.SetCFunc(commonc.invariantMass)
a.SetCFunc(commonc.invariantMassThree)
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/pdfweights.cc","pdfweights")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/hemispherize.cc","hemispherize")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/triggerlookup.cc","triggerlookup")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/btagsf.cc","btagsf")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/ptwlookup.cc","ptwlookup")
customc.Import("JHUanalyzer/Framework/AnalysisModules/B2G-20-004/topCut.cc","topCut")

colnames = a.BaseDataFrame.GetColumnNames()
# Start an initial group of cuts
triggerGroup = VarGroup('triggerGroup')
trigOR = ""
if '16' in options.output: 
    trigList = ["HLT_PFHT800","HLT_PFHT900","HLT_AK8PFJet360_TrimMass30"]
    for i,t in enumerate(trigList):
            if t in colnames: 
                if not trigOR: trigOR = "("+t+"" # empty string == False
                else: trigOR += " || "+t+""
            else:
                print "Trigger %s does not exist in TTree. Skipping." %(t)
    triggerGroup.Add("triggers",""+trigOR+")")
else: 
    trigList = ["HLT_PFHT1050","HLT_AK8PFJet400_TrimMass30"]
    for i,t in enumerate(trigList):
        if t in colnames: 
            if not trigOR: trigOR = "("+t+"" # empty string == False
            else: trigOR += " || "+t+""
        else:
            print "Trigger %s does not exist in TTree. Skipping." %(t)
    triggerGroup.Add("triggers",""+trigOR+")")


# Calculate some new comlumns that we'd like to cut on
newcolumns = VarGroup("newcolumns")
newcolumns.Add("pt0",""+pt0+"")
newcolumns.Add("pt1",""+pt1+"")
newcolumns.Add("mh",""+mass0+"")
newcolumns.Add("mh1",""+mass1+"")
newcolumns.Add("lead_vect","analyzer::TLvector("+pt0+","+eta0+","+phi0+","+mass0+")")
newcolumns.Add("sublead_vect","analyzer::TLvector("+pt1+","+eta1+","+phi1+","+mass1+")")
newcolumns.Add("mhh","analyzer::invariantMass(lead_vect,sublead_vect)")
newcolumns.Add("mreduced","mhh - (mh-125.0) - (mh1-125.0)")

bbColumn = VarGroup("bbColumn")
bbColumn.Add("Hemispherized","analyzer::Hemispherize(FatJet_pt_nom,FatJet_eta,FatJet_phi,FatJet_msoftdrop_nom,nFatJet,Jet_pt,Jet_eta,Jet_phi,Jet_mass,nJet,Jet_btagDeepB)")

mbbColumn = VarGroup("mbbColumn")
mbbColumn.Add("b_lead_vect","analyzer::TLvector(Jet_pt[Hemispherized[0]],Jet_eta[Hemispherized[0]],Jet_phi[Hemispherized[0]],Jet_mass[Hemispherized[0]])")
mbbColumn.Add("b_sublead_vect","analyzer::TLvector(Jet_pt[Hemispherized[1]],Jet_eta[Hemispherized[1]],Jet_phi[Hemispherized[1]],Jet_mass[Hemispherized[1]])")
mbbColumn.Add("mbb","analyzer::invariantMass(b_lead_vect,b_sublead_vect)")
mbbColumn.Add("topMassVec","analyzer::topCut(Hemispherized[0],Hemispherized[1],Jet_pt,Jet_eta,Jet_phi,Jet_mass,nJet)")
mbbColumn.Add("topMass","topMassVec[0]")
mbbColumn.Add("topDeltaR","topMassVec[1]")

mred21Column = VarGroup("mred21Column")
mred21Column.Add("mreduced21","analyzer::invariantMassThree(sublead_vect,b_lead_vect,b_sublead_vect) - (mh1-125.0) - (mbb-125)")

# Perform final column calculations (done last after selection to save on CPU time)
correctionColumns = VarGroup("correctionColumns")
correctionColumns11 = VarGroup("correctionColumns11")
correctionColumns21 = VarGroup("correctionColumns21")

    ### Btagging correction code

if not a.isData:
    correctionColumns21.Add("btagscalefactor","analyzer::BtagSF(reader,b_lead_vect,b_sublead_vect)")

    #### Trigger correction code

    triggerFile = ROOT.TFile("TriggerWeights.root","READ")
    triggerHistTight = triggerFile.Get(doubleB_name+'tight'+options.year)
    # triggerHistLoose = triggerFile.Get(doubleB_name+'11'+options.year)
    triggerHist21 = triggerFile.Get(doubleB_name+'21'+options.year)
    ROOT.gInterpreter.ProcessLine("auto tHistT = "+doubleB_name+"tight"+options.year+";")
    correctionColumns.Add("triggerTight","analyzer::TriggerLookup(mreduced,tHistT)")
    # ROOT.gInterpreter.ProcessLine("auto tHistL = "+doubleB_name+"loose"+options.year+";")
    correctionColumns.Add("triggerLoose","analyzer::TriggerLookup(mreduced,tHistT)")
    ROOT.gInterpreter.ProcessLine("auto tHist21 = "+doubleB_name+"21"+options.year+";")
    correctionColumns21.Add("trigger21","analyzer::TriggerLookup(mreduced21,tHist21)")

## top reweighting code if necessary
if not a.isData and 'ttbar' in options.output:
    correctionColumns.Add("topptvector","analyzer::PTWLookup(nGenPart, GenPart_pdgId, GenPart_statusFlags, GenPart_pt, GenPart_eta, GenPart_phi, GenPart_mass, lead_vect, sublead_vect)")
    correctionColumns.Add("topptvectorcheck","topptvector[0]")

#### B tag SF
if "btagHbb" in options.doublebtagger:
    if options.year == '16':
        correctionColumns.Add("dbSFnomloose","1.03*("+pt0+"<350)+1.03*("+pt0+">350)")
        correctionColumns.Add("dbSFuploose","1.09*("+pt0+"<350)+1.09*("+pt0+">350)")
        correctionColumns.Add("dbSFdownloose","0.90*("+pt0+"<350)+0.90*("+pt0+">350)") 
        correctionColumns.Add("dbSFnomtight","0.95*("+pt0+"<350)+0.95*("+pt0+">350)")
        correctionColumns.Add("dbSFuptight","1.02*("+pt0+"<350)+1.02*("+pt0+">350)")
        correctionColumns.Add("dbSFdowntight","0.82*("+pt0+"<350)+0.82*("+pt0+">350)") 
    if options.year == '17':
        correctionColumns.Add("dbSFnomloose","0.96*("+pt0+"<350)+0.95*("+pt0+">350)")
        correctionColumns.Add("dbSFuploose","0.99*("+pt0+"<350)+1.01*("+pt0+">350)")
        correctionColumns.Add("dbSFdownloose","0.93*("+pt0+"<350)+0.91*("+pt0+">350)") 
        correctionColumns.Add("dbSFnomtight","0.85*("+pt0+"<350)+0.8*("+pt0+">350)")
        correctionColumns.Add("dbSFuptight","0.89*("+pt0+"<350)+0.87*("+pt0+">350)")
        correctionColumns.Add("dbSFdowntight","0.81*("+pt0+"<350)+0.76*("+pt0+">350)") 
    if options.year == '18':
        correctionColumns.Add("dbSFnomloose","0.93*("+pt0+"<350)+0.98*("+pt0+">350)")
        correctionColumns.Add("dbSFuploose","0.97*("+pt0+"<350)+1.03*("+pt0+">350)")
        correctionColumns.Add("dbSFdownloose","0.89*("+pt0+"<350)+0.94*("+pt0+">350)") 
        correctionColumns.Add("dbSFnomtight","0.89*("+pt0+"<350)+0.84*("+pt0+">350)")
        correctionColumns.Add("dbSFuptight","0.97*("+pt0+"<350)+0.89*("+pt0+">350)")
        correctionColumns.Add("dbSFdowntight","0.85*("+pt0+"<350)+0.79*("+pt0+">350)")
elif "deepTagMD_HbbvsQCD" in options.doublebtagger:

# Fit a TF1 to the distribution you want to fit. The fit result will be the nominal values of the parameters of the fit and their uncertainties 
# (so for a line, a value +/- uncertainty on each the intercept and slope).
# Take the nominal post-fit TF1 shape and evaluate it as needed to make the nominal distribution that you want.
# Make the "up" intercept uncertainty template by varying the TF1 intercept value you up 
# (so manually set the value of the parameter before evaluating the TF1) and then evaluate it as you did for the nominal distribution but fill the "up" distribution.
# Repeat (3) but for the "down" intercept value and for the "up" and "down" of the slope.
# You'll have one nominal distribution and four templates - two "up" and two "down".
# Assign them to systematic uncertainties in the 2D Alphabet json config so Combine knows about them.
    # dak8SFdict = {"16":[],"17":[],"18":[]}
    # dak8SFerrordict = {"16":[],"17":[],"18":[]}

    # correctionColumns.Add("dbSFnomloose","1.1*("+pt0+"<350)+1.1*("+pt0+">350)")
    # correctionColumns.Add("dbSFuploose","1.3*("+pt0+"<350)+1.3*("+pt0+">350)")
    # correctionColumns.Add("dbSFdownloose","0.9*("+pt0+"<350)+0.9*("+pt0+">350)") 
    # correctionColumns.Add("dbSFnomtight","1.1*("+pt0+"<350)+1.1*("+pt0+">350)")
    # correctionColumns.Add("dbSFuptight","1.3*("+pt0+"<350)+1.3*("+pt0+">350)")
    # correctionColumns.Add("dbSFdowntight","0.9*("+pt0+"<350)+0.9*("+pt0+">350)")
    if options.year == '16':
        correctionColumns.Add("dbSFnomloose","1*(300<"+pt0+" && "+pt0+"<400)+0.97*(400<"+pt0+" && "+pt0+"<500)+0.91*(500<"+pt0+" && "+pt0+"<600)+0.95*("+pt0+">600)")
        correctionColumns.Add("dbSFuploose","1.06*(300<"+pt0+" && "+pt0+"<400)+1*(400<"+pt0+" && "+pt0+"<500)+0.96*(500<"+pt0+" && "+pt0+"<600)+0.99*("+pt0+">600)")
        correctionColumns.Add("dbSFdownloose","0.94*(300<"+pt0+" && "+pt0+"<400)+0.94*(400<"+pt0+" && "+pt0+"<500)+0.86*(500<"+pt0+" && "+pt0+"<600)+0.91*("+pt0+">600)")
        correctionColumns.Add("dbSFnomtight","1*(300<"+pt0+" && "+pt0+"<400)+0.97*(400<"+pt0+" && "+pt0+"<500)+0.91*(500<"+pt0+" && "+pt0+"<600)+0.95*("+pt0+">600)")
        correctionColumns.Add("dbSFuptight","1.06*(300<"+pt0+" && "+pt0+"<400)+1*(400<"+pt0+" && "+pt0+"<500)+0.96*(500<"+pt0+" && "+pt0+"<600)+0.99*("+pt0+">600)")
        correctionColumns.Add("dbSFdowntight","0.94*(300<"+pt0+" && "+pt0+"<400)+0.94*(400<"+pt0+" && "+pt0+"<500)+0.86*(500<"+pt0+" && "+pt0+"<600)+0.91*("+pt0+">600)")
    if options.year == '17':
        correctionColumns.Add("dbSFnomloose","1.05*(300<"+pt0+" && "+pt0+"<400)+1.01*(400<"+pt0+" && "+pt0+"<500)+1.06*(500<"+pt0+" && "+pt0+"<600)+1.13*("+pt0+">600)")
        correctionColumns.Add("dbSFuploose","1.07*(300<"+pt0+" && "+pt0+"<400)+1.04*(400<"+pt0+" && "+pt0+"<500)+1.09*(500<"+pt0+" && "+pt0+"<600)+1.18*("+pt0+">600)")
        correctionColumns.Add("dbSFdownloose","1.03*(300<"+pt0+" && "+pt0+"<400)+0.98*(400<"+pt0+" && "+pt0+"<500)+1.03*(500<"+pt0+" && "+pt0+"<600)+1.08*("+pt0+">600)")
        correctionColumns.Add("dbSFnomtight","1.05*(300<"+pt0+" && "+pt0+"<400)+1.01*(400<"+pt0+" && "+pt0+"<500)+1.06*(500<"+pt0+" && "+pt0+"<600)+1.13*("+pt0+">600)")
        correctionColumns.Add("dbSFuptight","1.07*(300<"+pt0+" && "+pt0+"<400)+1.04*(400<"+pt0+" && "+pt0+"<500)+1.09*(500<"+pt0+" && "+pt0+"<600)+1.18*("+pt0+">600)")
        correctionColumns.Add("dbSFdowntight","1.03*(300<"+pt0+" && "+pt0+"<400)+0.98*(400<"+pt0+" && "+pt0+"<500)+1.03*(500<"+pt0+" && "+pt0+"<600)+1.08*("+pt0+">600)")
    if options.year == '18':
        correctionColumns.Add("dbSFnomloose","1.35*(300<"+pt0+" && "+pt0+"<400)+1.22*(400<"+pt0+" && "+pt0+"<500)+1.31*(500<"+pt0+" && "+pt0+"<600)+1.30*("+pt0+">600)")
        correctionColumns.Add("dbSFuploose","1.38*(300<"+pt0+" && "+pt0+"<400)+1.25*(400<"+pt0+" && "+pt0+"<500)+1.35*(500<"+pt0+" && "+pt0+"<600)+1.34*("+pt0+">600)")
        correctionColumns.Add("dbSFdownloose","1.32*(300<"+pt0+" && "+pt0+"<400)+1.19*(400<"+pt0+" && "+pt0+"<500)+1.27*(500<"+pt0+" && "+pt0+"<600)+1.26*("+pt0+">600)")
        correctionColumns.Add("dbSFnomtight","1.35*(300<"+pt0+" && "+pt0+"<400)+1.22*(400<"+pt0+" && "+pt0+"<500)+1.31*(500<"+pt0+" && "+pt0+"<600)+1.30*("+pt0+">600)")
        correctionColumns.Add("dbSFuptight","1.38*(300<"+pt0+" && "+pt0+"<400)+1.25*(400<"+pt0+" && "+pt0+"<500)+1.35*(500<"+pt0+" && "+pt0+"<600)+1.34*("+pt0+">600)")
        correctionColumns.Add("dbSFdowntight","1.32*(300<"+pt0+" && "+pt0+"<400)+1.19*(400<"+pt0+" && "+pt0+"<500)+1.27*(500<"+pt0+" && "+pt0+"<600)+1.26*("+pt0+">600)")
else:
    correctionColumns.Add("dbSFnomloose","1*("+pt0+"<350)+1*("+pt0+">350)")
    correctionColumns.Add("dbSFuploose","1*("+pt0+"<350)+1*("+pt0+">350)")
    correctionColumns.Add("dbSFdownloose","1*("+pt0+"<350)+1*("+pt0+">350)") 
    correctionColumns.Add("dbSFnomtight","1*("+pt0+"<350)+1*("+pt0+">350)")
    correctionColumns.Add("dbSFuptight","1*("+pt0+"<350)+1*("+pt0+">350)")
    correctionColumns.Add("dbSFdowntight","1*("+pt0+"<350)+1*("+pt0+">350)")

if not a.isData:
    if 'ttbar' in options.input:
        topstringnom = "*topptvector[0]"
        topstringup = "*topptvector[1]"
        topstringdown = "*topptvector[2]"

        correctionColumns11.Add("topptweight_tight_up","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight"+topstringup+"")
        correctionColumns11.Add("topptweight_tight_down","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight"+topstringdown+"")
        correctionColumns11.Add("topptweight_loose_up","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringup+"")
        correctionColumns11.Add("topptweight_loose_down","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringdown+"")

        correctionColumns11.Add("topptweight_tight_upFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight"+topstringup+"")
        correctionColumns11.Add("topptweight_tight_downFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight"+topstringdown+"")
        correctionColumns11.Add("topptweight_loose_upFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight"+topstringup+"")
        correctionColumns11.Add("topptweight_loose_downFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight"+topstringdown+"")

        correctionColumns11.Add("topptweight_tight_upFailHalfSF","(dbSFnomtight)*triggerTight[0]*puWeight"+topstringup+"")
        correctionColumns11.Add("topptweight_tight_downFailHalfSF","(dbSFnomtight)*triggerTight[0]*puWeight"+topstringdown+"")
        correctionColumns11.Add("topptweight_loose_upFailHalfSF","(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringup+"")
        correctionColumns11.Add("topptweight_loose_downFailHalfSF","(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringdown+"")

        correctionColumns21.Add("topptweight_up","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringup+"")
        correctionColumns21.Add("topptweight_down","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringdown+"")

        correctionColumns21.Add("topptweight_upFailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringup+"")
        correctionColumns21.Add("topptweight_downFailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringdown+"")

        correctionColumns21.Add("topptweight_upFailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringup+"")
        correctionColumns21.Add("topptweight_downFailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringdown+"")
    else:
        topstringnom = ""
        topstringup = ""
        topstringdown = ""


    correctionColumns.Add("finalweightTight","dbSFnomtight*(dbSFnomtight)*triggerTight[0]*puWeight"+topstringnom+"")
    correctionColumns.Add("finalweightLoose","dbSFnomloose*(dbSFnomloose)*triggerLoose[0]*puWeight"+topstringnom+"")
    correctionColumns.Add("finalweightTightFailFullSF","dbSFnomtight*(1-dbSFnomtight)*triggerTight[0]*puWeight"+topstringnom+"")
    correctionColumns.Add("finalweightLooseFailFullSF","dbSFnomloose*(1-dbSFnomloose)*triggerLoose[0]*puWeight"+topstringnom+"")
    correctionColumns.Add("finalweightTightFailHalfSF","dbSFnomtight*triggerTight[0]*puWeight"+topstringnom+"")
    correctionColumns.Add("finalweightLooseFailHalfSF","dbSFnomloose*triggerLoose[0]*puWeight"+topstringnom+"")

    correctionColumns21.Add("finalweight21","dbSFnomloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
    correctionColumns21.Add("finalweight21FailFullSF","(1-dbSFnomloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")
    correctionColumns21.Add("finalweight21FailHalfSF","trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]"+topstringnom+"")


### Here I make the weights for the shape based uncertainties. This cannot be done inline with the Histo1D calls so it is done here.

if not a.isData:

    correctionColumns.Add("Pdfweight",'analyzer::PDFweight(LHEPdfWeight)')
    correctionColumns11.Add("Pdfweight_tight_up",'dbSFnomtight*(dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_tight_down",'dbSFnomtight*(dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_up",'dbSFnomloose*(dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_down",'dbSFnomloose*(dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("Pdfweight_tight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_tight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("Pdfweight_tight_upFailHalfSF",'(dbSFnomtight)*Pdfweight[0]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_tight_downFailHalfSF",'(dbSFnomtight)*Pdfweight[1]*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_upFailHalfSF",'(dbSFnomloose)*Pdfweight[0]*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("Pdfweight_loose_downFailHalfSF",'(dbSFnomloose)*Pdfweight[1]*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("pileupweight_tight_up",'dbSFnomtight*(dbSFnomtight)*puWeightUp*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_tight_down",'dbSFnomtight*(dbSFnomtight)*puWeightDown*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_up",'dbSFnomloose*(dbSFnomloose)*puWeightUp*triggerLoose[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_down",'dbSFnomloose*(dbSFnomloose)*puWeightDown*triggerLoose[0]'+topstringnom+'')

    correctionColumns11.Add("pileupweight_tight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*puWeightUp*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_tight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*puWeightDown*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*puWeightUp*triggerLoose[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*puWeightDown*triggerLoose[0]'+topstringnom+'')

    correctionColumns11.Add("pileupweight_tight_upFailHalfSF",'(dbSFnomtight)*puWeightUp*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_tight_downFailHalfSF",'(dbSFnomtight)*puWeightDown*triggerTight[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_upFailHalfSF",'(dbSFnomloose)*puWeightUp*triggerLoose[0]'+topstringnom+'')
    correctionColumns11.Add("pileupweight_loose_downFailHalfSF",'(dbSFnomloose)*puWeightDown*triggerLoose[0]'+topstringnom+'')

    correctionColumns11.Add("triggertight_up",'dbSFnomtight*(dbSFnomtight)*triggerTight[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggertight_down",'dbSFnomtight*(dbSFnomtight)*triggerTight[2]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_up",'dbSFnomloose*(dbSFnomloose)*triggerLoose[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_down",'dbSFnomloose*(dbSFnomloose)*triggerLoose[2]*puWeight'+topstringnom+'')

    correctionColumns11.Add("triggertight_upFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*triggerTight[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggertight_downFailFullSF",'dbSFnomtight*(1-dbSFnomtight)*triggerTight[2]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_upFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*triggerLoose[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_downFailFullSF",'dbSFnomloose*(1-dbSFnomloose)*triggerLoose[2]*puWeight'+topstringnom+'')

    correctionColumns11.Add("triggertight_upFailHalfSF",'(dbSFnomtight)*triggerTight[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggertight_downFailHalfSF",'(dbSFnomtight)*triggerTight[2]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_upFailHalfSF",'(dbSFnomloose)*triggerLoose[1]*puWeight'+topstringnom+'')
    correctionColumns11.Add("triggerloose_downFailHalfSF",'(dbSFnomloose)*triggerLoose[2]*puWeight'+topstringnom+'')

    correctionColumns11.Add("dbsftight_up",'dbSFuptight*(dbSFuptight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsftight_down",'dbSFdowntight*(dbSFdowntight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_up",'dbSFuploose*(dbSFuploose)*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_down",'dbSFdownloose*(dbSFdownloose)*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("dbsftight_upFailFullSF",'dbSFuptight*(1-dbSFuptight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsftight_downFailFullSF",'dbSFdowntight*(1-dbSFdowntight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_upFailFullSF",'dbSFuploose*(1-dbSFuploose)*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_downFailFullSF",'dbSFdownloose*(1-dbSFdownloose)*triggerLoose[0]*puWeight'+topstringnom+'')

    correctionColumns11.Add("dbsftight_upFailHalfSF",'(dbSFuptight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsftight_downFailHalfSF",'(dbSFdowntight)*triggerTight[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_upFailHalfSF",'(dbSFuploose)*triggerLoose[0]*puWeight'+topstringnom+'')
    correctionColumns11.Add("dbsfloose_downFailHalfSF",'(dbSFdownloose)*triggerLoose[0]*puWeight'+topstringnom+'')

#### Now do 2+1 weights

    correctionColumns21.Add("pileupweight_up",'dbSFnomloose*puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("pileupweight_down",'dbSFnomloose*puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("pileupweight_upFailFullSF",'(1-dbSFnomloose)*puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("pileupweight_downFailFullSF",'(1-dbSFnomloose)*puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("pileupweight_upFailHalfSF",'puWeightUp*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("pileupweight_downFailHalfSF",'puWeightDown*trigger21[0]*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("Pdfweight_up",'dbSFnomloose*Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("Pdfweight_down",'dbSFnomloose*Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("Pdfweight_upFailFullSF",'(1-dbSFnomloose)*Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("Pdfweight_downFailFullSF",'(1-dbSFnomloose)*Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("Pdfweight_upFailHalfSF",'Pdfweight[0]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("Pdfweight_downFailHalfSF",'Pdfweight[1]*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("btagsfweight_up",'dbSFnomloose*puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]'+topstringnom+'')
    correctionColumns21.Add("btagsfweight_down",'dbSFnomloose*puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]'+topstringnom+'')

    correctionColumns21.Add("btagsfweight_upFailFullSF",'(1-dbSFnomloose)*puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]'+topstringnom+'')
    correctionColumns21.Add("btagsfweight_downFailFullSF",'(1-dbSFnomloose)*puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]'+topstringnom+'')

    correctionColumns21.Add("btagsfweight_upFailHalfSF",'puWeight*trigger21[0]*btagscalefactor[1]*btagscalefactor[1]'+topstringnom+'')
    correctionColumns21.Add("btagsfweight_downFailHalfSF",'puWeight*trigger21[0]*btagscalefactor[2]*btagscalefactor[2]'+topstringnom+'')

    correctionColumns21.Add("trigger_up",'dbSFnomloose*trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("trigger_down",'dbSFnomloose*trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("trigger_upFailFullSF",'(1-dbSFnomloose)*trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("trigger_downFailFullSF",'(1-dbSFnomloose)*trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("trigger_upFailHalfSF",'trigger21[1]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("trigger_downFailHalfSF",'trigger21[2]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("dbsfup",'dbSFuploose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("dbsfdown",'dbSFdownloose*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("dbsfupFailFullSF",'(1-dbSFuploose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("dbsfdownFailFullSF",'(1-dbSFdownloose)*trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')

    correctionColumns21.Add("dbsfupFailHalfSF",'trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')
    correctionColumns21.Add("dbsfdownFailHalfSF",'trigger21[0]*puWeight*btagscalefactor[0]*btagscalefactor[0]'+topstringnom+'')


#### 1+1 algorithm
DoubleB_lead_tight = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tagTight'][0])+" && FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tagTight'][1])+""
DoubleB_lead_loose = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tagLoose'][0])+" && FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tagLoose'][1])+""
DoubleB_sublead_tight = "FatJet_"+doubleB_name+"[1] > "+str(cutsDict[doubleB_short+'tagTight'][0])+" && FatJet_"+doubleB_name+"[1] < "+str(cutsDict[doubleB_short+'tagTight'][1])+""
DoubleB_sublead_loose = "FatJet_"+doubleB_name+"[1] > "+str(cutsDict[doubleB_short+'tagLoose'][0])+" && FatJet_"+doubleB_name+"[1] < "+str(cutsDict[doubleB_short+'tagLoose'][1])+""
inverted_DoubleB_lead_loose = "FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tagLoose'][0])
inverted_DoubleB_sublead_loose = "FatJet_"+doubleB_name+"[1] < "+str(cutsDict[doubleB_short+'tagLoose'][0])

srttString = "("+DoubleB_lead_tight+" && "+DoubleB_sublead_tight+") == 1"
srllString = "(("+DoubleB_lead_loose+" && "+DoubleB_sublead_loose+") && !("+srttString+")) == 1"
atttString = "(!("+DoubleB_lead_loose+") && ("+DoubleB_sublead_tight+")) == 1"
atllString = "(!("+DoubleB_lead_loose+") && ("+DoubleB_sublead_loose+") && !("+DoubleB_lead_tight+")) == 1"


### Control region algorithm
invertedCR = "("+inverted_DoubleB_lead_loose+" && "+inverted_DoubleB_sublead_loose+")"
invertedCRFail = "!("+invertedCR+") "

#### 2+1 Algorithm
pass21String = "FatJet_"+doubleB_name+"[0] > "+str(cutsDict[doubleB_short+'tag'][0])+" && "+"FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tag'][1])+""
fail21String = "FatJet_"+doubleB_name+"[0] < "+str(cutsDict[doubleB_short+'tag'][0])+""

run21String = "((!("+srttString+") && (!("+atttString+")) && (!("+srllString+")) && (!("+atllString+"))) == 1)"
cand21String = "((!(nFatJet > 1) || !(pt0 > 300 && pt1 > 300) || !(abs("+eta0+") < 2.4 && abs("+eta1+") < 2.4) || !(abs("+eta0+" - "+eta1+") < 1.3) || !(mreduced > 750.) || !((110 < mh1) && (mh1 < 140))) == 1)"

### Make selection columns
selectionColumns = VarGroup("selectionColumns")
selectionColumns.Add("SRTT",srttString)
selectionColumns.Add("SRLL",srllString)
selectionColumns.Add("ATTT",atttString)
selectionColumns.Add("ATLL",atllString)
selectionColumns.Add("CR",invertedCR)
selectionColumns.Add("CRF",invertedCRFail)

selectionColumns21 = VarGroup("selectionColumns21")
selectionColumns21.Add("Pass21",pass21String)
selectionColumns21.Add("Fail21",fail21String)

#### Make cutgroups

slim_skim = CutGroup('slim_skim')
slim_skim.Add("triggers","triggers == 1")
slim_skim.Add("nFatJets1","nFatJet > 0")

filters = CutGroup('filters')
filters.Add("Flag_goodVertices","Flag_goodVertices == 1")
filters.Add("Flag_globalSuperTightHalo2016Filter","Flag_globalSuperTightHalo2016Filter == 1")
filters.Add("Flag_HBHENoiseFilter","Flag_HBHENoiseFilter == 1")
filters.Add("Flag_HBHENoiseIsoFilter","Flag_HBHENoiseIsoFilter == 1")
filters.Add("Flag_EcalDeadCellTriggerPrimitiveFilter","Flag_EcalDeadCellTriggerPrimitiveFilter == 1")
filters.Add("Flag_BadPFMuonFilter","Flag_BadPFMuonFilter == 1")

#### 1+1 cut groups

preselection11 = CutGroup('preselection11')
preselection11.Add("nFatJets2","nFatJet > 1")
preselection11.Add("pt0",""+pt0+" > 300")
preselection11.Add("pt1",""+pt1+" > 300")
preselection11.Add("eta0","abs("+eta0+") < 2.4")
preselection11.Add("eta1","abs("+eta1+") < 2.4")
preselection11.Add("jetID","((FatJet_jetId[0] & 2) == 2) && ((FatJet_jetId[1] & 2) == 2)")
# preselection11.Add("PV","PV_npvsGood > 0")
preselection11.Add("deltaEta","abs("+eta0+" - "+eta1+") < 1.3")
# preselection11.Add("tau21","(FatJet_tau2[0]/FatJet_tau1[0] < 0.55) && (FatJet_tau2[1]/FatJet_tau1[1] < 0.55)")
# Cut on new column
preselection12 = CutGroup('preselection12')
preselection12.Add("msoftdrop_1","(110 < mh1) && (mh1 < 140)")
preselection12.Add("cut_mreduced","mreduced > 750.")

#### 2+1 cut groups

preselection21 = CutGroup('preselection21')
preselection21.Add("candidate21","("+cand21String+") || ("+run21String+")")
preselection21.Add("nFatJets21","nFatJet > 0")
preselection21.Add("nJets21","nJet >= 2")

preselection22 = CutGroup('preselection22')
preselection22.Add("bb_pairs_check","(Hemispherized[0] != 0) && (Hemispherized[1] != 0)")
preselection22.Add("eta","abs("+eta0+") < 2.4")
preselection22.Add("b_eta","abs(Jet_eta[Hemispherized[0]]) < 2.0 && abs(Jet_eta[Hemispherized[1]]) < 2.0")
preselection22.Add("pt","(pt1 > 300)")
preselection22.Add("b_pt","Jet_pt[Hemispherized[0]] > 30 && Jet_pt[Hemispherized[1]] > 30")
preselection22.Add("jetID","((FatJet_jetId[1] & 2) == 2)")
# preselection22.Add("DeepCSV","(0.4184 < Jet_btagDeepB[Hemispherized[0]] && Jet_btagDeepB[Hemispherized[0]] < 1) && (0.4184 < Jet_btagDeepB[Hemispherized[1]] && Jet_btagDeepB[Hemispherized[1]] < 1)")
preselection22.Add("DeepCSV","(0.6324 < Jet_btagDeepB[Hemispherized[0]] && Jet_btagDeepB[Hemispherized[0]] < 1) && (0.6324 < Jet_btagDeepB[Hemispherized[1]] && Jet_btagDeepB[Hemispherized[1]] < 1)")
preselection22.Add("deltaEta21","abs("+eta1+" - (Jet_eta[Hemispherized[0]]+Jet_eta[Hemispherized[1]])) < 1.3")


preselection23 = CutGroup('preselection23')
# preselection23.Add("mbbCut","90.0 < mbb && mbb < 140.0")
preselection23.Add("mbbCut","105.0 < mbb && mbb < 135.0")
# preselection23.Add("topMass","topMass > 200.0 || topMass < 140.0")
preselection23.Add("topMass","topMass > 200.0")
# preselection23.Add("topMass","topMass > 220.0")
preselection23.Add("topDeltaR","topDeltaR > 1.0")

plotsColumn = VarGroup("plotsColumn")
plotsColumn.Add("eta0",""+eta0+"")
plotsColumn.Add("eta1",""+eta1+"")
plotsColumn.Add("deltaEta","abs("+eta0+" - "+eta1+")")
plotsColumn.Add("FJtau21","FatJet_tau2[0]/FatJet_tau1[0]")
plotsColumn.Add("tagger","FatJet_"+doubleB_name+"[0]")

# Apply all groups in list order to the base RDF loaded in during analyzer() initialization
slimandskim = a.Apply([triggerGroup,slim_skim,filters])

nminus1_11 = a.Apply([triggerGroup,newcolumns,selectionColumns,correctionColumns,correctionColumns11,plotsColumn])
nminus1_21 = a.Apply([triggerGroup,newcolumns,bbColumn,mbbColumn,mred21Column,selectionColumns21,correctionColumns,correctionColumns21,plotsColumn])

preselected = slimandskim.Apply([preselection11,newcolumns,preselection12,selectionColumns,correctionColumns,correctionColumns11,plotsColumn])
preselected21 = slimandskim.Apply([newcolumns,preselection21,bbColumn,preselection22,mbbColumn,preselection23,mred21Column,selectionColumns21,correctionColumns,correctionColumns21])

# Since four analysis regions are covered with relatively complicated cuts to define them, a manual forking is simplest though a Discriminate function does exist for when you need to keep pass and fail of a selection
SRTT = preselected.Cut("SRTT","SRTT==1")
ATTT = preselected.Cut("ATTT","ATTT==1")
SRLL = preselected.Cut("SRLL","SRLL==1")
ATLL = preselected.Cut("ATLL","ATLL==1")
SRCR = preselected.Cut("CR","CR==1")
ATCR = preselected.Cut("CRF","CRF==1")

Pass = preselected21.Cut("Pass21","Pass21==1")
Fail = preselected21.Cut("Fail21","Fail21==1")

out_f = ROOT.TFile(options.output,"RECREATE")
out_f.cd()

print("Outfile booked")

# Need to call DataFrame attribute since Histo2D/Histo1D is a method of RDataFrame - this means at any point, you have access to the plain RDataFrame object corresponding to each node!
##### Make histos for kinematic checks

if not a.isData:
    hpt0TT = preselected.DataFrame.Histo1D(("pt0TT","pt0TT",50 ,150 ,1500),"pt0","finalweightTight")
    hpt1TT = preselected.DataFrame.Histo1D(("pt1TT","pt1TT",50 ,150 ,1500),"pt1","finalweightTight")
    heta0TT = preselected.DataFrame.Histo1D(("eta0TT","eta0TT",50 ,-3.5 ,3.5),"eta0","finalweightTight")
    heta1TT = preselected.DataFrame.Histo1D(("eta1TT","eta1TT",50 ,-3.5 ,3.5),"eta1","finalweightTight")
    hdeltaEtaTT = preselected.DataFrame.Histo1D(("deltaEtaTT","deltaEtaTT",50 ,0 ,3.5),"deltaEta","finalweightTight")
    hmredTT = preselected.DataFrame.Histo1D(("mredTT","mredTT",28 ,700 ,3500),"mreduced","finalweightTight")
    hmsd0TT = preselected.DataFrame.Histo1D(("msd0TT","msd0TT",50 ,0 ,400),"mh","finalweightTight")
    hmsd1TT = preselected.DataFrame.Histo1D(("msd1TT","msd1TT",50 ,0 ,400),"mh1","finalweightTight")
    htau21TT = preselected.DataFrame.Histo1D(("tau21TT","tau21TT",50 ,0 ,1),"FJtau21","finalweightTight")

    hpt0LL = preselected.DataFrame.Histo1D(("pt0LL","pt0LL",50 ,150 ,1500),"pt0","finalweightLoose")
    hpt1LL = preselected.DataFrame.Histo1D(("pt1LL","pt1LL",50 ,150 ,1500),"pt1","finalweightLoose")
    heta0LL = preselected.DataFrame.Histo1D(("eta0LL","eta0LL",50 ,-3.5 ,3.5),"eta0","finalweightLoose")
    heta1LL = preselected.DataFrame.Histo1D(("eta1LL","eta1LL",50 ,-3.5 ,3.5),"eta1","finalweightLoose")
    hdeltaEtaLL = preselected.DataFrame.Histo1D(("deltaEtaLL","deltaEtaLL",50 ,0 ,3.5),"deltaEta","finalweightLoose")
    hmredLL = preselected.DataFrame.Histo1D(("mredLL","mredLL",28 ,700 ,3500),"mreduced","finalweightLoose")
    hmsd0LL = preselected.DataFrame.Histo1D(("msd0LL","msd0LL",50 ,0 ,400),"mh","finalweightLoose")
    hmsd1LL = preselected.DataFrame.Histo1D(("msd1LL","msd1LL",50 ,0 ,400),"mh1","finalweightLoose")
    htau21LL = preselected.DataFrame.Histo1D(("tau21LL","tau21LL",50 ,0 ,1),"FJtau21","finalweightLoose")


    htaggerTT = preselected.DataFrame.Histo1D(("FatJet_"+doubleB_name+"[0]","FatJet_"+doubleB_name+"[0]_TT",50 ,-1 ,1),"tagger","finalweightTight")
    htaggerLL = preselected.DataFrame.Histo1D(("FatJet_"+doubleB_name+"[0]","FatJet_"+doubleB_name+"[0]_LL",50 ,-1 ,1),"tagger","finalweightLoose")


else:
    hpt0TT = preselected.DataFrame.Histo1D(("pt0TT","pt0TT",50 ,150 ,1500),"pt0")
    hpt1TT = preselected.DataFrame.Histo1D(("pt1TT","pt1TT",50 ,150 ,1500),"pt1")
    heta0TT = preselected.DataFrame.Histo1D(("eta0TT","eta0TT",50 ,-3.5 ,3.5),"eta0")
    heta1TT = preselected.DataFrame.Histo1D(("eta1TT","eta1TT",50 ,-3.5 ,3.5),"eta1")
    hdeltaEtaTT = preselected.DataFrame.Histo1D(("deltaEtaTT","deltaEtaTT",50 ,0 ,3.5),"deltaEta")
    hmredTT = preselected.DataFrame.Histo1D(("mredTT","mredTT",28 ,700 ,3500),"mreduced")
    hmsd0TT = preselected.DataFrame.Histo1D(("msd0TT","msd0TT",50 ,0 ,400),"mh")
    hmsd1TT = preselected.DataFrame.Histo1D(("msd1TT","msd1TT",50 ,0 ,400),"mh1")
    htau21TT = preselected.DataFrame.Histo1D(("tau21TT","tau21TT",50 ,0 ,1),"FJtau21")

    hpt0LL = preselected.DataFrame.Histo1D(("pt0LL","pt0LL",50 ,150 ,1500),"pt0")
    hpt1LL = preselected.DataFrame.Histo1D(("pt1LL","pt1LL",50 ,150 ,1500),"pt1")
    heta0LL = preselected.DataFrame.Histo1D(("eta0LL","eta0LL",50 ,-3.5 ,3.5),"eta0")
    heta1LL = preselected.DataFrame.Histo1D(("eta1LL","eta1LL",50 ,-3.5 ,3.5),"eta1")
    hdeltaEtaLL = preselected.DataFrame.Histo1D(("deltaEtaLL","deltaEtaLL",50 ,0 ,3.5),"deltaEta")
    hmredLL = preselected.DataFrame.Histo1D(("mredLL","mredLL",28 ,700 ,3500),"mreduced")
    hmsd0LL = preselected.DataFrame.Histo1D(("msd0LL","msd0LL",50 ,0 ,400),"mh")
    hmsd1LL = preselected.DataFrame.Histo1D(("msd1LL","msd1LL",50 ,0 ,400),"mh1")
    htau21LL = preselected.DataFrame.Histo1D(("tau21LL","tau21LL",50 ,0 ,1),"FJtau21")

    htaggerTT = preselected.DataFrame.Histo1D(("FatJet_"+doubleB_name+"[0]","FatJet_"+doubleB_name+"[0]_TT",50 ,-1 ,1),"tagger")
    htaggerLL = preselected.DataFrame.Histo1D(("FatJet_"+doubleB_name+"[0]","FatJet_"+doubleB_name+"[0]_LL",50 ,-1 ,1),"tagger")


if not a.isData:
    hSRTT11 = SRTT.DataFrame.Histo2D(("SRTT_11","SRTT_11",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced',"finalweightTight")
    hSFTT11 = SRTT.DataFrame.Histo2D(("SFTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightTightFailFullSF")
    hATTT11 = ATTT.DataFrame.Histo2D(("ATTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightTightFailHalfSF")

    hSRLL11 = SRLL.DataFrame.Histo2D(("SRLL_11","SRLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLoose")
    hSFLL11 = SRLL.DataFrame.Histo2D(("SFLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailFullSF")
    hATLL11 = ATLL.DataFrame.Histo2D(("ATLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailHalfSF")


    hSRTT21 = Pass.DataFrame.Histo2D(("Pass_21","Pass_21",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21',"finalweight21")
    hSFTT21 = Pass.DataFrame.Histo2D(("SFFail_21","ATTT_21",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21","finalweight21FailFullSF")
    hATTT21 = Fail.DataFrame.Histo2D(("Fail_21","ATTT_21",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21","finalweight21FailHalfSF")

else:
    hSRTT11 = SRTT.DataFrame.Histo2D(("SRTT_11","SRTT_11",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced')
    hATTT11 = ATTT.DataFrame.Histo2D(("ATTT_11","ATTT_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hSRLL11 = SRLL.DataFrame.Histo2D(("SRLL_11","SRLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hATLL11 = ATLL.DataFrame.Histo2D(("ATLL_11","ATLL_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")

    hSRTT21 = Pass.DataFrame.Histo2D(("Pass_21","Pass_21",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21')
    hATTT21 = Fail.DataFrame.Histo2D(("Fail_21","Fail_21",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21")

### Implement control region
if not a.isData:
    hSRCR11 = SRCR.DataFrame.Histo2D(("SRCR_11","SRCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLoose")
    hSFCR11 = SRCR.DataFrame.Histo2D(("SFCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailFullSF")
    hATCR11 = ATCR.DataFrame.Histo2D(("ATCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced","finalweightLooseFailHalfSF")

else:
    hSRCR11 = SRCR.DataFrame.Histo2D(("SRCR_11","SRCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")
    hATCR11 = ATCR.DataFrame.Histo2D(("ATCR_11","ATCR_11",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced")


mhbins = list(range(45,235,10))
print(mhbins)
mredbins11 = list(range(700,3600,100))
print(mredbins11)
mredbins21 = list(range(700,2100,100))
print(mredbins21)
### Shape based templates

if not a.isData:

##### 1+1 templates
    hSRTT11_pdfUp = SRTT.DataFrame.Histo2D(("SRTT_11_pdfUp","SRTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','Pdfweight_tight_up')
    hATTT11_pdfUp = ATTT.DataFrame.Histo2D(("ATTT_11_pdfUp","ATTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_upFailHalfSF')
    hSFTT11_pdfUp = SRTT.DataFrame.Histo2D(("SFTT_11_pdfUp","ATTT_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_upFailFullSF')

    hSRLL11_pdfUp = SRLL.DataFrame.Histo2D(("SRLL_11_pdfUp","SRLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_up')
    hATLL11_pdfUp = ATLL.DataFrame.Histo2D(("ATLL_11_pdfUp","ATLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailHalfSF')
    hSFLL11_pdfUp = SRLL.DataFrame.Histo2D(("SFLL_11_pdfUp","ATLL_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailFullSF')

    hSRTT11_pdfDown = SRTT.DataFrame.Histo2D(("SRTT_11_pdfDown","SRTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','Pdfweight_tight_down')
    hATTT11_pdfDown = ATTT.DataFrame.Histo2D(("ATTT_11_pdfDown","ATTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_downFailHalfSF')
    hSFTT11_pdfDown = SRTT.DataFrame.Histo2D(("SFTT_11_pdfDown","ATTT_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_tight_downFailFullSF')

    hSRLL11_pdfDown = SRLL.DataFrame.Histo2D(("SRLL_11_pdfDown","SRLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_down')
    hATLL11_pdfDown = ATLL.DataFrame.Histo2D(("ATLL_11_pdfDown","ATLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailHalfSF')
    hSFLL11_pdfDown = SRLL.DataFrame.Histo2D(("SFLL_11_pdfDown","ATLL_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailFullSF')

    hSRTT11_pileupUp = SRTT.DataFrame.Histo2D(("SRTT_11_pileupUp","SRTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','pileupweight_tight_up')
    hATTT11_pileupUp = ATTT.DataFrame.Histo2D(("ATTT_11_pileupUp","ATTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_upFailHalfSF')
    hSFTT11_pileupUp = SRTT.DataFrame.Histo2D(("SFTT_11_pileupUp","ATTT_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_upFailFullSF')

    hSRLL11_pileupUp = SRLL.DataFrame.Histo2D(("SRLL_11_pileupUp","SRLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_up')
    hATLL11_pileupUp = ATLL.DataFrame.Histo2D(("ATLL_11_pileupUp","ATLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailHalfSF')
    hSFLL11_pileupUp = SRLL.DataFrame.Histo2D(("SFLL_11_pileupUp","ATLL_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailFullSF')

    hSRTT11_pileupDown = SRTT.DataFrame.Histo2D(("SRTT_11_pileupDown","SRTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','pileupweight_tight_down')
    hATTT11_pileupDown = ATTT.DataFrame.Histo2D(("ATTT_11_pileupDown","ATTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_downFailHalfSF')
    hSFTT11_pileupDown = SRTT.DataFrame.Histo2D(("SFTT_11_pileupDown","ATTT_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_tight_downFailFullSF')

    hSRLL11_pileupDown = SRLL.DataFrame.Histo2D(("SRLL_11_pileupDown","SRLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_down')
    hATLL11_pileupDown = ATLL.DataFrame.Histo2D(("ATLL_11_pileupDown","ATLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailHalfSF')
    hSFLL11_pileupDown = SRLL.DataFrame.Histo2D(("SFLL_11_pileupDown","ATLL_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailFullSF')

    hSRTT11_triggertight_up = SRTT.DataFrame.Histo2D(("SRTT_11_trigger_up","SRTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','triggertight_up')
    hATTT11_triggertight_up = ATTT.DataFrame.Histo2D(("ATTT_11_trigger_up","ATTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_upFailHalfSF')
    hSFTT11_triggertight_up = SRTT.DataFrame.Histo2D(("SFTT_11_trigger_up","ATTT_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_upFailFullSF')

    hSRLL11_triggerloose_up = SRLL.DataFrame.Histo2D(("SRLL_11_trigger_up","SRLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_up')
    hATLL11_triggerloose_up = ATLL.DataFrame.Histo2D(("ATLL_11_trigger_up","ATLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailHalfSF')
    hSFLL11_triggerloose_up = SRLL.DataFrame.Histo2D(("SFLL_11_trigger_up","ATLL_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailFullSF')

    hSRTT11_triggertight_down = SRTT.DataFrame.Histo2D(("SRTT_11_trigger_down","SRTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','triggertight_down')
    hATTT11_triggertight_down = ATTT.DataFrame.Histo2D(("ATTT_11_trigger_down","ATTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_downFailHalfSF')
    hSFTT11_triggertight_down = SRTT.DataFrame.Histo2D(("SFTT_11_trigger_down","ATTT_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggertight_downFailFullSF')

    hSRLL11_triggerloose_down = SRLL.DataFrame.Histo2D(("SRLL_11_trigger_down","SRLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_down')
    hATLL11_triggerloose_down = ATLL.DataFrame.Histo2D(("ATLL_11_trigger_down","ATLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailHalfSF')
    hSFLL11_triggerloose_down = SRLL.DataFrame.Histo2D(("SFLL_11_trigger_down","ATLL_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailFullSF')

    hSRTT11_dbsftight_up = SRTT.DataFrame.Histo3D(("SRTT_11_dbsf_up","SRTT_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),'pt0','mh','mreduced','dbsftight_up')
    hATTT11_dbsftight_up = ATTT.DataFrame.Histo3D(("ATTT_11_dbsf_up","ATTT_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsftight_upFailHalfSF')
    hSFTT11_dbsftight_up = SRTT.DataFrame.Histo3D(("SFTT_11_dbsf_up","ATTT_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsftight_upFailFullSF')

    hSRLL11_dbsfloose_up = SRLL.DataFrame.Histo3D(("SRLL_11_dbsf_up","SRLL_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_up')
    hATLL11_dbsfloose_up = ATLL.DataFrame.Histo3D(("ATLL_11_dbsf_up","ATLL_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_upFailHalfSF')
    hSFLL11_dbsfloose_up = SRLL.DataFrame.Histo3D(("SFLL_11_dbsf_up","ATLL_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_upFailFullSF')

    hSRTT11_dbsftight_down = SRTT.DataFrame.Histo3D(("SRTT_11_dbsf_down","SRTT_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0",'mh','mreduced','dbsftight_down')
    hATTT11_dbsftight_down = ATTT.DataFrame.Histo3D(("ATTT_11_dbsf_down","ATTT_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsftight_downFailHalfSF')
    hSFTT11_dbsftight_down = SRTT.DataFrame.Histo3D(("SFTT_11_dbsf_down","ATTT_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsftight_downFailFullSF')

    hSRLL11_dbsfloose_down = SRLL.DataFrame.Histo3D(("SRLL_11_dbsf_down","SRLL_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_down')
    hATLL11_dbsfloose_down = ATLL.DataFrame.Histo3D(("ATLL_11_dbsf_down","ATLL_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_downFailHalfSF')
    hSFLL11_dbsfloose_down = SRLL.DataFrame.Histo3D(("SFLL_11_dbsf_down","ATLL_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_downFailFullSF')

##### Control Region templates

    hSRCR11_pdfUp = SRCR.DataFrame.Histo2D(("SRCR_11_pdfUp","SRCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_up')
    hATCR11_pdfUp = ATCR.DataFrame.Histo2D(("ATCR_11_pdfUp","ATCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailHalfSF')
    hSFCR11_pdfUp = SRCR.DataFrame.Histo2D(("SFCR_11_pdfUp","ATCR_11_pdfUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_upFailFullSF')

    hSRCR11_pdfDown = SRCR.DataFrame.Histo2D(("SRCR_11_pdfDown","SRCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_down')
    hATCR11_pdfDown = ATCR.DataFrame.Histo2D(("ATCR_11_pdfDown","ATCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailHalfSF')
    hSFCR11_pdfDown = SRCR.DataFrame.Histo2D(("SFCR_11_pdfDown","ATCR_11_pdfDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'Pdfweight_loose_downFailFullSF')

    hSRCR11_pileupUp = SRCR.DataFrame.Histo2D(("SRCR_11_pileupUp","SRCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_up')
    hATCR11_pileupUp = ATCR.DataFrame.Histo2D(("ATCR_11_pileupUp","ATCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailHalfSF')
    hSFCR11_pileupUp = SRCR.DataFrame.Histo2D(("SFCR_11_pileupUp","ATCR_11_pileupUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_upFailFullSF')

    hSRCR11_pileupDown = SRCR.DataFrame.Histo2D(("SRCR_11_pileupDown","SRCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_down')
    hATCR11_pileupDown = ATCR.DataFrame.Histo2D(("ATCR_11_pileupDown","ATCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailHalfSF')
    hSFCR11_pileupDown = SRCR.DataFrame.Histo2D(("SFCR_11_pileupDown","ATCR_11_pileupDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'pileupweight_loose_downFailFullSF')

    hSRCR11_triggerloose_up = SRCR.DataFrame.Histo2D(("SRCR_11_trigger_up","SRCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_up')
    hATCR11_triggerloose_up = ATCR.DataFrame.Histo2D(("ATCR_11_trigger_up","ATCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailHalfSF')
    hSFCR11_triggerloose_up = SRCR.DataFrame.Histo2D(("SFCR_11_trigger_up","ATCR_11_triggerUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_upFailFullSF')

    hSRCR11_triggerloose_down = SRCR.DataFrame.Histo2D(("SRCR_11_trigger_down","SRCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_down')
    hATCR11_triggerloose_down = ATCR.DataFrame.Histo2D(("ATCR_11_trigger_down","ATCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailHalfSF')
    hSFCR11_triggerloose_down = SRCR.DataFrame.Histo2D(("SFCR_11_trigger_down","ATCR_11_triggerDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'triggerloose_downFailFullSF')

    hSRCR11_dbsfloose_up = SRCR.DataFrame.Histo3D(("SRCR_11_dbsf_up","SRCR_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_up')
    hATCR11_dbsfloose_up = ATCR.DataFrame.Histo3D(("ATCR_11_dbsf_up","ATCR_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_upFailHalfSF')
    hSFCR11_dbsfloose_up = SRCR.DataFrame.Histo3D(("SFCR_11_dbsf_up","ATCR_11_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_upFailFullSF')

    hSRCR11_dbsfloose_down = SRCR.DataFrame.Histo3D(("SRCR_11_dbsf_down","SRCR_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_down')
    hATCR11_dbsfloose_down = ATCR.DataFrame.Histo3D(("ATCR_11_dbsf_down","ATCR_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_downFailHalfSF')
    hSFCR11_dbsfloose_down = SRCR.DataFrame.Histo3D(("SFCR_11_dbsf_down","ATCR_11_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,28 ,array('d',mredbins11)),"pt0","mh","mreduced",'dbsfloose_downFailFullSF')

##### Now for 2+1 template histo calls.

    hSRTT21_pdfUp = Pass.DataFrame.Histo2D(("SRTT_21_pdfUp","SRTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','Pdfweight_up')
    hATTT21_pdfUp = Fail.DataFrame.Histo2D(("ATTT_21_pdfUp","ATTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'Pdfweight_upFailHalfSF')
    hSFTT21_pdfUp = Pass.DataFrame.Histo2D(("SFTT_21_pdfUp","SFTT_21_pdfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'Pdfweight_upFailFullSF')

    hSRTT21_pdfDown = Pass.DataFrame.Histo2D(("SRTT_21_pdfDown","SRTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','Pdfweight_down')
    hATTT21_pdfDown = Fail.DataFrame.Histo2D(("ATTT_21_pdfDown","ATTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'Pdfweight_downFailHalfSF')
    hSFTT21_pdfDown = Pass.DataFrame.Histo2D(("SFTT_21_pdfDown","ATTT_21_pdfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'Pdfweight_downFailFullSF')

    hSRTT21_pileupUp = Pass.DataFrame.Histo2D(("SRTT_21_pileupUp","SRTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','pileupweight_up')
    hATTT21_pileupUp = Fail.DataFrame.Histo2D(("ATTT_21_pileupUp","ATTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'pileupweight_upFailHalfSF')
    hSFTT21_pileupUp = Pass.DataFrame.Histo2D(("SFTT_21_pileupUp","SFTT_21_pileupUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'pileupweight_upFailFullSF')

    hSRTT21_pileupDown = Pass.DataFrame.Histo2D(("SRTT_21_pileupDown","SRTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','pileupweight_down')
    hATTT21_pileupDown = Fail.DataFrame.Histo2D(("ATTT_21_pileupDown","ATTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'pileupweight_downFailHalfSF')
    hSFTT21_pileupDown = Pass.DataFrame.Histo2D(("SFTT_21_pileupDown","ATTT_21_pileupDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'pileupweight_downFailFullSF')

    hSRTT21_trigger_up = Pass.DataFrame.Histo2D(("SRTT_21_trigger_up","SRTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','trigger_up')
    hATTT21_trigger_up = Fail.DataFrame.Histo2D(("ATTT_21_trigger_up","ATTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'trigger_upFailHalfSF')
    hSFTT21_trigger_up = Pass.DataFrame.Histo2D(("SFTT_21_trigger_up","SFTT_21_triggerUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'trigger_upFailFullSF')

    hSRTT21_trigger_down = Pass.DataFrame.Histo2D(("SRTT_21_trigger_down","SRTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','trigger_down')
    hATTT21_trigger_down = Fail.DataFrame.Histo2D(("ATTT_21_trigger_down","ATTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'trigger_downFailHalfSF')
    hSFTT21_trigger_down = Pass.DataFrame.Histo2D(("SFTT_21_trigger_down","ATTT_21_triggerDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'trigger_downFailFullSF')

    hSRTT21_btagsfUp = Pass.DataFrame.Histo2D(("hSRTT_21_btagsfUp","SRTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','btagsfweight_up')
    hATTT21_btagsfUp = Fail.DataFrame.Histo2D(("hATTT_21_btagsfUp","ATTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'btagsfweight_upFailHalfSF')
    hSFTT21_btagsfUp = Pass.DataFrame.Histo2D(("hSFTT_21_btagsfUp","SFTT_21_btagsfUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'btagsfweight_upFailFullSF')

    hSRTT21_btagsfDown = Pass.DataFrame.Histo2D(("hSRTT_21_btagsfDown","SRTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','btagsfweight_down')
    hATTT21_btagsfDown = Fail.DataFrame.Histo2D(("hATTT_21_btagsfDown","ATTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'btagsfweight_downFailHalfSF')
    hSFTT21_btagsfDown = Pass.DataFrame.Histo2D(("hSFTT_21_btagsfDown","ATTT_21_btagsfDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'btagsfweight_downFailFullSF')

    hSRTT21_dbsf_up = Pass.DataFrame.Histo3D(("SRTT_21_dbsf_up","SRTT_21_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,13 ,array('d',mredbins21)),'pt1','mh1','mreduced21','dbsfup')
    hATTT21_dbsf_up = Fail.DataFrame.Histo3D(("ATTT_21_dbsf_up","ATTT_21_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,13 ,array('d',mredbins21)),"pt1","mh1","mreduced21",'dbsfupFailHalfSF')
    hSFTT21_dbsf_up = Pass.DataFrame.Histo3D(("SFTT_21_dbsf_up","SFTT_21_dbsfUp",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,13 ,array('d',mredbins21)),"pt1","mh1","mreduced21",'dbsfupFailFullSF')

    hSRTT21_dbsf_down = Pass.DataFrame.Histo3D(("SRTT_21_dbsf_down","SRTT_21_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,13 ,array('d',mredbins21)),"pt1",'mh1','mreduced21','dbsfdown')
    hATTT21_dbsf_down = Fail.DataFrame.Histo3D(("ATTT_21_dbsf_down","ATTT_21_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,13 ,array('d',mredbins21)),"pt1","mh1","mreduced21",'dbsfdownFailHalfSF')
    hSFTT21_dbsf_down = Pass.DataFrame.Histo3D(("SFTT_21_dbsf_down","ATTT_21_dbsfDown",4,array('d',[300,400,500,600,2000]),18 ,array('d',mhbins) ,13 ,array('d',mredbins21)),"pt1","mh1","mreduced21",'dbsfdownFailFullSF')

    if 'ttbar' in options.input:
#### 1+1 Templates
        hSRTT11_topptUp = SRTT.DataFrame.Histo2D(("SRTT_11_topptUp","SRTT_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','topptweight_tight_up')
        hATTT11_topptUp = ATTT.DataFrame.Histo2D(("ATTT_11_topptUp","ATTT_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_upFailHalfSF')
        hSFTT11_topptUp = SRTT.DataFrame.Histo2D(("SFTT_11_topptUp","ATTT_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_upFailFullSF')

        hSRLL11_topptUp = SRLL.DataFrame.Histo2D(("SRLL_11_topptUp","SRLL_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_up')
        hATLL11_topptUp = ATLL.DataFrame.Histo2D(("ATLL_11_topptUp","ATLL_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_upFailHalfSF')
        hSFLL11_topptUp = SRLL.DataFrame.Histo2D(("SFLL_11_topptUp","ATLL_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_upFailFullSF')

        hSRTT11_topptDown = SRTT.DataFrame.Histo2D(("SRTT_11_topptDown","SRTT_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),'mh','mreduced','topptweight_tight_down')
        hATTT11_topptDown = ATTT.DataFrame.Histo2D(("ATTT_11_topptDown","ATTT_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_downFailHalfSF')
        hSFTT11_topptDown = SRTT.DataFrame.Histo2D(("SFTT_11_topptDown","ATTT_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_tight_downFailFullSF')

        hSRLL11_topptDown = SRLL.DataFrame.Histo2D(("SRLL_11_topptDown","SRLL_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_down')
        hATLL11_topptDown = ATLL.DataFrame.Histo2D(("ATLL_11_topptDown","ATLL_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_downFailHalfSF')
        hSFLL11_topptDown = SRLL.DataFrame.Histo2D(("SFLL_11_topptDown","ATLL_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_downFailFullSF')

### Now Control Region templates
        hSRCR11_topptUp = SRCR.DataFrame.Histo2D(("SRCR_11_topptUp","SRCR_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_up')
        hATCR11_topptUp = ATCR.DataFrame.Histo2D(("ATCR_11_topptUp","ATCR_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_upFailHalfSF')
        hSFCR11_topptUp = SRCR.DataFrame.Histo2D(("SFCR_11_topptUp","ATCR_11_topptUp",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_upFailFullSF')

        hSRCR11_topptDown = SRCR.DataFrame.Histo2D(("SRCR_11_topptDown","SRCR_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_down')
        hATCR11_topptDown = ATCR.DataFrame.Histo2D(("ATCR_11_topptDown","ATCR_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_downFailHalfSF')
        hSFCR11_topptDown = SRCR.DataFrame.Histo2D(("SFCR_11_topptDown","ATCR_11_topptDown",18 ,45 ,225 ,28 ,700 ,3500),"mh","mreduced",'topptweight_loose_downFailFullSF')

### Now 2+1 top templates
        hSRTT21_topptUp = Pass.DataFrame.Histo2D(("SRTT_21_topptUp","SRTT_21_topptUp",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','topptweight_up')
        hATTT21_topptUp = Fail.DataFrame.Histo2D(("ATTT_21_topptUp","ATTT_21_topptUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'topptweight_upFailHalfSF')
        hSFTT21_topptUp = Pass.DataFrame.Histo2D(("SFTT_21_topptUp","SFTT_21_topptUp",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'topptweight_upFailFullSF')


        hSRTT21_topptDown = Pass.DataFrame.Histo2D(("SRTT_21_topptDown","SRTT_21_topptDown",18 ,45 ,225 ,13 ,700 ,2000),'mh1','mreduced21','topptweight_down')
        hATTT21_topptDown = Fail.DataFrame.Histo2D(("ATTT_21_topptDown","ATTT_21_topptDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'topptweight_downFailHalfSF')
        hSFTT21_topptDown = Pass.DataFrame.Histo2D(("SFTT_21_topptDown","ATTT_21_topptDown",18 ,45 ,225 ,13 ,700 ,2000),"mh1","mreduced21",'topptweight_downFailFullSF')


        top_check = preselected.DataFrame.Histo1D("topptvectorcheck")


#### The below is done to account for needing to derive a SF for the Fail distribution on the alphabet jet

if not a.isData:

    hATTT11.Add(hSFTT11.GetPtr())
    hATLL11.Add(hSFLL11.GetPtr())
    hATTT21.Add(hSFTT21.GetPtr())
    hATCR11.Add(hSFCR11.GetPtr())

##### 1+1 templates

    hATTT11_pdfUp.Add(hSFTT11_pdfUp.GetPtr())
    hATLL11_pdfUp.Add(hSFLL11_pdfUp.GetPtr())
    hATTT11_pdfDown.Add(hSFTT11_pdfDown.GetPtr())
    hATLL11_pdfDown.Add(hSFLL11_pdfDown.GetPtr())
    hATTT11_pileupUp.Add(hSFTT11_pileupUp.GetPtr())
    hATLL11_pileupUp.Add(hSFLL11_pileupUp.GetPtr())
    hATTT11_pileupDown.Add(hSFTT11_pileupDown.GetPtr())
    hATLL11_pileupDown.Add(hSFLL11_pileupDown.GetPtr())
    hATTT11_triggertight_up.Add(hSFTT11_triggertight_up.GetPtr())
    hATLL11_triggerloose_up.Add(hSFLL11_triggerloose_up.GetPtr())
    hATTT11_triggertight_down.Add(hSFTT11_triggertight_down.GetPtr())
    hATLL11_triggerloose_down.Add(hSFLL11_triggerloose_down.GetPtr())
    hATTT11_dbsftight_up.Add(hSFTT11_dbsftight_up.GetPtr())
    hATLL11_dbsfloose_up.Add(hSFLL11_dbsfloose_up.GetPtr())
    hATTT11_dbsftight_down.Add(hSFTT11_dbsftight_down.GetPtr())
    hATLL11_dbsfloose_down.Add(hSFLL11_dbsfloose_down.GetPtr())

##### Control Region templates

    hATCR11_pdfUp.Add(hSFCR11_pdfUp.GetPtr())
    hATCR11_pdfDown.Add(hSFCR11_pdfDown.GetPtr())
    hATCR11_pileupUp.Add(hSFCR11_pileupUp.GetPtr())
    hATCR11_pileupDown.Add(hSFCR11_pileupDown.GetPtr())
    hATCR11_triggerloose_up.Add(hSFCR11_triggerloose_up.GetPtr())
    hATCR11_triggerloose_down.Add(hSFCR11_triggerloose_down.GetPtr())
    hATCR11_dbsfloose_up.Add(hSFCR11_dbsfloose_up.GetPtr())
    hATCR11_dbsfloose_down.Add(hSFCR11_dbsfloose_down.GetPtr())

##### Now for 2+1 template histo calls.
    hATTT21_pdfUp.Add(hSFTT21_pdfUp.GetPtr())
    hATTT21_pdfDown.Add(hSFTT21_pdfDown.GetPtr())
    hATTT21_pileupUp.Add(hSFTT21_pileupUp.GetPtr())
    hATTT21_pileupDown.Add(hSFTT21_pileupDown.GetPtr())
    hATTT21_trigger_up.Add(hSFTT21_trigger_up.GetPtr())
    hATTT21_trigger_down.Add(hSFTT21_trigger_down.GetPtr())
    hATTT21_btagsfUp.Add(hSFTT21_btagsfUp.GetPtr())
    hATTT21_btagsfDown.Add(hSFTT21_btagsfDown.GetPtr())
    hATTT21_dbsf_up.Add(hSFTT21_dbsf_up.GetPtr())
    hATTT21_dbsf_down.Add(hSFTT21_dbsf_down.GetPtr())

    if 'ttbar' in options.input:
#### 1+1 Templates

        hATTT11_topptUp.Add(hSFTT11_topptUp.GetPtr())
        hATLL11_topptUp.Add(hSFLL11_topptUp.GetPtr())
        hATTT11_topptDown.Add(hSFTT11_topptDown.GetPtr())
        hATLL11_topptDown.Add(hSFLL11_topptDown.GetPtr())

### Now Control Region templates

        hATCR11_topptUp.Add(hSFCR11_topptUp.GetPtr())
        hATCR11_topptDown.Add(hSFCR11_topptDown.GetPtr())       

### Now 2+1 top templates

        hATTT21_topptUp.Add(hSFTT21_topptUp.GetPtr())
        hATTT21_topptDown.Add(hSFTT21_topptDown.GetPtr())

#### Now we can process the histograms
hists = [hSRTT11,hATTT11,hSRLL11,hATLL11,hSRTT21,hATTT21,hSRCR11,hATCR11,        
        hpt0TT,hpt1TT,heta0TT,heta1TT,hdeltaEtaTT,hmredTT,hmsd1TT,htau21TT,hmsd0TT,hpt0LL,hpt1LL,heta0LL,heta1LL,hdeltaEtaLL,hmredLL,hmsd1LL,htau21LL,hmsd0LL,htaggerTT,htaggerLL]

if not a.isData:
    hists.extend([hSRTT11_pdfUp,hATTT11_pdfUp,hSRLL11_pdfUp,hATLL11_pdfUp,hSRTT11_pdfDown,hATTT11_pdfDown,hSRLL11_pdfDown,hATLL11_pdfDown,
        hSRTT11_pileupUp,hATTT11_pileupUp,hSRLL11_pileupUp,hATLL11_pileupUp,hSRTT11_pileupDown,hATTT11_pileupDown,hSRLL11_pileupDown,hATLL11_pileupDown,
        hSRTT11_triggertight_up,hATTT11_triggertight_up,hSRLL11_triggerloose_up,hATLL11_triggerloose_up,hSRTT11_triggertight_down,hATTT11_triggertight_down,hSRLL11_triggerloose_down,hATLL11_triggerloose_down,
        hSRTT11_dbsftight_up,hATTT11_dbsftight_up,hSRLL11_dbsfloose_up,hATLL11_dbsfloose_up,hSRTT11_dbsftight_down,hATTT11_dbsftight_down,hSRLL11_dbsfloose_down,hATLL11_dbsfloose_down,
        hSRTT21_pdfUp,hATTT21_pdfUp,hSRTT21_pdfDown,hATTT21_pdfDown,hSRTT21_pileupUp,hATTT21_pileupUp,hSRTT21_pileupDown,hATTT21_pileupDown,hSRTT21_dbsf_up,hATTT21_dbsf_up,hSRTT21_dbsf_down,hATTT21_dbsf_down,
        hSRTT21_trigger_up,hATTT21_trigger_up,hSRTT21_trigger_down,hATTT21_trigger_down,hSRTT21_btagsfUp,hATTT21_btagsfUp,hSRTT21_btagsfDown,hATTT21_btagsfDown,
        hSRCR11_pdfUp,hATCR11_pdfUp,hSRCR11_pdfDown,hATCR11_pdfDown,
        hSRCR11_pileupUp,hATCR11_pileupUp,hSRCR11_pileupDown,hATCR11_pileupDown,
        hSRCR11_triggerloose_up,hATCR11_triggerloose_up,hSRCR11_triggerloose_down,hATCR11_triggerloose_down,
        hSRCR11_dbsfloose_up,hATCR11_dbsfloose_up,hSRCR11_dbsfloose_down,hATCR11_dbsfloose_down])
    if 'ttbar' in options.input:
        hists.extend([hSRTT11_topptUp,hATTT11_topptUp,hSRLL11_topptUp,hATLL11_topptUp,hSRTT11_topptDown,hATTT11_topptDown,hSRLL11_topptDown,hATLL11_topptDown,
            hSRCR11_topptUp,hATCR11_topptUp,hSRCR11_topptDown,hATCR11_topptDown,        
            hSRTT21_topptUp,hATTT21_topptUp,hSRTT21_topptDown,hATTT21_topptDown])

norm_hist = ROOT.TH1F('norm','norm',1,0,1)
norm_hist.SetBinContent(1,norm)
norm_hist.Write()

# Draw a simple cutflow plot
SRTT_cuts = slim_skim+filters+preselection11+preselection12
SRTT_cuts.Add("SRTT","SRTT==1")
SRTT_cutflow = CutflowHist('cutflow11',SRTT) # SRTT.DataFrame already has the cuts and numbers, SRTT_cuts is just to name the histogram bins (but that means they must match up!)
SRTT_cutflow.Write()

Pass21_cuts = slim_skim+filters+preselection21+preselection22+preselection23
Pass21_cuts.Add("Pass21","Pass21==1")
Pass21_cutflow = CutflowHist('cutflow21',Pass) 
Pass21_cutflow.Write()

nminus1_21_node = Nminus1(nminus1_21,Pass21_cuts)
if not a.isData:
    trijetDeltaRhist = nminus1_21_node["topDeltaR"].DataFrame.Histo1D(("trijetDeltaR","trijetDeltaR",50 ,0 ,5),"topDeltaR","finalweightTight")
    trijetMasshist = nminus1_21_node["topMass"].DataFrame.Histo1D(("trijetMass","trijetMass",50 ,100 ,1000),"topMass","finalweightTight")
else:
    trijetDeltaRhist = nminus1_21_node["topDeltaR"].DataFrame.Histo1D(("trijetDeltaR","trijetDeltaR",50 ,0 ,5),"topDeltaR")
    trijetMasshist = nminus1_21_node["topMass"].DataFrame.Histo1D(("trijetMass","trijetMass",50 ,100 ,1000),"topMass")

hists.extend([trijetDeltaRhist,trijetMasshist])

for h in hists: 
    h.Scale(norm)
    h.Write()

dbsflist = [hSRTT11_dbsftight_up,hATTT11_dbsftight_up,hSRLL11_dbsfloose_up,hATLL11_dbsfloose_up,hSRTT11_dbsftight_down,hATTT11_dbsftight_down,hSRLL11_dbsfloose_down,hATLL11_dbsfloose_down]
for h in dbsflist:
    h.GetXaxis().SetRangeUser(300.0,400.0)
    h.Project3D("34_zy").Write()
    h.GetXaxis().SetRangeUser(400.0,500.0)
    h.Project3D("45_zy").Write()
    h.GetXaxis().SetRangeUser(500.0,600.0)
    h.Project3D("56_zy").Write()
    h.GetXaxis().SetRangeUser(600.0,2000.0)
    h.Project3D("6p_zy").Write()
# Cleanup
out_f.Close()
print("Total time: "+str((time.time()-start_time)/60.) + ' min')
