#!/usr/bin/python3

from math import *
import os
import sys
import aux_data
from operator import itemgetter
import matplotlib
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt

def pes_extract_a(batch_dir_inp, output_filename):
    
    task_list = os.listdir(batch_dir_inp)
    print("Total steps = {}".format(task_list.__len__()))

    out_data = []
    r_domain = []
    theta_domain = []
    out_data_sorted = []

    for task_id, task in enumerate(task_list):
        #print ("{} {}".format(task_id, task))
        task_data = {}

        batch_dir = "{}/{}".format(batch_dir_inp, task)
        #open DATA file
        data_file = open("{}/DATA".format(batch_dir), "r")
        data_file_lines = data_file.readlines()[0].split()
        task_r = float(data_file_lines[0])
        task_theta = float(data_file_lines[1])

        outfile = open("{}/orca.out".format(batch_dir), "r")

        toten_hf = []
        toten_ccsdt = []
        cbs_scf = []
        cbs_mdci = []
        cbs_final = []
        dipople_moment = []

        for line in outfile.readlines():
        
            if "Total Energy       :" in line:
                toten_hf.append(float(line.split()[3]))    
                pass
        
            if "E(CCSD(T))" in line:
                toten_ccsdt.append(float(line.split()[2]))    
                pass

            if "Extrapolated CBS SCF energy (4/5)" in line:
                cbs_scf.append(float(line.split()[6]))    
                pass

            if "Extrapolated CBS correlation energy (4/5) :" in line:
                cbs_mdci.append(float(line.split()[6]))    
                pass

            if "Estimated CBS total energy (4/5) : " in line:
                cbs_final.append(float(line.split()[6]))    
                pass

            if "Total Dipole Moment" in line:
                lsp = line.split()
                dipople_moment.append([float(lsp[4]), float(lsp[5]), float(lsp[6])])

        if task_r not in r_domain:
            r_domain.append(task_r)        

        if task_theta not in theta_domain:
            theta_domain.append(task_theta)

        task_data["r"] = task_r
        task_data["theta"] = task_theta
        task_data["E_HF_AB"] = toten_hf[0]
        task_data["E_HF_A"] = toten_hf[1]
        task_data["E_HF_B"] = toten_hf[2]   
        task_data["E_HF_BSSE"] = toten_hf[0] - toten_hf[1] - toten_hf[2]
        task_data["E_CCSDT_AB"] = toten_ccsdt[0]         
        task_data["E_CCSDT_A"] = toten_ccsdt[1]
        task_data["E_CCSDT_B"] = toten_ccsdt[2]
        task_data["E_CCSDT_B"] = toten_ccsdt[0] - toten_ccsdt[1] - toten_ccsdt[2]
        task_data["E_MDCI_CBS_AB"] = cbs_final[0]
        task_data["E_MDCI_CBS_A"] = cbs_final[1]
        task_data["E_MDCI_CBS_B"] = cbs_final[2]
        task_data["E_FINAL"] = aux_data.ha2cminv*(cbs_final[0] - cbs_final[1] - cbs_final[2])
        task_data["DIPOLE_MOMENT_MDCI"] = dipople_moment[1]

        out_data.append(task_data)

    out_data_sorted = sorted(out_data, key = lambda i: (i['theta'], i['r'])) 
    r_domain_s = sorted(r_domain)
    theta_domain_s = sorted(theta_domain)

    # print(r_domain_s, theta_domain_s)
    # z = []
    # for elem in out_data_sorted:
    #     z.append(elem["E_FINAL"])
    # print(z)

    # print("Min Z = {}".format(min(z)))

    # x = np.array(r_domain_s)
    # y = np.array(theta_domain_s)
    # X,Y = np.meshgrid(x,y)
    # Z = np.array(z).reshape(len(theta_domain_s), len(r_domain_s))
    # h = plt.contourf(X,Y,Z, 1000, levels = [-100 + a*2 for a in range(0, 1000)])
    # plt.show()

    output_data = open(output_filename, "w")
    output_data.write("r_angs,theta_rad,e_final_cminv,dm_x_au,dm_y_au,dm_z_au\n")
    for elem in out_data_sorted:
        output_data.write("{},{},{},{},{},{}\n".format(elem["r"], elem["theta"], elem["E_FINAL"],
        elem["DIPOLE_MOMENT_MDCI"][0], elem["DIPOLE_MOMENT_MDCI"][1], elem["DIPOLE_MOMENT_MDCI"][2]))

    #generate data for plots
    for t_i in range(0, len(theta_domain_s)):
        cur_r = open("r{}.data".format(t_i), "w")
        data_per_theta = [elem for elem in out_data_sorted if elem["theta"] == theta_domain_s[t_i]]
        for elem2 in data_per_theta:
            cur_r.write("{},{}\n".format(elem2["r"], elem2["E_FINAL"]))
   
    #perform convergence check at long range
    start_dist_check = 3.4 #Angstrom
    
    for theta_subspace_elem in theta_domain_s:
        elem_data = []
        #build data for current theta
        for elem in out_data_sorted:
            if (elem['theta']-theta_subspace_elem < 0.001) and (elem['r'] > start_dist_check):
                elem_data.append([elem['theta'], elem['r'], elem["E_FINAL"]])
                pass
        print(elem_data)            


    pass

def pes_extract_generic(batch_dir_inp, output_filename):
    
    task_list = os.listdir(batch_dir_inp)
    print("Total steps = {}".format(task_list.__len__()))

    out_data = []
    r_domain = []
    theta_domain = []
    out_data_sorted = []

    for task_id, task in enumerate(task_list):
        #print ("{} {}".format(task_id, task))
        task_data = {}

        batch_dir = "{}/{}".format(batch_dir_inp, task)
        #open DATA file
        data_file = open("{}/DATA".format(batch_dir), "r")
        data_file_lines = data_file.readlines()[0].split()
        task_r = float(data_file_lines[0])
        task_theta = float(data_file_lines[1])

        outfile = open("{}/orca.out".format(batch_dir), "r")

        e_hf = []
        e_mdci = []
        dipole_moments = []

        for out_line in outfile.readlines():
            if "Total Energy       :" in out_line:
                e_hf.append(float(out_line.split()[3]))    
                pass
        
            if "E(CCSD(T))" in out_line:
                e_mdci.append(float(out_line.split()[2]))    
                pass
            
            if "Total Dipole Moment" in out_line:
                lsp = out_line.split()
                dipole_moments.append([float(lsp[4]), float(lsp[5]), float(lsp[6])])

        task_data["r"] = task_r
        task_data["theta"] = task_theta
        task_data["E_AB_HF"] = e_hf[0]
        task_data["E_AG_HF"] = e_hf[1]
        task_data["E_GB_HF"] = e_hf[2] 
        task_data["E_HF_INT"] = e_hf[0] - e_hf[1] - e_hf[2]
        task_data["E_AB_CCSDT"] = e_mdci[0]  
        task_data["E_AG_CCSDT"] = e_mdci[1]
        task_data["E_GB_CCSDT"] = e_mdci[2]
        task_data["E_CCSDT_INT"] = aux_data.ha2cminv*(e_mdci[0] - e_mdci[1] - e_mdci[2])
        task_data["DIPOLE_MOMENT_HF"] = dipole_moments[0]
        task_data["DIPOLE_MOMENT_MDCI"] = dipole_moments[1]

        out_data.append(task_data)
        
        out_data_sorted = sorted(out_data, key = lambda i: (i['theta'], i['r'])) 
        r_domain_s = sorted(r_domain)
        theta_domain_s = sorted(theta_domain)

        #compact version
        output_data = open("{}_compact.pes".format(output_filename), "w")
        output_data.write("r_angs,theta_rad,e_final_cminv,dm_x_au,dm_y_au,dm_z_au\n")
        for elem in out_data_sorted:
            output_data.write("{:.8f},{:.8f},{},{},{},{}\n".format(elem["r"], elem["theta"], elem["E_CCSDT_INT"],
            elem["DIPOLE_MOMENT_MDCI"][0], elem["DIPOLE_MOMENT_MDCI"][1], elem["DIPOLE_MOMENT_MDCI"][2]))

        #detail version
        output_data_detail = open("{}_detail.pes".format(output_filename), "w")
        # """
        # r_angs 0 
        # theta_rad 1
        # e_final_cminv 2
        # e_ab_hf 3 
        # e_ag_hf 4 
        # e_gb_hf 5 
        # e_hf_int 6
        # e_ab_ccsdt 7 
        # e_ag_ccsdt 8 
        # e_gb_ccsdt 9 
        # e_ccsdt_int 10
        # dm_hf_x_au 11 
        # dm_hf_y_au 12 
        # dm_hf_z_au 13
        # dm_ccsdt_x_au 14 
        # dm_ccsdt_y_au 15 
        # dm_ccsdt_z_au 16
        # """
        output_data_detail.write(
            "r_angs,theta_rad,e_final_cminv,e_ab_hf,e_ag_hf,e_gb_hf,e_hf_int,e_ab_ccsdt,e_ag_ccsdt,e_gb_ccsdt,e_ccsdt_int,"
            )
        output_data_detail.write(
            "dm_hf_x_au,dm_hf_y_au,dm_hf_z_au,dm_x_au,dm_y_au,dm_z_au\n"
            )    
        for elem in out_data_sorted:
            #                           0      1    2  3  4  5  6  7  8  9  10 11 12 13 14 15 16
            output_data_detail.write("{:.8f},{:.8f},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(
                elem["r"], 
                elem["theta"], 
                elem["E_CCSDT_INT"],
                elem["E_AB_HF"],
                elem["E_AG_HF"],
                elem["E_GB_HF"],
                elem["E_AB_HF"] - elem["E_AG_HF"] - elem["E_GB_HF"],
                elem["E_AB_CCSDT"],
                elem["E_AG_CCSDT"],
                elem["E_GB_CCSDT"],
                elem["E_AB_CCSDT"] - elem["E_AG_CCSDT"] - elem["E_GB_CCSDT"],
                elem["DIPOLE_MOMENT_HF"][0], 
                elem["DIPOLE_MOMENT_HF"][1], 
                elem["DIPOLE_MOMENT_HF"][2],
                elem["DIPOLE_MOMENT_MDCI"][0], 
                elem["DIPOLE_MOMENT_MDCI"][1], 
                elem["DIPOLE_MOMENT_MDCI"][2])
                )
        
        
    #perform convergence check

    pass
    