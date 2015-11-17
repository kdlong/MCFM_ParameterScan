#!/usr/bin/env python
import argparse
import os
import shutil
import string
import subprocess
import time

def getComLineArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--rseed", type=str, default="1089",
                        help="Random number seed for integration")
    parser.add_argument("-s", "--pdf", type=str, default="NNPDF",
                        help="PDF set to use")
    parser.add_argument("-n", "--job_name", type=str, default="",
                        help="Job name (todays date by default)")
    parser.add_argument("-p", "--processes",
                        default= ["ZZ_eemm", "WpZ_mee", "WmZ_mee"],
                        type=lambda x : [i.strip() for i in x.split(',')],
                        help="Processes to run")
    args = parser.parse_args()
    if args.job_name == "":
        args.job_name = time.strftime("%d_%m_%Y")
    return args
def fillTemplatedFile(template_file_name, out_file_name, template_dict):
    with open(template_file_name, "r") as templateFile:
        source = string.Template(templateFile.read())
        result = source.substitute(template_dict)
    with open(out_file_name, "w") as outFile:
        outFile.write(result)
def getPDFdict(pdf):
    pdf_dict = {}    
    if "NNPDF_LO" in pdf:
        pdf_dict["pdflabel"] = "NNPDF30_lo_as_0130"
        pdf_dict["ngroup"] = 4
        pdf_dict["nset"] = 101
        pdf_dict["LHAPDFgroup"] = "NNPDF30_lo_as_0130"
        pdf_dict["LHAPDFset"] = -1 
    elif "NNPDF" in pdf:
        pdf_dict["pdflabel"] = "NNPDF30_nlo_as_0118"
        pdf_dict["ngroup"] = 4
        pdf_dict["nset"] = 101
        pdf_dict["LHAPDFgroup"] = "NNPDF30_nlo_as_0118"
        pdf_dict["LHAPDFset"] = -1 
    elif "MMHT" in pdf:
        pdf_dict["pdflabel"] = "MMHT2014nlo68clas118"
        pdf_dict["ngroup"] = 4
        pdf_dict["nset"] = 51
        pdf_dict["LHAPDFgroup"] = "MMHT2014nlo68clas118"
        pdf_dict["LHAPDFset"] = -1 
    elif "CT14" in pdf:
        pdf_dict["pdflabel"] = "CT14nlo"
        pdf_dict["ngroup"] = 4
        pdf_dict["nset"] = 57
        pdf_dict["LHAPDFgroup"] = "CT14nlo"
        pdf_dict["LHAPDFset"] = -1 
    return pdf_dict
def make_mcfm_input(process, seed, scale, pdf, minmll, out_dir):
    processes = {"WpZ_mee": 71,
        "WmZ_mee" : 76,
        "WpZ_mvv" : 72,
        "WmZ_evv" : 77,
        "ZZ_eeee" : 90,
        "ZZ_eemm" : 81,
        "ZZ_eevv" : 82,
        "WpZ_bbar" : 73,
        "WpZ_ddbar" : 74,
        "WpZ_uubar" : 75,
        "WmZ_bbar" : 78,
        "WmZ_ddbar" : 79,
        "WmZ_uubar" : 80,
        "ggZZ_eemm" : 132
    }
    fill_dict = {}
    if process not in processes.keys():
        print "Invalid process!"
        exit(1)
    fill_dict["process"] = processes[process]
    fill_dict["name"] = process + "_minmll_" + minmll
    if "dyn" not in scale:
        fill_dict["qcdscale"] = scale + "d0"
        fill_dict["facscale"] = scale + "d0"
    else:
        ren_scale = 1 if "ggZZ" not in process else 0.5
        fac_scale = 1 if "ggZZ" not in process else 0.5
        if "facUp" in scale:
            fac_scale *= 2
        elif "facDown" in scale:
            fac_scale *= 0.5
        if "renUp" in scale:
            ren_scale *= 2
        elif "renDown" in scale:
            ren_scale *= 0.5
        fill_dict["qcdscale"] = "%.01fd0" % ren_scale
        fill_dict["facscale"] = "%.01fd0" % fac_scale
    fill_dict["dynamic"] = ".false." if "dyn" not in scale else "m(3456)"
    fill_dict.update(getPDFdict(pdf))
    fill_dict["order"] = "tota" if "ggZZ" not in process else "lord"
    if "ZZ" in process:
        fill_dict["m34min"] = minmll + "d0"
        fill_dict["m34max"] = "120d0"
        #fill_dict["m34max"] = "14000d0"
    else:
        fill_dict["m34min"] = "0d0"
        fill_dict["m34max"] = "14000d0"
    fill_dict["seed"] = seed
    fill_dict["m56min"] = minmll + "d0"
    fill_dict["m56max"] = "120d0"
    #fill_dict["m56max"] = "14000d0"
    fill_dict["makecuts"] = ".true."
    fillTemplatedFile("templates/input_template.DAT", 
        ''.join([out_dir, "/input.DAT"]), 
        fill_dict
    )
def make_condor_submit(directories):
    fillTemplatedFile("templates/condor_submit_template", 
        ''.join([directories["condor_run_info"], "/", "submit_condor"]), 
        directories)

def make_submit_files(process, seed, scale, pdf, minmll, out_dir_base, dir_names):
    out_dir = ''.join([out_dir_base, "/", process, "_scale", scale.split(".")[0], "_minmll_", minmll])
    os.mkdir(out_dir)
    directories = {}
    for dir_name in dir_names:
        directories[dir_name] = ''.join([out_dir, "/", dir_name])
        os.mkdir(directories[dir_name])
    make_mcfm_input(process, seed, scale, pdf, minmll, directories["transfer_files"])
    make_condor_submit(directories)
    shutil.copyfile("transfer_files/process.DAT",
        ''.join([directories["transfer_files"], "/", "process.DAT"]))
    shutil.copyfile("transfer_files/mcfm",
        ''.join([directories["transfer_files"], "/", "mcfm"]))
    shutil.copyfile("transfer_files/br.sm1",
        ''.join([directories["transfer_files"], "/", "br.sm1"]))
    shutil.copyfile("transfer_files/br.sm2",
        ''.join([directories["transfer_files"], "/", "br.sm2"]))
    return directories["condor_run_info"]
#scales = 
scales = ["dyn_facUp_renUp", "dyn_facDown_renDown", "dyn_facUp",
        "dyn_renUp", "dyn_facDown", "dyn_renDown"]
mllcuts = ["60"]
processes = ["ZZ_eemm", "WpZ_mee", "WmZ_mee"]
#processes = ["WpZ_mee", "WmZ_mee"]
#processes = ["ggZZ_eemm"]
#["WpZ_bbar", "WpZ_ddbar", "WpZ_uubar", "WmZ_bbar", "WmZ_ddbar", i



args = getComLineArgs()

condor_base_dir = "/data/kelong/MCFM_ParameterScan"
job_name = args.job_name
jobdir = ''.join([condor_base_dir, "/", job_name])
os.mkdir(jobdir)
dir_names = ["results", "condor_run_info", "transfer_files"]

for process in args.processes:
    for scale in scales:
        for mllcut in mllcuts:
            submit_dir = make_submit_files(process, args.rseed, scale, args.pdf, mllcut, jobdir, dir_names)
            subprocess.call(["condor_submit", ''.join([submit_dir, "/submit_condor"])])
