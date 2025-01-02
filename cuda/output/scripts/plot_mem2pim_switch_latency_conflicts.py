#! /u/sgupta45/conda/bin/python3
from common import *
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

def get_switch_overheads(stats_db, policies):
    avg_switch_latency = {p:[] for p in policies}
    avg_switch_conflicts = {p:[] for p in policies}

    for pim in pim_kernels:
        switch_latency = {p:[] for p in policies}
        switch_conflicts = {p:[] for p in policies}

        for policy in policies:
            for app in applications:
                switch_latency[policy].append(
                        stats_db[policy][pim][app]["switch_latency"])
                switch_conflicts[policy].append(
                        stats_db[policy][pim][app]["switch_conflicts"])

        ##################
        # Normalize values
        ##################
        for policy in policies:
            avg_switch_latency[policy].append(amean(switch_latency[policy]))
            avg_switch_conflicts[policy].append(
                    amean(switch_conflicts[policy]))

    for policy in policies:
        avg_switch_latency[policy].append(amean(avg_switch_latency[policy]))
        avg_switch_conflicts[policy].append(
                amean(avg_switch_conflicts[policy]))

    return [avg_switch_latency[policy][-1] for policy in policies], \
            [avg_switch_conflicts[policy][-1] for policy in policies]

def gen_plot(vc1_stats, vc2_stats, ylabel, filename):
    def add_bar(offset, yval, label, color):
        plt.bar([i+offset for i in x], yval, edgecolor="k", width=width,
                label=label, fc=color)

    # plot parameters
    x = np.arange(len(policies))

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 6), dpi=600)
    plt.rc("axes", axisbelow=True)

    width = 0.4

    add_bar(-(width / 2), vc1_stats, "VC1", colormap[0])
    add_bar(  width / 2,  vc2_stats, "VC2", colormap[2])

    plt.xticks(x, [labels[policy] for policy in policies], fontsize=25)
    plt.yticks(fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    #plt.ylim([0, 1])
    #plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=2, mode="expand", borderaxespad=0, fontsize=25)
    plt.grid(axis="y", color="silver", linestyle="-", linewidth=1)

    # save the image
    plt.savefig("../plots/all_" + filename + "_all_vcs.pdf",
            bbox_inches="tight")

# Load stats_db
stats_db = None

if len(sys.argv) == 2:
    if sys.argv[1] == "refresh":
        stats_db = recreate_and_return_stats_db()
    else:
        print("Incorrect argv\n")
        exit(-1)
else:
    stats_db = load_db()

switch_latency_vc_1, switch_conflicts_vc_1 = \
        get_switch_overheads(stats_db, policies)
switch_latency_vc_2, switch_conflicts_vc_2 = \
        get_switch_overheads(stats_db, policies_vc_2)

gen_plot(switch_latency_vc_1, switch_latency_vc_2,
        "MEM Drain Latency / Switch", "switch_latency")
gen_plot(switch_conflicts_vc_1, switch_conflicts_vc_2,
        "MEM Conflicts / Switch", "switch_conflicts")
