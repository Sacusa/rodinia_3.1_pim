#! /u/sgupta45/conda/bin/python3
from common import *

sweep_parameter = 'cap'  # cap, slowdown

colormap = matplotlib.cm.get_cmap("tab20c").colors

if sweep_parameter == 'cap':
    pim_frfcfs_util_policies = [
            'pim_frfcfs_util/cap_0',
            'pim_frfcfs_util/cap_8_slowdown_4',
            'pim_frfcfs_util/cap_16_slowdown_4',
            'pim_frfcfs_util/cap_32_slowdown_4',
            'pim_frfcfs_util/cap_64_slowdown_4',
            'pim_frfcfs_util/cap_128_slowdown_4']
            #'pim_frfcfs_util/cap_256_slowdown_4']
    colors = {
            'pim_frfcfs_util/cap_0': 'k',
            'pim_frfcfs_util/cap_8_slowdown_4': colormap[16],
            'pim_frfcfs_util/cap_16_slowdown_4': colormap[0],
            'pim_frfcfs_util/cap_32_slowdown_4': colormap[1],
            'pim_frfcfs_util/cap_64_slowdown_4': colormap[2],
            'pim_frfcfs_util/cap_128_slowdown_4': colormap[3]}
            #'pim_frfcfs_util/cap_256_slowdown_4': colormap[14]}
elif 'slowdown':
    pim_frfcfs_util_policies = [
            'pim_frfcfs_util/cap_8_slowdown_0.33',
            'pim_frfcfs_util/cap_8_slowdown_1',
            'pim_frfcfs_util/cap_8_slowdown_4'
            ]
    colors = {
            'pim_frfcfs_util/cap_8_slowdown_0.33': colormap[0],
            'pim_frfcfs_util/cap_8_slowdown_1': colormap[1],
            'pim_frfcfs_util/cap_8_slowdown_4': colormap[2]
            }
else:
    print('ERROR: Unknown sweep parameter: ' + sweep_parameter)
    exit()

def gen_plot_single_pim(pim, yvalues, ylim, ylabel, filename):
    def add_bar(offset, policy):
        if sweep_parameter == 'cap': plabel = policy.split('_')[3]
        else:                        plabel = policy.split('_')[5]
        plt.bar([i+offset for i in x], yvalues[policy], edgecolor='k',
                width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(pim_frfcfs_util_policies)
    if len(pim_frfcfs_util_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(pim_frfcfs_util_policies) / 2) - 1))
    else:
        offset = -width * ((len(pim_frfcfs_util_policies) - 1) / 2)

    for policy in pim_frfcfs_util_policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, [app_labels[app] for app in applications] + ['GMean'],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, ylim])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(pim_frfcfs_util_policies) + 1, mode='expand',
            borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_pim_frfcfs_util_' + filename + '.pdf',
            bbox_inches='tight')

def gen_plot_single_pim_throughput_fairness():
    def add_bar(offset, policy):
        if sweep_parameter == 'cap': plabel = policy.split('_')[3]
        else:                        plabel = policy.split('_')[5]
        ax1.bar([i+offset for i in x], fairness_index[policy], edgecolor='k',
                width=width, label=plabel, fc=colors[policy])

    def add_line(index):
        if len(pim_frfcfs_util_policies) % 2 == 0:
            offset = -width * (0.5 + ((len(pim_frfcfs_util_policies) / 2) - 1))
        else:
            offset = -width * ((len(pim_frfcfs_util_policies) - 1) / 2)

        x_vals = []
        y_vals = []
        for policy in pim_frfcfs_util_policies:
            x_vals.append(index + offset)
            y_vals.append(throughput[policy][index])
            offset += width

        label = ''
        if index == 0: label = 'Throughput'

        ax2.plot(x_vals, y_vals, 'ko-', markersize=10, linewidth=2,
                markeredgecolor='k', markeredgewidth=1, markerfacecolor='y',
                label=label)

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    fig, ax1 = plt.subplots(figsize=(24, 8), dpi=600)
    ax2 = ax1.twinx()
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(pim_frfcfs_util_policies)
    if len(pim_frfcfs_util_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(pim_frfcfs_util_policies) / 2) - 1))
    else:
        offset = -width * ((len(pim_frfcfs_util_policies) - 1) / 2)

    for policy in pim_frfcfs_util_policies:
        add_bar(offset, policy)
        offset += width

    for i in range(len(applications)+1): add_line(i)

    ax1.set_xticks(x)
    ax1.set_xticklabels([app_labels[app] for app in applications] + ['GMean'],
            size=30)
    ax1.set_ylabel('Fairness Index', size=30)
    ax1.yaxis.set_tick_params(labelsize=30)
    ax1.set_ylim([0, 1])
    ax1.yaxis.set_major_locator(plt.MultipleLocator(0.1))

    ax2.set_ylabel('Throughput', size=30)
    ax2.yaxis.set_tick_params(labelsize=30)
    ax2.set_ylim([0, 2])
    ax2.yaxis.set_major_locator(plt.MultipleLocator(0.2))

    ax1.grid(zorder=0, axis='y', color='silver', linestyle='-', linewidth=1)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(0, 1.02, 1, 0.2),
            loc="lower left", ncol=len(pim_frfcfs_util_policies) + 1,
            mode='expand', borderaxespad=0, fontsize=25)

    # save the image
    plt.savefig('../plots/' + pim + '_pim_frfcfs_util_throughput_fairness.pdf',
            bbox_inches='tight')

def gen_plot_all_pim(yvalues, ylabel, ylim, filename):
    def add_bar(offset, policy):
        if sweep_parameter == 'cap': plabel = policy.split('_')[3]
        else:                        plabel = policy.split('_')[5]
        plt.bar([i+offset for i in x], yvalues[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(pim_kernels) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(pim_frfcfs_util_policies)
    if len(pim_frfcfs_util_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(pim_frfcfs_util_policies) / 2) - 1))
    else:
        offset = -width * ((len(pim_frfcfs_util_policies) - 1) / 2)

    for policy in pim_frfcfs_util_policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, [pim_labels[pim] for pim in pim_kernels] + ['GMean'],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, ylim])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(pim_frfcfs_util_policies) + 1, mode='expand',
            borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_pim_frfcfs_util_' + filename + '.pdf',
            bbox_inches='tight')

def gen_plot_all_pim_throughput_fairness():
    def add_bar(offset, policy):
        if sweep_parameter == 'cap': plabel = policy.split('_')[3]
        else:                        plabel = policy.split('_')[5]
        ax1.bar([i+offset for i in x], avg_fairness_index[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

    def add_line(index):
        if len(pim_frfcfs_util_policies) % 2 == 0:
            offset = -width * (0.5 + ((len(pim_frfcfs_util_policies) / 2) - 1))
        else:
            offset = -width * ((len(pim_frfcfs_util_policies) - 1) / 2)

        x_vals = []
        y_vals = []
        for policy in pim_frfcfs_util_policies:
            x_vals.append(index + offset)
            y_vals.append(avg_throughput[policy][index])
            offset += width

        label = ''
        if index == 0: label = 'Throughput'

        ax2.plot(x_vals, y_vals, 'ko-', markersize=10, linewidth=2,
                markeredgecolor='k', markeredgewidth=1, markerfacecolor='y',
                label=label)

    # plot parameters
    x = np.arange(len(pim_kernels) + 1)

    # add the bars
    plt.clf()
    fig, ax1 = plt.subplots(figsize=(24, 8), dpi=600)
    ax2 = ax1.twinx()
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(pim_frfcfs_util_policies)
    if len(pim_frfcfs_util_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(pim_frfcfs_util_policies) / 2) - 1))
    else:
        offset = -width * ((len(pim_frfcfs_util_policies) - 1) / 2)

    for policy in pim_frfcfs_util_policies:
        add_bar(offset, policy)
        offset += width

    for i in range(len(pim_kernels)+1): add_line(i)

    ax1.set_xticks(x)
    ax1.set_xticklabels([pim_labels[pim] for pim in pim_kernels] + ['GMean'],
            size=30)
    ax1.set_ylabel('Fairness Index', size=30)
    ax1.yaxis.set_tick_params(labelsize=30)
    ax1.set_ylim([0, 1])
    ax1.yaxis.set_major_locator(plt.MultipleLocator(0.1))

    ax2.set_ylabel('Throughput', size=30)
    ax2.yaxis.set_tick_params(labelsize=30)
    ax2.set_ylim([0, 2])
    ax2.yaxis.set_major_locator(plt.MultipleLocator(0.2))

    ax1.grid(zorder=0, axis='y', color='silver', linestyle='-', linewidth=1)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1+h2, l1+l2, bbox_to_anchor=(0, 1.02, 1, 0.2),
            loc="lower left", ncol=len(pim_frfcfs_util_policies) + 1,
            mode='expand', borderaxespad=0, fontsize=25)

    # save the image
    plt.savefig('../plots/all_pim_frfcfs_util_throughput_fairness.pdf',
            bbox_inches='tight')

# Load baseline execution times
base_mem_time = get_base_mem_exec_time()
base_pim_time = get_base_pim_exec_time()

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

    mem_speedup = {p:[] for p in pim_frfcfs_util_policies}
    pim_speedup = {p:[] for p in pim_frfcfs_util_policies}

    fairness_index = {p:[] for p in pim_frfcfs_util_policies}
    throughput = {p:[] for p in pim_frfcfs_util_policies}

    for policy in pim_frfcfs_util_policies:
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

    for policy in pim_frfcfs_util_policies:
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
    gen_plot_single_pim_throughput_fairness()

for policy in pim_frfcfs_util_policies:
    avg_fairness_index[policy].append(gmean(avg_fairness_index[policy]))
    avg_throughput[policy].append(gmean(avg_throughput[policy]))

gen_plot_all_pim(avg_fairness_index, 'Fairness Index', 1, 'fairness_index')
gen_plot_all_pim(avg_throughput, 'Throughput', 2, 'throughput')
gen_plot_all_pim_throughput_fairness()
