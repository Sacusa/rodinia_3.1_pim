#! /u/sgupta45/conda/bin/python3
from common import *

def add_plot_all_pim(speedup, ylabel, filename):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], speedup[policy], edgecolor='k',
                width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(48, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(policies)
    if len(policies) % 2 == 0:
        offset = -width * (0.5 + ((len(policies) / 2) - 1))
    else:
        offset = -width * ((len(policies) - 1) / 2)

    for policy in policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, [app_labels[app] for app in applications] + ['GMean'],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_' + filename + '.pdf',
            bbox_inches='tight')

base_mem_time = get_base_mem_exec_time()

avg_mem_speedup = {p:[] for p in policies}

for app in applications:
    for policy in policies:
        print(app, policy)

        mem_speedup = []

        for pim in pim_kernels:
            if pim == 'stream_triad':
                stream_add_index = pim_kernels.index('stream_add')
                mem_speedup.append(mem_speedup[stream_add_index])
                continue

            mem_time = get_exec_time(policy, pim, app, True, False)
            mem_speedup.append(base_mem_time[app] / mem_time)

        avg_mem_speedup[policy].append(gmean(mem_speedup))

for policy in policies:
    avg_mem_speedup[policy].append(gmean(avg_mem_speedup[policy]))

add_plot_all_pim(avg_mem_speedup, 'GPU Speedup', 'speedup_mem_rodinia')
