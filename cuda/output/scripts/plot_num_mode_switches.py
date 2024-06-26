#! /u/sgupta45/conda/bin/python3
from common import *

ymax = 1.07
if 'fifo' not in policies: policies = ['fifo'] + policies

def add_plot_single_pim(pim):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], num_mode_switches[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

        for i, val in enumerate(num_mode_switches[policy]):
            if val > ymax:
                plt.text(i+offset+width, 1.02, "{:.2f}".format(round(val, 2)),
                        fontsize=20)

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
    plt.ylabel('Mode switches (normalized)', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, ymax])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_num_mode_switches.pdf',
            bbox_inches='tight')

def add_plot_all_pim():
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], avg_num_mode_switches[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

        for i, val in enumerate(avg_num_mode_switches[policy]):
            if val > ymax:
                plt.text(i+offset+width, 1.02, "{:.2f}".format(round(val, 2)),
                        fontsize=20)

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
    plt.ylabel('Mode switches (normalized)', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, ymax])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_num_mode_switches.pdf',
            bbox_inches='tight')

#########################
# Load number of switches
#########################

avg_num_mode_switches = {p:[] for p in policies}

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in policies:
            avg_num_mode_switches[policy].append(
                    avg_num_mode_switches[policy][stream_add_index])
        continue

    num_mode_switches = {p:[] for p in policies}

    for policy in policies:
        print(pim, policy)

        for app in applications:
            num_mode_switches[policy].append([0 for c in range(num_channels)])

            channel = -1
            num_mem_iterations = 0
            num_pim_iterations = 0

            for line in open('../' + policy + '/' + app + '_' + pim):
                if 'Memory Partition' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    channel = int(tokens[2][:-1])
                elif 'pim2nonpimswitches' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_mode_switches[policy][-1][channel] = int(tokens[2])
                elif 'nonpim2pimswitches' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_mode_switches[policy][-1][channel] += int(tokens[2])
                elif '<<< MEM FINISHED >>>' in line:
                    num_mem_iterations += 1
                elif '<<< PIM FINISHED >>>' in line:
                    num_pim_iterations += 1

            num_mode_switches[policy][-1] = \
                    sum(num_mode_switches[policy][-1]) / \
                    max(num_mem_iterations, num_pim_iterations)

    ##################
    # Normalize values
    ##################
    norm_values = num_mode_switches['fifo'][:]
    for policy in policies:
        for i in range(len(applications)):
            num_mode_switches[policy][i] /= norm_values[i]

        avg = gmean(num_mode_switches[policy])
        num_mode_switches[policy].append(avg)
        avg_num_mode_switches[policy].append(avg)

    add_plot_single_pim(pim)

for policy in policies:
    avg_num_mode_switches[policy].append(gmean(avg_num_mode_switches[policy]))

add_plot_all_pim()
