#! /u/sgupta45/conda/bin/python3
from common import *
import statistics

def get_stats(policies):
    avg_mem_speedup = {p:[] for p in policies}
    avg_pim_speedup = {p:[] for p in policies}

    for pim in pim_kernels:
        if pim == 'stream_triad':
            stream_add_index = pim_kernels.index('stream_add')
            for policy in policies:
                avg_mem_speedup[policy].append(
                        avg_mem_speedup[policy][stream_add_index])
                avg_pim_speedup[policy].append(
                        avg_pim_speedup[policy][stream_add_index])
            continue

        for policy in policies:
            mem_speedup = []
            pim_speedup = []
            throughput = []

            for app in applications:
                mem_time, pim_time = get_exec_time(policy, pim, app, True,
                        True)

                mem_speedup.append(base_mem_time[app] / mem_time)
                pim_speedup.append(base_pim_time[pim] / pim_time)

                throughput.append(mem_speedup[-1] + pim_speedup[-1])

            avg_mem_speedup[policy].append(amean(mem_speedup))
            avg_pim_speedup[policy].append(amean(pim_speedup))

    return avg_mem_speedup, avg_pim_speedup

def gen_plot_all_pim(mem_speedup, pim_speedup):
    def add_bar(axis, offset, policy, hatch, stat_values, bottom):
        plabel = labels[policy] if policy in labels else policy

        if bottom is None:
            axis.bar([i+offset for i in x], stat_values[policy], edgecolor='k',
                    width=width, fc=colors[policy], hatch=hatch,
                    zorder=3.5)
        else:
            axis.bar([i+offset for i in x], stat_values[policy], edgecolor='k',
                    width=width, label=plabel, fc=colors[policy],
                    bottom=bottom[policy], zorder=3.5)

    num_pim_kernels = len(pim_kernels) + 1

    # plot parameters
    x = np.arange((len(pim_kernels) + 1) * 2)
    ylim = 2
    hatches = ["//"]
    next_hatch = 0

    # add the bars
    plt.clf()
    fig, axis = plt.subplots(figsize=(54, 6), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(policies)
    if len(policies) % 2 == 0:
        offset = -width * (0.5 + ((len(policies) / 2) - 1))
    else:
        offset = -width * ((len(policies) - 1) / 2)

    for policy in policies:
        add_bar(axis, offset, policy, hatches[next_hatch], mem_speedup, None)
        add_bar(axis, offset, policy, hatches[next_hatch], pim_speedup,
                mem_speedup)
        offset += width
        next_hatch = (next_hatch + 1) % len(hatches)

    axis.set_xticks(x)
    axis.set_xticklabels(["VC1", "VC2"] * num_pim_kernels, size=25)
    axis.set_ylabel("System Throughput", size=30)
    axis.yaxis.set_tick_params(labelsize=25)
    axis.set_ylim([0, ylim])
    axis.yaxis.set_major_locator(plt.MultipleLocator(ylim / 5))

    secondary_ax = axis.secondary_xaxis(location = 0)
    secondary_ax.set_xticks([(i * 2) + 0.5 for i in range(num_pim_kernels)])
    secondary_ax.set_xticklabels([pim_labels[pim] for pim in pim_kernels] + \
            ["AMean"], size=30)
    secondary_ax.tick_params('x', length=35, color='w')

    tertiary_ax = axis.secondary_xaxis(location = 0)
    tertiary_ax.set_xticks([(i * 2) + 1.5 for i in range(num_pim_kernels - 1)])
    tertiary_ax.set_xticklabels(['' for i in range(num_pim_kernels - 1)])
    tertiary_ax.tick_params('x', length=65, width=2)

    axis.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    axis.grid(zorder=2.5, axis='y', color='silver', linestyle='-', linewidth=1)
    axis.vlines([(i * 2) + 1.5 for i in range(num_pim_kernels - 1)], 0, ylim,
            linestyles='dashed', color='k', linewidth=2)

    # save the image
    plt.savefig('../plots/all_weighted_speedup_all_vcs.png',
            bbox_inches='tight')

# Load baseline execution times
base_mem_time = get_base_mem_exec_time()
base_pim_time = get_base_pim_exec_time()

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

vc_1_mem_speedup, vc_1_pim_speedup = get_stats(policies)
vc_2_mem_speedup, vc_2_pim_speedup = get_stats(policies_vc_2)

avg_mem_speedup = {p:[] for p in policies}
avg_pim_speedup = {p:[] for p in policies}

for i in range(len(policies)):
    policy = policies[i]
    policy_vc_2 = policies_vc_2[i]

    vc_1_avg = amean(vc_1_mem_speedup[policies[i]])
    vc_2_avg = amean(vc_2_mem_speedup[policies_vc_2[i]])

    for j in range(len(pim_kernels)):
        avg_mem_speedup[policy].append(vc_1_mem_speedup[policy][j])
        avg_mem_speedup[policy].append(vc_2_mem_speedup[policy_vc_2][j])

    avg_mem_speedup[policy].append(vc_1_avg)
    avg_mem_speedup[policy].append(vc_2_avg)

    vc_1_avg = amean(vc_1_pim_speedup[policies[i]])
    vc_2_avg = amean(vc_2_pim_speedup[policies_vc_2[i]])

    for j in range(len(pim_kernels)):
        avg_pim_speedup[policy].append(vc_1_pim_speedup[policy][j])
        avg_pim_speedup[policy].append(vc_2_pim_speedup[policy_vc_2][j])

    avg_pim_speedup[policy].append(vc_1_avg)
    avg_pim_speedup[policy].append(vc_2_avg)

gen_plot_all_pim(avg_mem_speedup, avg_pim_speedup)
