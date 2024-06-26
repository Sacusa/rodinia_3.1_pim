#! /u/sgupta45/conda/bin/python3
from common import *

colormap = matplotlib.cm.get_cmap("tab20c").colors

cap_policies = [
        'pim_frfcfs_util/cap_0',
        'pim_frfcfs_util/cap_8_slowdown_4',
        'pim_frfcfs_util/cap_16_slowdown_4',
        'pim_frfcfs_util/cap_32_slowdown_4',
        'pim_frfcfs_util/cap_64_slowdown_4',
        'pim_frfcfs_util/cap_128_slowdown_4'
        ]
cap_colors = {
        'pim_frfcfs_util/cap_0': 'k',
        'pim_frfcfs_util/cap_8_slowdown_4': colormap[16],
        'pim_frfcfs_util/cap_16_slowdown_4': colormap[0],
        'pim_frfcfs_util/cap_32_slowdown_4': colormap[1],
        'pim_frfcfs_util/cap_64_slowdown_4': colormap[2],
        'pim_frfcfs_util/cap_128_slowdown_4': colormap[3]
        }

slowdown_policies = [
        'pim_frfcfs_util/cap_8_slowdown_0.33',
        'pim_frfcfs_util/cap_8_slowdown_1',
        'pim_frfcfs_util/cap_8_slowdown_4'
        ]
slowdown_colors = {
        'pim_frfcfs_util/cap_8_slowdown_0.33': colormap[0],
        'pim_frfcfs_util/cap_8_slowdown_1': colormap[1],
        'pim_frfcfs_util/cap_8_slowdown_4': colormap[2]
        }

def get_stats(sweep_parameter):
    if sweep_parameter == 'cap':
        pim_frfcfs_util_policies = cap_policies
    elif sweep_parameter == 'slowdown':
        pim_frfcfs_util_policies = slowdown_policies

    avg_fairness_index = {p:[] for p in pim_frfcfs_util_policies}
    avg_throughput = {p:[] for p in pim_frfcfs_util_policies}

    for pim in pim_kernels:
        if pim == 'stream_triad':
            stream_add_index = pim_kernels.index('stream_add')
            for policy in pim_frfcfs_util_policies:
                avg_fairness_index[policy].append(
                        avg_fairness_index[policy][stream_add_index])
                avg_throughput[policy].append(
                        avg_throughput[policy][stream_add_index])
            continue

        for policy in pim_frfcfs_util_policies:
            print(pim, policy)

            fairness_index = []
            throughput = []

            for app in applications:
                mem_time, pim_time = get_exec_time(policy, pim, app, True,
                        True)

                mem_speedup = base_mem_time[app] / mem_time
                pim_speedup = base_pim_time[pim] / pim_time

                fairness_index.append(min(mem_speedup / pim_speedup,
                    pim_speedup / mem_speedup))
                throughput.append(mem_speedup + pim_speedup)

            avg_fairness_index[policy].append(gmean(fairness_index))
            avg_throughput[policy].append(gmean(throughput))

    for policy in pim_frfcfs_util_policies:
        avg_fairness_index[policy].append(gmean(avg_fairness_index[policy]))
        avg_throughput[policy].append(gmean(avg_throughput[policy]))

    return avg_fairness_index, avg_throughput

def gen_plot():
    def add_bar(axis, offset, yvals, label, color, zorder):
        axis.bar([i+offset for i in x], yvals, edgecolor='k', width=width,
                label=label, fc=color, zorder=zorder)

    # plot parameters
    x = np.arange(len(cap_policies) + len(slowdown_policies))

    # add the bars
    plt.clf()
    fig, ax1 = plt.subplots(figsize=(24, 8), dpi=600)
    ax2 = ax1.twinx()
    plt.rc('axes', axisbelow=True)

    width = 0.4  # 0.8 / 2

    add_bar(ax1, -0.2, fairness_index, 'Fairness Index', colormap[0], 3.5)
    add_bar(ax2, 0.2, throughput, 'Throughput', colormap[4], 4.5)

    ax1.set_xticks(x)
    ax1.set_xticklabels([policy.split('_')[3] for policy in cap_policies] + \
            [policy.split('_')[5] for policy in slowdown_policies], size=25)
    ax1.set_ylabel('Fairness Index', size=30)
    ax1.yaxis.set_tick_params(labelsize=30)
    ax1.set_ylim([0, 1])
    ax1.yaxis.set_major_locator(plt.MultipleLocator(0.1))

    ax2.set_ylabel('Throughput', size=30)
    ax2.yaxis.set_tick_params(labelsize=30)
    ax2.set_ylim([0, 2])
    ax2.yaxis.set_major_locator(plt.MultipleLocator(0.2))

    secondary_ax = ax1.secondary_xaxis(location = 0)
    secondary_ax.set_xticks([2.5, 7])
    secondary_ax.tick_params('x', length=35, color='w')
    secondary_ax.set_xticklabels(['Cap', 'Tau'], size=30)

    tertiary_ax = ax1.secondary_xaxis(location = 0)
    tertiary_ax.set_xticks([5.5])
    tertiary_ax.tick_params('x', length=65, width=2)
    tertiary_ax.set_xticklabels([''])

    ax1.grid(zorder=2.5, axis='y', color='silver', linestyle='-', linewidth=1)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(0, 1.02, 1, 0.2),
            loc="lower left", ncol=2, mode='expand', borderaxespad=0,
            fontsize=25)

    # save the image
    plt.savefig('../plots/all_pim_frfcfs_util_throughput_fairness_combined.pdf',
            bbox_inches='tight')

base_mem_time = get_base_mem_exec_time()
base_pim_time = get_base_pim_exec_time()

fairness_index = []
throughput = []

fi, t = get_stats('cap')
fairness_index += [fi[p][-1] for p in cap_policies]
throughput += [t[p][-1] for p in cap_policies]

fi, t = get_stats('slowdown')
fairness_index += [fi[p][-1] for p in slowdown_policies]
throughput += [t[p][-1] for p in slowdown_policies]

gen_plot()
