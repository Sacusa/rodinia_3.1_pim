#! /u/sgupta45/conda/bin/python3
from common import *

rr_policies = ['i3/batch_1_slowdown_2', 'i3/batch_2_slowdown_2',
        'i3/batch_4_slowdown_2', 'i3/batch_8_slowdown_2',
        'i3/batch_16_slowdown_2']

colormap = matplotlib.cm.get_cmap("tab20c").colors
colors = {
        'i3/batch_1_slowdown_2': colormap[3],
        'i3/batch_2_slowdown_2': colormap[2],
        'i3/batch_4_slowdown_2': colormap[1],
        'i3/batch_8_slowdown_2': colormap[0],
        'i3/batch_16_slowdown_2': colormap[16]
        }

def gen_plot_single_pim(pim, yvalues, ylim, ylabel, filename):
    def add_bar(offset, policy):
        plabel = policy.split('_')[1]
        plt.bar([i+offset for i in x], yvalues[policy], edgecolor='k',
                width=width, label=plabel, fc=colors[policy])

    def add_line(index):
        if len(rr_policies) % 2 == 0:
            offset = -width * (0.5 + ((len(rr_policies) / 2) - 1))
        else:
            offset = -width * ((len(rr_policies) - 1) / 2)

        x_vals = []
        y_vals = []
        for policy in rr_policies:
            x_vals.append(index + offset)
            y_vals.append(throughput[policy][index] / 2)
            offset += width

        label = ''
        if index == 0: label = 'Throughput'

        plt.plot(x_vals, y_vals, 'ko-', markersize=10, linewidth=2,
                markeredgecolor='k', markeredgewidth=1, markerfacecolor='y',
                label=label)

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(rr_policies)
    if len(rr_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(rr_policies) / 2) - 1))
    else:
        offset = -width * ((len(rr_policies) - 1) / 2)

    for policy in rr_policies:
        add_bar(offset, policy)
        offset += width

    if 'Fairness' in ylabel:
        for i in range(len(applications)+1): add_line(i)

    plt.xticks(x, [app_labels[app] for app in applications] + ['GMean'],
            fontsize=25)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, ylim])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", ncol=6,
            mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_rr_' + filename + '.pdf',
            bbox_inches='tight')

def gen_plot_single_pim_throughput_fairness():
    def add_bar(offset, policy):
        plabel = policy.split('_')[1]
        ax1.bar([i+offset for i in x], fairness_index[policy], edgecolor='k',
                width=width, label=plabel, fc=colors[policy])

    def add_line(index):
        if len(rr_policies) % 2 == 0:
            offset = -width * (0.5 + ((len(rr_policies) / 2) - 1))
        else:
            offset = -width * ((len(rr_policies) - 1) / 2)

        x_vals = []
        y_vals = []
        for policy in rr_policies:
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

    width = 0.8 / len(rr_policies)
    if len(rr_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(rr_policies) / 2) - 1))
    else:
        offset = -width * ((len(rr_policies) - 1) / 2)

    for policy in rr_policies:
        add_bar(offset, policy)
        offset += width

    for i in range(len(applications)+1): add_line(i)

    ax1.set_xticks(x)
    ax1.set_xticklabels([app_labels[app] for app in applications] + ['GMean'],
            size=25)
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
            loc="lower left", ncol=6, mode='expand', borderaxespad=0,
            fontsize=25)

    # save the image
    plt.savefig('../plots/' + pim + '_rr_throughput_fairness.pdf',
            bbox_inches='tight')

def gen_plot_all_pim(yvalues, ylabel, ylim, filename):
    def add_bar(offset, policy):
        plabel = policy.split('_')[1]
        plt.bar([i+offset for i in x], yvalues[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(pim_kernels) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(rr_policies)
    if len(rr_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(rr_policies) / 2) - 1))
    else:
        offset = -width * ((len(rr_policies) - 1) / 2)

    for policy in rr_policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, [pim_labels[pim] for pim in pim_kernels] + ['GMean'],
            fontsize=25)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, ylim])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", ncol=6,
            mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_rr_' + filename + '.pdf',
            bbox_inches='tight')

def gen_plot_all_pim_throughput_fairness():
    def add_bar(offset, policy):
        plabel = policy.split('_')[1]
        ax1.bar([i+offset for i in x], avg_fairness_index[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

    def add_line(index):
        if len(rr_policies) % 2 == 0:
            offset = -width * (0.5 + ((len(rr_policies) / 2) - 1))
        else:
            offset = -width * ((len(rr_policies) - 1) / 2)

        x_vals = []
        y_vals = []
        for policy in rr_policies:
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

    width = 0.8 / len(rr_policies)
    if len(rr_policies) % 2 == 0:
        offset = -width * (0.5 + ((len(rr_policies) / 2) - 1))
    else:
        offset = -width * ((len(rr_policies) - 1) / 2)

    for policy in rr_policies:
        add_bar(offset, policy)
        offset += width

    for i in range(len(pim_kernels)+1): add_line(i)

    ax1.set_xticks(x)
    ax1.set_xticklabels([pim_labels[pim] for pim in pim_kernels] + ['GMean'],
            size=25)
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
            loc="lower left", ncol=6, mode='expand', borderaxespad=0,
            fontsize=25)

    # save the image
    plt.savefig('../plots/all_rr_throughput_fairness.pdf',
            bbox_inches='tight')

base_mem_time = get_base_mem_exec_time()
base_pim_time = get_base_pim_exec_time()

avg_fairness_index = {p:[] for p in rr_policies}
avg_throughput = {p:[] for p in rr_policies}

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in rr_policies:
            avg_fairness_index[policy].append(
                    avg_fairness_index[policy][stream_add_index])
            avg_throughput[policy].append(
                    avg_throughput[policy][stream_add_index])
        continue

    mem_speedup = {p:[] for p in rr_policies}
    pim_speedup = {p:[] for p in rr_policies}

    fairness_index = {p:[] for p in rr_policies}
    throughput = {p:[] for p in rr_policies}

    for policy in rr_policies:
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
    gen_plot_single_pim_throughput_fairness()

for policy in rr_policies:
    avg_fairness_index[policy].append(gmean(avg_fairness_index[policy]))
    avg_throughput[policy].append(gmean(avg_throughput[policy]))

gen_plot_all_pim_throughput_fairness()
