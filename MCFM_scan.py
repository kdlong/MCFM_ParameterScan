#!/usr/bin/env python
import os
import shutil
import string
import subprocess

def fillTemplatedFile(template_file_name, out_file_name, template_dict):
    with open(template_file_name, "r") as templateFile:
        source = string.Template(templateFile.read())
        result = source.substitute(template_dict)
    with open(out_file_name, "w") as outFile:
        outFile.write(result)
def getPDFdict(pdf):
    pdf_dict = {}    
    if "NNPDF" in pdf:
        pdf_dict["pdflabel"] = "NNPDF30_nlo_as_0118"
        pdf_dict["ngroup"] = 4
        pdf_dict["nset"] = 46
        pdf_dict["LHAPDFgroup"] = "NNPDF30_nlo_as_0118"
        pdf_dict["LHAPDFset"] = -1 
    return pdf_dict
def make_mcfm_input(process, scale, pdf, minmll, out_dir):
    processes = {"WpZ_mee": 71,
        "WmZ_mee" : 76,
        "ZZ_eeee" : 90,
        "ZZ_eemm" : 81
    }
    fill_dict = {}
    fill_dict["process"] = processes[process]
    fill_dict["name"] = process + "_minmll_" + minmll
    fill_dict["qcdscale"] = scale + "d0" if "dyn" not in scale else "1d0"
    fill_dict["facscale"] = scale + "d0" if "dyn" not in scale else "1d0"
    fill_dict["dynamic"] = ".false." if "dyn" not in scale else "m(3456)"
    fill_dict.update(getPDFdict(pdf))
    if "ZZ" in process:
        fill_dict["m34min"] = minmll + "d0"
        fill_dict["m34max"] = "14000d0"
    else:
        fill_dict["m34min"] = "0d0"
        fill_dict["m34max"] = "14000d0"
    fill_dict["m56min"] = minmll + "d0"
    fill_dict["m56max"] = "14000d0"
    fill_dict["makecuts"] = ".false."
    fillTemplatedFile("templates/input_template.DAT", 
        ''.join([out_dir, "/input.DAT"]), 
        fill_dict
    )
def make_condor_submit(directories):
    fillTemplatedFile("templates/condor_submit_template", 
        ''.join([directories["condor_run_info"], "/", "submit_condor"]), 
        directories)

def make_submit_files(process, scale, pdf, minmll, out_dir_base, dir_names):
    out_dir = ''.join([out_dir_base, "/", process, "_scale", scale.split(".")[0], "_minmll_", minmll])
    os.mkdir(out_dir)
    directories = {}
    for dir_name in dir_names:
        directories[dir_name] = ''.join([out_dir, "/", dir_name])
        os.mkdir(directories[dir_name])
    make_mcfm_input(process, scale, pdf, minmll, directories["transfer_files"])
    make_condor_submit(directories)
    shutil.copyfile("transfer_files/process.DAT",
            ''.join([directories["transfer_files"], "/", "process.DAT"]))
    return directories["condor_run_info"]
scales = ["60", "91.1876", "dynscale", "182.3752"]
mllcuts = ["60", "4", "12"]
processes = ["WpZ_mee", "WmZ_mee"]
pdf = "NNPDF"

condor_base_dir = "/data/kelong/MCFM_ParameterScan"
dir_names = ["results", "condor_run_info", "transfer_files"]

for process in processes:
    for scale in scales:
        for mllcut in mllcuts:
            submit_dir = make_submit_files(process, scale, pdf, mllcut, condor_base_dir, dir_names)
            filename = ''.join(["output/", process, "_minmll", mllcut, "/",
                process, "_scale" if "dyn" not in scale else "_", scale,
                "_28_07_15.out"])
            subprocess.call(["condor_submit", 
                ''.join([submit_dir, "/submit_condor"])]
            )
