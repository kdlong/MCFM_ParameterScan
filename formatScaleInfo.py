#!/usr/bin/env python

import argparse
import subprocess
import glob
import re
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--folder", type=str, required=True)
parser.add_argument("--remove_gg", action='store_true')
parser.add_argument("--format_as_data", action='store_true')
parser.add_argument("--removebr", action='store_true')
parser.add_argument("--ggonly", action='store_true')
parser.add_argument("-p", "--processes",
                    type=lambda x : [i.strip() for i in x.split(',')],
                    required=True)
args = parser.parse_args()

filelist = glob.glob('/'.join([args.folder, "*", "condor_run_info", "stdout*"]))

values = subprocess.Popen(['grep', "Central value"] + filelist, stdout= subprocess.PIPE)
unc = subprocess.Popen(['grep', "-A", "1", "Absolute PDF"] + filelist, stdout= subprocess.PIPE)
gg = subprocess.Popen(['grep', "GG"] + filelist, stdout= subprocess.PIPE)
cross_secs = values.stdout.readlines()
gg_results = gg.stdout.readlines()
pdf_uncs = [line for line in unc.stdout.readlines() if "Symmetric" in line]
raw_results = {}
summed_results = {}
for xsec_line, pdf_line, gg_line in zip(cross_secs, pdf_uncs, gg_results):
    path_arr = xsec_line.split("/")
    path = '/'.join(path_arr[0:path_arr.index("condor_run_info")])
    xsec = float(re.findall('\d+.\d*', xsec_line)[-1])
    pdf_unc = float(re.findall('\d+.\d*', pdf_line)[-1])
    if args.remove_gg:
        ggxsec = float(re.findall('\d+.\d*', gg_line)[-2])
        xsec -= ggxsec
    elif args.ggonly:
        xsec = float(re.findall('\d+.\d*', gg_line)[-2])
    raw_results[path] = {"xsec" : xsec, "pdf_unc" : pdf_unc}
    sum_path = path.replace("WpZ", "WZ") if "WpZ" in path else path.replace("WmZ", "WZ")
    if sum_path not in summed_results:
        summed_results[sum_path] = { "xsec" : xsec, "pdf_unc" : pdf_unc}
    else:
        summed_results[sum_path]["xsec"] += xsec
        summed_results[sum_path]["pdf_unc"] += pdf_unc
scale_strings = ["dyn_facDown_renDown", "dyn_facUp_renUp", "dyn_renDown", "dyn_facUp",
        "dyn_facDown", "dyn_renUp", "dyn"]
for process in args.processes:
    scale_results = OrderedDict.fromkeys(scale_strings, {"xsec" : 0, "pdf_unc" : 0})
    for key, value in summed_results.iteritems():
        if process not in key: 
            continue
        for scale in scale_strings:
            if scale in key and "_".join([scale, "ren"]) not in key and "_".join([scale, "fac"]) not in key:
                scale_results[scale] = value
    names = ["Central", "PDF", "Max Scale", "Min scale", "FacDownRenDown",  \
            "facUprenUp", "renDown", "facUp", "facDown", "renUp"]
    info = [str(scale_results["dyn"]["xsec"]), str(scale_results["dyn"]["pdf_unc"])]
    scale_values = [value["xsec"] for value in scale_results.values()[:-1]]
    info += [str(max(scale_values)), str(min(scale_values))]
    if not args.format_as_data:
        print "Results for process %s" % process
        format_string = " ".join(["{%i:^15}" %i for i in xrange(0,10)])
        print format_string.format(*names)
        print format_string.format(*(info + [str(value["xsec"]) for value in scale_results.values()[:-1]]))
    else:
        # Format as <energy> <central xsec> <scale up> <scale down> <pdf uncertainty>
        energy = str(float(re.findall('\d+', args.folder)[-1])/1000)
        scale = 1
        if args.removebr:
            if "ZZ" in process:
                #In pb
                scale = 0.5/(1000*0.0363*0.0366)
            elif "WZ" in process:
                scale = 1/(1000*0.0363*0.1057)
        print " ".join([energy, str(float(info[0])*scale)] +
            [str(value["xsec"]*scale) for value in scale_results.values()[:2]] +
            [str(float(info[1])*scale)])
    #print "\t\t".join(info + [str(value["xsec"]) for value in scale_results.values()[:-1]])

