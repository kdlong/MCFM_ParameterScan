#!/usr/bin/env python

import math
import ROOT
import argparse
import os
from array import array

def errorPlotFromFile(file_name):
    xvals = []
    central = []
    errorup = []
    errordown = []
    error2up = []
    error2down = []
    num_lines = 0
    with open(file_name) as input_file:
        for line in input_file:
            num_lines += 1
            values = line.split()
            if len(values) < 2:
                print "Invalid input file %s" % file_name
                exit(0)
            xvals.append(float(values[0]))
            central.append(float(values[1]))
            if len(values) < 4:
                print "No error values found in input file %s" % file_name
                continue
            if "%" in values[2]:
                values[2] = float(values[1])*float(values[2].strip("%"))/100
            if "%" in values[3]:
                values[3] = float(values[1])*float(values[3].strip("%"))/100
            errorup.append(float(values[2]))
            errordown.append(float(values[3]))
            if len(values) == 6:
                error2down.append(math.sqrt(float(values[2])**2 + float(values[4])**2))
                error2up.append(math.sqrt(float(values[3])**2 + float(values[5])**2))
    error_graph = ROOT.TGraphAsymmErrors(num_lines,
        array('f', xvals),
        array('f', central),
        array('f', [0 for val in xvals]), #No x errors
        array('f', [0 for val in xvals]), #No x errors
        array('f', errordown),
        array('f', errorup)
    )
    syst_error_graph = 0
    if len(error2up) != 0:
        syst_error_graph = ROOT.TGraphAsymmErrors(num_lines,
            array('f', xvals),
            array('f', central),
            array('f', [0 for val in xvals]), #No x errors
            array('f', [0 for val in xvals]), #No x errors
            array('f', error2down),
            array('f', error2up)
        )
        
    return (error_graph, syst_error_graph)
ROOT.gROOT.SetBatch()
parser = argparse.ArgumentParser()
parser.add_argument("analysis", choices=["WZ", "ZZ"])

args = parser.parse_args()

mc_file = "data/%s_scan_values_removebr.txt" % args.analysis
if not os.path.isfile(mc_file):
    print "Invalid data file %s" % mc_file
    exit(0)

(xsec_graph, pdf_errs) = errorPlotFromFile(mc_file)
xsec_graph.SetLineColor(ROOT.TColor.GetColor("#FFE6EC"))
xsec_graph.SetLineColor(ROOT.TColor.GetColor("#ca0020"))
xsec_graph.SetFillColor(ROOT.TColor.GetColor("#FFE6EC"))
xsec_graph.SetLineWidth(1)
pdf_errs.SetLineColor(ROOT.TColor.GetColor("#F8D4DA"))
pdf_errs.SetFillColor(ROOT.TColor.GetColor("#F8D4DA"))

canvas = ROOT.TCanvas("canvas", "canvas", 600, 600)

(data_graph, sys_errors) = errorPlotFromFile("data/%s_CMS_measurements.txt" % args.analysis)
data_graph.SetMarkerStyle(24)
data_graph.SetLineWidth(1)
data_graph.SetMarkerSize(1)

sys_errors.SetMarkerStyle(20)
sys_errors.SetLineWidth(2)
sys_errors.SetMarkerSize(1)
sys_errors.SetMarkerColor(10)
(atlas_data_graph, atlas_sys_errors) = errorPlotFromFile("data/%s_ATLAS_measurements.txt" % args.analysis)
atlas_data_graph.SetMarkerStyle(26)
atlas_data_graph.SetLineWidth(1)
atlas_data_graph.SetMarkerSize(1)
atlas_sys_errors.SetMarkerColor(10)
atlas_sys_errors.SetMarkerStyle(22)
atlas_sys_errors.SetLineWidth(2)
atlas_sys_errors.SetMarkerSize(1)



pdf_errs.SetMaximum(23 if args.analysis == "ZZ" else 55)
if args.analysis == "ZZ":
    pdf_errs.SetMinimum(2)

pdf_errs.Draw("A3")
pdf_errs.GetXaxis().SetRangeUser(5.6, 14.4)
pdf_errs.GetXaxis().SetTitle("#sqrt{s} (TeV)")
pdf_errs.GetYaxis().SetTitle("#sigma_{pp #rightarrow %s}(pb)" % args.analysis)
xsec_graph.Draw("3")

xsec_graph_clone = xsec_graph.Clone()
xsec_graph_clone.SetLineColor(ROOT.TColor.GetColor("#ca0020"))
xsec_graph_clone.Draw("CX")

if args.analysis == "ZZ":
    nnlo_graph = errorPlotFromFile("data/ZZ_nnlo_values.txt")[0]
    nnlo_graph.SetFillColor(ROOT.TColor.GetColor("#A3DFFF"))
    nnlo_graph.SetLineColor(ROOT.TColor.GetColor("#002D80"))
    nnlo_graph.Draw("3 same")
    nnlo_graph_clone = nnlo_graph.Clone()
    nnlo_graph_clone.SetLineColor(ROOT.TColor.GetColor("#002D80"))
    nnlo_graph_clone.Draw("CX")
    
    mcfm_nlo_graph = errorPlotFromFile("data/ZZ_MCFM_published_nlo_values.txt")[0]
    mcfm_nlo_graph.SetFillColorAlpha(ROOT.TColor.GetColor("#C2FFBD"), 0.4)
    mcfm_nlo_graph.SetLineColor(ROOT.TColor.GetColor("#004D00"))
    mcfm_nlo_graph.Draw("3 same")                               
    mcfm_nlo_graph_clone = mcfm_nlo_graph.Clone()
    mcfm_nlo_graph_clone.SetLineColor(ROOT.TColor.GetColor("#004D00"))
    mcfm_nlo_graph_clone.Draw("CX")

    (zz2l2v_data_graph, zz2l2v_sys_errors) = errorPlotFromFile("data/ZZ2l2v_CMS_measurements.txt")
    zz2l2v_data_graph.SetMarkerStyle(25)
    zz2l2v_data_graph.SetLineWidth(1)
    zz2l2v_data_graph.SetMarkerSize(1)
    zz2l2v_sys_errors.SetMarkerStyle(21)
    zz2l2v_sys_errors.SetLineWidth(2)
    zz2l2v_sys_errors.SetMarkerColor(10)
    zz2l2v_sys_errors.SetMarkerSize(1)
    zz2l2v_data_graph.Draw("P same")
    zz2l2v_sys_errors.Draw("P same")

data_graph.Draw("P same")
sys_errors.Draw("P same")
atlas_data_graph.Draw("P same")
atlas_sys_errors.Draw("P same")
ROOT.gStyle.SetEndErrorSize(4)
#legend = ROOT.TLegend(0.20, 0.65 - (0.10 if args.analysis == "ZZ" else 0.0), 0.55, 0.85 )
legend = ROOT.TLegend(*([0.20, 0.55, .55, .90] if args.analysis == "ZZ" else [0.20, 0.65, 0.55, 0.85]))
if args.analysis == "ZZ":
    legend.AddEntry(nnlo_graph,
            "#splitline{#sigma_{NNLO} Cascioli et. al.}"
            "{#scale[0.6]{ MMSTW2008, fixed #mu_{F}= #mu_{R}= M_{Z}}}",
            "lf"
    )
    legend.AddEntry(mcfm_nlo_graph,
            "#splitline{#sigma_{NLO+gg} Campbell et. al.}"
            "{#scale[0.6]{ MMSTW2008, fixed #mu_{F}= #mu_{R}= M_{Z}}}",
            "lf"
    )
legend.AddEntry(xsec_graph,
       #"#sigma_{pp #rightarrow WZ} Theory",
        "#splitline{#sigma_{NLO%s, M_{Z}#in[60, 120] GeV} MCFM}" 
        "{#scale[0.6]{NNPDF3.0, dynamic #mu_{F}= #mu_{R}= M_{%s}}}" % 
            (("+gg", "ZZ") if args.analysis == "ZZ" else ("", "WZ")),
        "lf"
)
if args.analysis == "ZZ":
    legend.AddEntry(zz2l2v_data_graph,
            "CMS #sigma_{pp #rightarrow ZZ}, 2l2#nu channel",
            "p"
    )
legend.AddEntry(atlas_data_graph,
        "ATLAS %s " % "#sigma_{pp #rightarrow %s}, %s channel" % (("WZ", "3l#nu") if args.analysis == "WZ" else ("ZZ", "4l")),
        "p"
)
legend.AddEntry(data_graph,
        "CMS %s " % "#sigma_{pp #rightarrow %s}, %s channel" % (("WZ", "3l#nu") if args.analysis == "WZ" else ("ZZ", "4l")),
        "p"
)
legend.Draw()
ROOT.gPad.RedrawAxis()

canvas.Print("~/public_html/DibosonPlots/%sCrossSection.pdf" % args.analysis)
