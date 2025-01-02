#! /u/sgupta45/conda/bin/python3
from common import *
from functools import partial

def gen_plot_single_pim(pim):
    def add_bar(yval, bottom, label, color):
        plt.bar(x, yval, bottom=bottom, edgecolor='k', width=0.8, label=label,
                fc=color)

    # plot parameters
    x = list(np.arange(len(applications) + 1))

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    bottom = [0 for i in x]
    add_bar(none_time, bottom, 'None', 'k')

    for i in x: bottom[i] += none_time[i]
    add_bar(mem_time, bottom, 'MEM only', colormap[2])

    for i in x: bottom[i] += mem_time[i]
    add_bar(pim_time, bottom, 'PIM only', colormap[8])

    for i in x: bottom[i] += pim_time[i]
    add_bar(both_time, bottom, 'Both', colormap[10])

    plt.xticks(x, applications + ['AMean'], fontsize=30, rotation='vertical')
    plt.ylabel('% Time Blacklisted', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 100])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(20))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_bliss_breakdown.pdf',
            bbox_inches='tight')

def gen_plot_all_pim():
    def add_bar(yval, bottom, label, color):
        plt.bar(x, yval, bottom=bottom, edgecolor='k', width=0.8, label=label,
                fc=color)

    # plot parameters
    x = list(np.arange(len(pim_kernels) + 1))

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    bottom = [0 for i in x]
    add_bar(avg_none_time, bottom, 'None', 'k')

    for i in x: bottom[i] += avg_none_time[i]
    add_bar(avg_mem_time, bottom, 'MEM only', colormap[2])

    for i in x: bottom[i] += avg_mem_time[i]
    add_bar(avg_pim_time, bottom, 'PIM only', colormap[8])

    for i in x: bottom[i] += avg_pim_time[i]
    add_bar(avg_both_time, bottom, 'Both', colormap[10])

    plt.xticks(x, [pim_labels[pim] for pim in pim_kernels] + ['AMean'],
            fontsize=30, rotation='vertical')
    plt.ylabel('% Time Blacklisted', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 100])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(20))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_bliss_breakdown.pdf', bbox_inches='tight')

def gen_plot_all_pim_average_only():
    def add_bar(yval, bottom, label, color):
        plt.bar(x, yval, bottom=bottom, edgecolor='k', width=0.5, label=label,
                fc=color)

    # plot parameters
    x = [0]

    # add the bars
    plt.clf()
    plt.figure(figsize=(2, 4), dpi=600)
    plt.rc('axes', axisbelow=True)

    bottom = [0]
    add_bar([avg_none_time[-1]], bottom, 'None', 'k')

    bottom[0] += avg_none_time[-1]
    add_bar([avg_mem_time[-1]], bottom, 'MEM', colormap[2])

    bottom[0] += avg_mem_time[-1]
    add_bar([avg_pim_time[-1]], bottom, 'PIM', colormap[8])

    bottom[0] += avg_pim_time[-1]
    add_bar([avg_both_time[-1]], bottom, 'Both', colormap[10])

    plt.xticks(x, ['AMean'], fontsize=30)
    plt.ylabel('% Time Blacklisted', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 100])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(20))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=1, mode='expand', borderaxespad=0, fontsize=18)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_bliss_breakdown_average_only.pdf',
            bbox_inches='tight')

avg_none_time = []
avg_mem_time = []
avg_pim_time = []
avg_both_time = []

for pim in pim_kernels:
    none_time = []
    mem_time = []
    pim_time = []
    both_time = []

    for app in applications:
        print(pim, app)

        total_cycles = [0 for c in range(num_channels)]
        none_time.append([0 for c in range(num_channels)])
        mem_time.append([0 for c in range(num_channels)])
        pim_time.append([0 for c in range(num_channels)])
        both_time.append([0 for c in range(num_channels)])

        channel = -1

        for line in open('../bliss_vc_2/interval_10000_threshold_4/' + app + \
                '_' + pim):
            if 'Memory Partition' in line:
                tokens = line.split()
                assert(len(tokens) == 3)
                channel = int(tokens[2][:-1])
            elif 'Total cycles =' in line:
                tokens = line.split()
                assert(len(tokens) == 4)
                total_cycles[channel] = int(tokens[3][:-2]) / 100
            elif 'Cycles none blacklisted =' in line:
                tokens = line.split()
                assert(len(tokens) == 5)
                none_time[-1][channel] = int(tokens[4][:-2]) / \
                        total_cycles[channel]
            elif 'Cycles MEM blacklisted =' in line:
                tokens = line.split()
                assert(len(tokens) == 5)
                mem_time[-1][channel] = int(tokens[4][:-2]) / \
                        total_cycles[channel]
            elif 'Cycles PIM blacklisted =' in line:
                tokens = line.split()
                assert(len(tokens) == 5)
                pim_time[-1][channel] = int(tokens[4][:-2]) / \
                        total_cycles[channel]
            elif 'Cycles both blacklisted =' in line:
                tokens = line.split()
                assert(len(tokens) == 5)
                both_time[-1][channel] = int(tokens[4][:-2]) / \
                        total_cycles[channel]

        none_time[-1] = amean(none_time[-1])
        mem_time[-1] = amean(mem_time[-1])
        pim_time[-1] = amean(pim_time[-1])
        both_time[-1] = amean(both_time[-1])

    none_time.append(amean(none_time))
    mem_time.append(amean(mem_time))
    pim_time.append(amean(pim_time))
    both_time.append(amean(both_time))

    avg_none_time.append(none_time[-1])
    avg_mem_time.append(mem_time[-1])
    avg_pim_time.append(pim_time[-1])
    avg_both_time.append(both_time[-1])

    gen_plot_single_pim(pim)

avg_none_time.append(amean(avg_none_time))
avg_mem_time.append(amean(avg_mem_time))
avg_pim_time.append(amean(avg_pim_time))
avg_both_time.append(amean(avg_both_time))

gen_plot_all_pim()
gen_plot_all_pim_average_only()
