#! /u/sgupta45/conda/bin/python3
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def get_exec_time(policies):
    exec_time = []

    for policy in policies:
        mem_time = 0
        pim_time = 0
        mem_found = False
        pim_found = False

        cycle_count = -1

        for line in open('../' + policy + '/llm'):
            if 'gpu_tot_sim_cycle' in line:
                tokens = line.split()
                assert(len(tokens) == 3)
                cycle_count = int(tokens[2])
            elif 'MEM FINISHED' in line:
                mem_time = cycle_count
                mem_found = True
            elif 'PIM FINISHED' in line:
                pim_time = cycle_count
                pim_found = True

            if mem_found and pim_found: break

        exec_time.append(max(mem_time, pim_time))

    return exec_time

def gen_plot():
    def add_bar(offset, yval, label, color):
        plt.bar([i+offset for i in x], yval, edgecolor='k', width=width,
                label=label, fc=color)

    # plot parameters
    x = np.arange(len(policies))

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 6), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.4

    add_bar(-(width / 2), exec_time_vc_1, 'VC1', colormap[0])
    add_bar(  width / 2,  exec_time_vc_2, 'VC2', colormap[2])

    plt.xticks(x, [labels[policy] for policy in policies], fontsize=23)
    plt.yticks(fontsize=30)
    plt.ylabel('Speedup (norm. to\nsequential execution)', fontsize=30)
    plt.ylim([0, 1.6])
    #plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=2, mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    plt.axhline(y=ideal_exec_time, color='r', linestyle='-',
            linewidth=3)
    plt.text(x[-1], ideal_exec_time + 0.06, 'Ideal', fontsize=30,
            fontstyle='italic')

    # save the image
    plt.savefig('../plots/llm_analysis_all_vcs.png',
            bbox_inches='tight')

###############################
# Load baseline execution times
###############################

base_mem_time = 0
base_pim_time = 0

for line in open('../pim_frfcfs/cap_0/llm_mem_only'):
    if 'gpu_tot_sim_cycle' in line:
        tokens = line.split()
        assert(len(tokens) == 3)
        base_mem_time = int(tokens[2])

for line in open('../pim_frfcfs/cap_0/llm_pim_only'):
    if 'gpu_tot_sim_cycle' in line:
        tokens = line.split()
        assert(len(tokens) == 3)
        base_pim_time = int(tokens[2])

sequential_exec_time = base_mem_time + base_pim_time
ideal_exec_time = sequential_exec_time / max(base_mem_time, base_pim_time)

# PIM-FRFCFS policies
pim_frfcfs_vc_1 = "pim_frfcfs/cap_256_slowdown_0.5"
pim_frfcfs_vc_2 = "pim_frfcfs_vc_2/cap_64"

# Extract the label for PIM-FRFCFS
has_pim_frfcfs = False
pim_frfcfs_label = ""
for i in range(len(policies)):
    if "pim_frfcfs" in policies[i]:
        has_pim_frfcfs = True
        pim_frfcfs_label = labels[policies[i]]

        del policies[i]
        del policies_vc_2[i]
        break

if has_pim_frfcfs: labels["pim_frfcfs"] = pim_frfcfs_label

# Get VC1 execution time
if has_pim_frfcfs: policies += [pim_frfcfs_vc_1]
exec_time_vc_1 = get_exec_time(policies)
if has_pim_frfcfs: del policies[-1]

# Get VC2 execution time
if has_pim_frfcfs: policies_vc_2 += [pim_frfcfs_vc_2]
exec_time_vc_2 = get_exec_time(policies_vc_2)
if has_pim_frfcfs: del policies_vc_2[-1]

# Combine the two dictionaries
if has_pim_frfcfs: policies += ["pim_frfcfs"]
exec_time = []

for i in range(len(policies)):
    if exec_time_vc_1[i] > 0:
        exec_time_vc_1[i] = sequential_exec_time / exec_time_vc_1[i]
    exec_time.append(exec_time_vc_1[i])

    if exec_time_vc_2[i] > 0:
        exec_time_vc_2[i] = sequential_exec_time / exec_time_vc_2[i]
    exec_time.append(exec_time_vc_2[i])

gen_plot()
