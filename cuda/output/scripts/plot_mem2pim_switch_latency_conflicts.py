#! /u/sgupta45/conda/bin/python3
from common import *

def add_single_pim_plot(pim, stat, ylabel, filename):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], stat[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

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

    plt.xticks(x, [app_labels[app] for app in applications] + ['AMean'],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_' + filename + '.pdf',
            bbox_inches='tight')

def add_all_pim_plot(stat, ylabel, filename):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], stat[policy],
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

    plt.xticks(x, [pim_labels[pim] for pim in pim_kernels] + ['AMean'],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_' + filename + '.pdf',
            bbox_inches='tight')

avg_switch_latency = {p:[] for p in policies}
avg_switch_conflicts = {p:[] for p in policies}

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in policies:
            avg_switch_latency[policy].append(
                    avg_switch_latency[policy][stream_add_index])
            avg_switch_conflicts[policy].append(
                    avg_switch_conflicts[policy][stream_add_index])
        continue

    switch_latency = {p:[] for p in policies}
    switch_conflicts = {p:[] for p in policies}

    for policy in policies:
        print(pim, policy)

        for app in applications:
            switch_latency[policy].append([0 for c in range(num_channels)])
            switch_conflicts[policy].append([0 for c in range(num_channels)])

            channel = -1
            num_switches = -1

            for line in open('../' + policy + '/' + app + '_' + pim):
                if 'Memory Partition' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    channel = int(tokens[2][:-1])
                elif 'nonpim2pimswitches' in line and policy != 'pim_first':
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_switches = int(tokens[2])
                elif 'pim2nonpimswitches' in line and policy == 'pim_first':
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_switches = int(tokens[2])
                elif 'nonpim2pimswitchlatency' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    if num_switches == 0: continue
                    switch_latency[policy][-1][channel] = float(tokens[2]) / \
                            num_switches
                elif 'nonpim2pimswitchconflicts' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    if num_switches == 0: continue
                    switch_conflicts[policy][-1][channel] = float(tokens[2]) /\
                            num_switches

            switch_latency[policy][-1] = amean(switch_latency[policy][-1])
            switch_conflicts[policy][-1] = amean(switch_conflicts[policy][-1])

    ##################
    # Normalize values
    ##################
    for policy in policies:
        avg = amean(switch_conflicts[policy])
        switch_conflicts[policy].append(avg)
        avg_switch_conflicts[policy].append(avg)

        avg = amean(switch_latency[policy])
        switch_latency[policy].append(avg)
        avg_switch_latency[policy].append(avg)

    add_single_pim_plot(pim, switch_latency, "MEM Drain Latency / Switch",
            "switch_latency")
    add_single_pim_plot(pim, switch_conflicts, "MEM Conflicts / Switch",
            "switch_conflicts")

for policy in policies:
    avg_switch_latency[policy].append(amean(avg_switch_latency[policy]))
    avg_switch_conflicts[policy].append(amean(avg_switch_conflicts[policy]))

add_all_pim_plot(avg_switch_latency, "MEM Drain Latency / Switch",
        "switch_latency")
add_all_pim_plot(avg_switch_conflicts, "MEM Conflicts / Switch",
        "switch_conflicts")
