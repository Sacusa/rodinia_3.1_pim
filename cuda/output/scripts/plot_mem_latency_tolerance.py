#! /u/sgupta45/conda/bin/python3
from common import *

colormap = matplotlib.cm.get_cmap("tab20c").colors
wait_time_policies = [
        'pim_frfcfs/single_apps/artificial_wait_time_0',
        'pim_frfcfs/single_apps/artificial_wait_time_1',
        'pim_frfcfs/single_apps/artificial_wait_time_10',
        'pim_frfcfs/single_apps/artificial_wait_time_100'
        ]
colors = {
        'pim_frfcfs/single_apps/artificial_wait_time_0': 'k',
        'pim_frfcfs/single_apps/artificial_wait_time_1': colormap[0],
        'pim_frfcfs/single_apps/artificial_wait_time_10': colormap[1],
        'pim_frfcfs/single_apps/artificial_wait_time_100': colormap[2]
        }
labels = {
        'pim_frfcfs/single_apps/artificial_wait_time_0': 'Base',
        'pim_frfcfs/single_apps/artificial_wait_time_1': '1',
        'pim_frfcfs/single_apps/artificial_wait_time_10': '10',
        'pim_frfcfs/single_apps/artificial_wait_time_100': '100'
        }

def gen_plot():
    def add_bar(offset, policy):
        plt.bar([i+offset for i in x], speedup[policy], edgecolor='k',
                width=width, label=labels[policy], fc=colors[policy])

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(wait_time_policies)
    if len(wait_time_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(wait_time_policies) / 2) - 1))
    else:
        offset = -width * ((len(wait_time_policies) - 1) / 2)

    for policy in wait_time_policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, applications + ['GMean'], fontsize=30, rotation='vertical')
    plt.ylabel('Speedup', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 1])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(wait_time_policies), mode='expand', borderaxespad=0,
            fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_mem_latency_tolerance.pdf',
            bbox_inches='tight')

speedup = {p:[] for p in wait_time_policies}

for i, app in enumerate(applications):
    for policy in wait_time_policies:
        speedup[policy].append(get_exec_time(policy, 'nop', app, True, False))

    base_val = speedup['pim_frfcfs/single_apps/artificial_wait_time_0'][-1]
    for policy in wait_time_policies:
        speedup[policy][-1] = base_val / speedup[policy][-1]

for policy in wait_time_policies:
    speedup[policy].append(gmean(speedup[policy]))

gen_plot()
