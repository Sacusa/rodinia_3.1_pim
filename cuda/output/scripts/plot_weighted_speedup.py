#! /u/sgupta45/conda/bin/python3
from common import *

def gen_plot_single_pim(pim):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], weighted_speedup[policy], edgecolor='k',
                width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
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
    plt.ylabel('Throughput', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 2])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_weighted_speedup.pdf',
            bbox_inches='tight')

def gen_plot_all_pim():
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], avg_weighted_speedup[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(pim_kernels) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(policies)
    if len(policies) % 2 == 0:
        offset = -width * (0.5 + ((len(policies) / 2) - 1))
    else:
        offset = -width * ((len(policies) - 1) / 2)

    for policy in policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, [pim_labels[pim] for pim in pim_kernels] + ['GMean'],
            fontsize=30)
    plt.ylabel('Throughput', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 2])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_weighted_speedup.pdf',
            bbox_inches='tight')

base_mem_time = get_base_mem_exec_time()
base_pim_time = get_base_pim_exec_time()

avg_weighted_speedup = {p:[] for p in policies}

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in policies:
            avg_weighted_speedup[policy].append(
                    avg_weighted_speedup[policy][stream_add_index])
        continue

    weighted_speedup = {p:[] for p in policies}

    for policy in policies:
        print(pim, policy)

        for app in applications:
            mem_time, pim_time = get_exec_time(policy, pim, app, True, True)

            mem_speedup = base_mem_time[app] / mem_time
            pim_speedup = base_pim_time[pim] / pim_time

            weighted_speedup[policy].append(mem_speedup + pim_speedup)

        avg = gmean(weighted_speedup[policy])
        weighted_speedup[policy].append(avg)
        avg_weighted_speedup[policy].append(avg)

    gen_plot_single_pim(pim)

for policy in policies:
    avg_weighted_speedup[policy].append(gmean(avg_weighted_speedup[policy]))

gen_plot_all_pim()
