#!/usr/bin/env python
#------------------------------------------------------------------
#- File: plotBNN.py
#- Description: Make BNN plots
#- Created:     20-Dec-2013 HBP, Tallahassee
#------------------------------------------------------------------
import os, sys
from time import sleep
from histutil import *
from string import *
from pprint import PrettyPrinter
from ROOT import *
#------------------------------------------------------------------
SCOLOR = kRed
BCOLOR = kCyan+2
RCOLOR = kBlue
TREENAME  = 'HZZ4LeptonsAnalysisReduced'
VARS = '''
event.f_Z1mass
event.f_Z2mass
event.f_angle_costhetastar
event.f_angle_costheta1
event.f_angle_costheta2
event.f_angle_phi
event.f_angle_phistar1
'''
VARS = split(strip(VARS))
#------------------------------------------------------------------
def readAndFill(filename, treename, bnn, bnnvar, c, h):
    ntuple = Ntuple(filename, treename)

    # create call to bnn, which is to be evaluated using eval
    cmd = 'bnn(%s)' % joinfields(bnnvar, ',')
    
    # loop over ntuple
    count = 0
    total = 0.0
    for rownumber, event in enumerate(ntuple):
        count += 1
        total += event.f_weight
        
        D = eval(cmd)
        h.Fill(D, event.f_weight)
        if count % 5000 == 0:
            c.cd()
            h.Draw('hist')
            c.Update()
    print "count: %d,\ttotal: %10.2f\n" % (count, total)
#------------------------------------------------------------------
#------------------------------------------------------------------
def main():
    print "="*80

    BNNname = 'bnnMELA'
    ytitle  = ''
    sigfile = glob('data/ntp_*_m126_ggF.root')
    bkgfile = glob('data/ntp_*_bkgd.root')
    datfile = glob('data/ntp_*_data.root')
    
    variables = VARS
    pp = PrettyPrinter()
    print 'BNN:        %s\n' % BNNname
    
    print 'signal files'
    pp.pprint(sigfile)
    print
    
    print 'background files'
    pp.pprint(bkgfile)
    print
    
    print 'data files'
    pp.pprint(datfile)
    print
    
    print 'variables'
    pp.pprint(variables)
    print "="*80
    #----------------------------------------------------------
    # compile bnn function (need Root 6)
    gROOT.ProcessLine(open('%s.cpp' % BNNname).read())

    # import into python give it the alias "bnn"
    exec('from ROOT import %s as bnn' % BNNname)

    # ---------------------------------------------------------
    # plot stuff
    # ---------------------------------------------------------
    setStyle()
    
    c1  = TCanvas("fig_%s_D" % BNNname, "", 10, 10, 500, 500)

    hfile = TFile("his_%s.root" % BNNname,"RECREATE")

    nbins = 20
    hfile.cd()
    hs = mkhist1("hs", "BNN(#font[12]{m_{H}}=126GeV)", "", nbins, 0, 1)
    hs.GetXaxis().SetNdivisions(510) 
    hs.SetLineWidth(1)
    hs.SetLineColor(SCOLOR)
    hs.SetFillColor(SCOLOR)
    hs.SetFillStyle(3002)
    print "\n=> process signals"
    readAndFill(sigfile, TREENAME, bnn, variables, c1, hs)
    
    hfile.cd()
    hb = mkhist1("hb", "BNN(#font[12]{m_{H}}=126GeV)", "", nbins, 0, 1)
    hb.GetXaxis().SetNdivisions(510) 
    hb.SetLineWidth(1)
    hb.SetLineColor(BCOLOR)
    hb.SetFillColor(BCOLOR)
    hb.SetFillStyle(3002)
    print "\n=> process backgrounds"
    readAndFill(bkgfile, TREENAME, bnn, variables, c1, hb)
    
    hfile.cd()
    hd = mkhist1("hd", "BNN(#font[12]{m_{H}}=126GeV)", "count", nbins, 0, 1)
    hd.SetLineWidth(2)
    hd.SetLineColor(kBlack)
    hd.GetXaxis().SetNdivisions(510)
    print "\n=> process data"
    readAndFill(datfile, TREENAME, bnn, variables, c1, hd)

    
    c1.cd()
    k = int(1.3*max(hb.GetMaximum(), hs.GetMaximum())/0.1)
    ymax = (k+1) * 0.1
    ymax = 18.0
    hs.SetMaximum(ymax)
    hd.SetMaximum(ymax)

    hfile.cd()
    hst = THStack('hst', "stacked")
    hst.Add(hb)
    hst.Add(hs)
    hst.SetMaximum(ymax)
    
    c1.cd()
    hst.Draw('hist')
    hd.Draw('ep same')
    c1.Update()
    c1.SaveAs(".pdf")
    
    hfile.cd()
    c1.Write()
    hfile.Write()    
    sleep(5)
#----------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "ciao!"
    
