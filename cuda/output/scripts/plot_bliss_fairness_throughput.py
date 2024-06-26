#! /u/sgupta45/conda/bin/python3
from common import *

bliss_policies = [
        'bliss/interval_10000_threshold_4',
        'bliss/interval_10000_threshold_8',
        'bliss/interval_10000_threshold_16',
        'bliss/interval_10000_threshold_32'
        ]

colormap = matplotlib.cm.get_cmap("tab20c").colors
colors = {
        'bliss/interval_10000_threshold_4': colormap[3],
        'bliss/interval_10000_threshold_8': colormap[2],
        'bliss/interval_10000_threshold_16': colormap[1],
        'bliss/interval_10000_threshold_32': colormap[0]
        }

def gen_plot_single_pim(pim, yvalues, ylim, ylabel, filename):
    def add_bar(offset, policy):
        plabel = policy.split('_')[3]
        plt.bar([i+offset for i in x], yvalues[policy], edgecolor='k',
                width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(bliss_policies)
    if len(bliss_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(bliss_policies) / 2) - 1))
    else:
        offset = -width * ((len(bliss_policies) - 1) / 2)

    for policy in bliss_policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, [app_labels[app] for app in applications] + ['GMean'],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, ylim])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(bliss_policies), mode='expand', borderaxespad=0,
            fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_bliss_' + filename + '.pdf',
            bbox_inches='tight')

def gen_plot_all_pim(yvalues, ylabel, ylim, filename):
    def add_bar(offset, policy):
        plabel = policy.split('_')[3]
        plt.bar([i+offset for i in x], yvalues[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(pim_kernels) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(bliss_policies)
    if len(bliss_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(bliss_policies) / 2) - 1))
    else:
        offset = -width * ((len(bliss_policies) - 1) / 2)

    for policy in bliss_policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, [pim_labels[pim] for pim in pim_kernels] + ['GMean'],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, ylim])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(bliss_policies), mode='expand', borderaxespad=0,
            fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_bliss_' + filename + '.pdf',
            bbox_inches='tight')

# Load baseline execution times
base_mem_time = get_base_mem_exec_time()
base_pim_time = get_base_pim_exec_time()

avg_fairness_index = {p:[] for p in bliss_policies}
avg_throughput = {p:[] for p in bliss_policies}

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in bliss_policies:
            avg_fairness_index[policy].append(
                    avg_fairness_index[policy][stream_add_index])
            avg_throughput[policy].append(
                    avg_throughput[policy][stream_add_index])
        continue

    mem_speedup = {p:[] for p in bliss_policies}
    pim_speedup = {p:[] for p in bliss_policies}

    fairness_index = {p:[] for p in bliss_policies}
    throughput = {p:[] for p in bliss_policies}

    for policy in bliss_policies:
        print(pim, policy)

        for app in applications:
            mem_time, pim_time = get_exec_time(policy, pim, app, True, True)

            mem_speedup[policy].append(base_mem_time[app] / mem_time)
            pim_speedup[policy].append(base_pim_time[pim] / pim_time)

            fairness_index[policy].append(min(
                mem_speedup[policy][-1] / pim_speedup[policy][-1],
                pim_speedup[policy][-1] / mem_speedup[policy][-1]))
            throughput[policy].append(mem_speedup[policy][-1] + \
                    pim_speedup[policy][-1])

        mem_speedup[policy].append(gmean(mem_speedup[policy]))
        pim_speedup[policy].append(gmean(pim_speedup[policy]))

        avg = gmean(fairness_index[policy])
        fairness_index[policy].append(avg)
        avg_fairness_index[policy].append(avg)

        avg = gmean(throughput[policy])
        throughput[policy].append(avg)
        avg_throughput[policy].append(avg)

    gen_plot_single_pim(pim, mem_speedup, 1, 'GPU Speedup', 'mem_speedup')
    gen_plot_single_pim(pim, pim_speedup, 1, 'PIM Speedup', 'pim_speedup')
    gen_plot_single_pim(pim, fairness_index, 1, 'Fairness Index',
            'fairness_index')
    gen_plot_single_pim(pim, throughput, 2, 'Throughput', 'throughput')

for policy in bliss_policies:
    avg_fairness_index[policy].append(gmean(avg_fairness_index[policy]))
    avg_throughput[policy].append(gmean(avg_throughput[policy]))

gen_plot_all_pim(avg_fairness_index, 'Fairness Index', 1, 'fairness_index')
gen_plot_all_pim(avg_throughput, 'Throughput', 2, 'throughput')
