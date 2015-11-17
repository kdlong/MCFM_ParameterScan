#!/usr/bin/env python

import argparse
import subprocess
import glob
import re

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", type=str, required=True)
args = parser.parse_args()

filelist = glob.glob('/'.join([args.folder, "W*", "condor_run_info", "stdout*"]))

values = subprocess.Popen(['grep', "Central value"] + filelist, stdout= subprocess.PIPE)
unc = subprocess.Popen(['grep', "-A", "1", "Absolute PDF"] + filelist, stdout= subprocess.PIPE)

cross_secs = values.stdout.readlines()
pdf_uncs = [line for line in unc.stdout.readlines() if "Symmetric" in line]

raw_results = {}
summed_results = {}
for xsec_line, pdf_line in zip(cross_secs, pdf_uncs):
    path_arr = xsec_line.split("/")     
    path = '/'.join(path_arr[0:path_arr.index("condor_run_info")])
    xsec = float(re.findall('\d+.\d*', xsec_line)[-1])
    pdf_unc = float(re.findall('\d+.\d*', pdf_line)[-1])
    raw_results[path] = {"xsec" : xsec, "pdf_unc" : pdf_unc}
    sum_path = path.replace("WpZ", "WZ") if "WpZ" in path else path.replace("WmZ", "WZ")
    if sum_path not in summed_results:
        summed_results[sum_path] = { "xsec" : xsec, "pdf_unc" : pdf_unc}
    else:
        summed_results[sum_path]["xsec"] += xsec
        summed_results[sum_path]["pdf_unc"] += pdf_unc

print "Separated W+/-Z results were:"
for key, value in raw_results.iteritems():
    print key
    print "\tCross section: %f" % value["xsec"]
    print "\tPDF uncertainty: %f" % value["pdf_unc"]

print "-"*70
print "Summed WZ results were:"
for key, value in summed_results.iteritems():
    print key
    print "\tCross section: %f" % value["xsec"]
    print "\tPDF uncertainty: %f" % value["pdf_unc"]
