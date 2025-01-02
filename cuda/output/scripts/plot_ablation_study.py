#! /u/sgupta45/conda/bin/python3
from common import *

reorder = lambda l, nc: sum((l[i::nc] for i in range(nc)), [])

def get_exec_time(policy, pim, app, get_total_time):
    mem_time = -1
    pim_time = -1
    cycles = -1
    mem_time_found = False
    pim_time_found = False

    filename = "../" + policy + "/"
    if app is not None:
        filename += app + "_"
    filename += pim

    for line in open(filename):
        if "launching kernel" in line:
            tokens = line.split()
            assert len(tokens) == 10, "/".join(
                    [policy, pim, app])
            stream = int(tokens[3])
            cycles = int(tokens[9])

            if stream == 1:
                if pim_time == -1:
                    pim_time = cycles
            else:
                if mem_time == -1:
                    mem_time = cycles

        elif "gpu_tot_sim_cycle" in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            cycles = int(tokens[2])

        elif "<<< MEM FINISHED >>>" in line:
            if not mem_time_found:
                mem_time = cycles - mem_time
                mem_time_found = True

        elif "<<< PIM FINISHED >>>" in line:
            if not pim_time_found:
                pim_time = cycles - pim_time
                pim_time_found = True

        if mem_time_found and pim_time_found:
            break

    if get_total_time:
        return cycles
    else:
        return mem_time, pim_time

def gen_plot(fairness_index, mem_speedup, pim_speedup, llm_speedup):
    def add_bar(axis, offset, color, hatch, label, stat_values, bottom):
        if hatch is None:
            axis.bar([i+offset for i in x], stat_values, edgecolor="k",
                    width=width, label=label, fc=color,
                    bottom=bottom, zorder=3.5)
        else:
            axis.bar([i+offset for i in x], stat_values, edgecolor="k",
                    width=width, fc=color, hatch=hatch,
                    bottom=bottom, zorder=3.5)

    def add_line(axis, color, label, stat_values):
        axis.plot([i for i in x], stat_values, color=color, marker="D",
                linewidth=2, markersize=12, markeredgewidth=2,
                markeredgecolor="k", label=label, zorder=3.5)

    # plot parameters
    x = np.arange(len(policies))

    # add the bars
    plt.clf()
    fig, axis = plt.subplots(figsize=(6, 6), dpi=600)
    plt.rc("axes", axisbelow=True)

    width = 0.4  # two bars per policy
    offset = -0.2

    # add fairness index
    add_bar(axis, offset, colormap[0], None, "FI", fairness_index, None)
    offset += width

    # add throughput
    add_bar(axis, offset, colormap[2], "//", "ST", mem_speedup, None)
    add_bar(axis, offset, colormap[2], None, "ST", pim_speedup, mem_speedup)

    # add LLM speedup
    add_line(axis, colormap[4], "LLM", llm_speedup)

    axis.set_xticks(x)
    axis.set_xticklabels([labels[policy] for policy in policies], size=30)
    axis.tick_params(axis="x", labelrotation=90)

    axis.yaxis.set_tick_params(labelsize=25)
    axis.set_ylim([0, 2])
    axis.yaxis.set_major_locator(plt.MultipleLocator(0.2))

    ncol = 3
    axis.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", ncol=ncol,
            mode="expand", borderaxespad=0, handletextpad=0.4, fontsize=25)
    axis.grid(zorder=2.5, axis="y", color="silver", linestyle="-", linewidth=1)

    # save the image
    plt.savefig("../plots/ablation_study.png", bbox_inches="tight")

policies = [
        "frfcfs_vc_2/cap_32",
        "paws_fixed_cap_vc_2/cap_64",
        "pim_frfcfs_vc_2/cap_256",
        "pim_frfcfs_vc_2/cap_256_slowdown_0.5"
]

labels = {
        "frfcfs_vc_2/cap_32": "FR-FCFS-Cap",
        "paws_fixed_cap_vc_2/cap_64": "+Mode Cap",
        "pim_frfcfs_vc_2/cap_256": "+First Mode",
        "pim_frfcfs_vc_2/cap_256_slowdown_0.5": "+Asym. Cap"
}

pim_kernel = "stream_copy"
gpu_kernel = "hotspot3D"

# Load baseline execution times
base_mem_time = get_base_mem_exec_time()
base_pim_time = get_base_pim_exec_time()
base_llm_time = \
        get_exec_time("pim_frfcfs/cap_0", "llm_mem_only", None, True) + \
        get_exec_time("pim_frfcfs/cap_0", "llm_pim_only", None, True)

avg_fairness_index = []
avg_mem_speedup = []
avg_pim_speedup = []
llm_speedup = []

for policy in policies:
    fairness_index = []
    mem_speedup = []
    pim_speedup = []

    for app in applications:
        mem_time, pim_time = get_exec_time(policy, pim_kernel, app, False)

        mem_speedup.append(base_mem_time[app] / mem_time)
        pim_speedup.append(base_pim_time[pim_kernel] / pim_time)

        fairness_index.append(min(mem_speedup[-1] / pim_speedup[-1],
                pim_speedup[-1] / mem_speedup[-1]))

    avg_mem_speedup.append(amean(mem_speedup))
    avg_pim_speedup.append(amean(pim_speedup))
    avg_fairness_index.append(gmean(fairness_index))

    llm_time = get_exec_time(policy, "llm", None, True)
    llm_speedup.append(base_llm_time / llm_time)

gen_plot(avg_fairness_index, avg_mem_speedup, avg_pim_speedup, llm_speedup)
