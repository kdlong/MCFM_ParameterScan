#!/usr/bin/env python

import ROOT
import argparse
import os
from array import array

ROOT.gROOT.SetBatch()
parser = argparse.ArgumentParser()
parser.add_argument("analysis", choices=["WZ", "ZZ"])

args = parser.parse_args()

mc_file = "data/%s_scan_values_removebr.txt" % args.analysis
if not os.path.isfile(mc_file):
    print "Invalid data file %s" % mc_file
    exit(0)

xsec_graph = ROOT.TGraph(mc_file)
xsec_graph.SetLineColor(ROOT.kRed-6)
scaleup_graph = ROOT.TGraph(mc_file, "%lg %*lg %lg")
scaleup_graph.SetLineColor(ROOT.kGray)
scaledown_graph = ROOT.TGraph(mc_file, "%lg %*lg %*lg %lg")
scaledown_graph.SetLineColor(ROOT.kGray)

canvas = ROOT.TCanvas("canvas", "canvas", 600, 600)

data_graph = ROOT.TGraphAsymmErrors(3,
    array('f', [7., 8., 13.]),
    array('f', [20.76, 24.61, 40.2]),
    array('f', [0, 0., 0.]),
    array('f', [0, 0., 0.]),
    array('f', [1.8, 1.74, 7.8]),
    array('f', [1.8, 1.74, 8.43])
) if args.analysis == "WZ" else ROOT.TGraphAsymmErrors(3,
    array('f', [7., 8., 13.]),
    array('f', [6.24, 7.7, 16.3]),
    array('f', [0, 0., 0.]),
    array('f', [0, 0., 0.]),
    array('f', [0.87, 0.78, 3.34]),
    array('f', [0.96, 0.84, 3.80])
)
data_graph.Draw("Ape1")
ROOT.gStyle.SetEndErrorSize(6)
data_graph.SetMarkerStyle(24)
data_graph.SetLineWidth(2)
data_graph.SetMarkerSize(1)
data_graph.GetXaxis().SetRangeUser(6, 14)
data_graph.GetXaxis().SetTitle("#sqrt{s} (TeV)")
data_graph.GetYaxis().SetTitle("Cross Section (pb)")

xsec_graph.Draw("C same")
scaleup_graph.Draw("C same")
scaledown_graph.Draw("C same")

canvas.Print("%sCrossSection.pdf" % args.analysis)
