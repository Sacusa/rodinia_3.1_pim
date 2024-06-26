#! /u/sgupta45/conda/bin/python3
from common import *
from functools import partial

def gen_plot_single_pim():
    def add_bar(yval, color, edgecolor, hatch):
        plt.bar([i+offset for i in x], yval, edgecolor=edgecolor, width=width,
                label=label, fc=color, hatch=hatch, bottom=bottom, zorder=1)
        plt.bar([i+offset for i in x], yval, edgecolor='k', width=width,
                fc='none', bottom=bottom, zorder=2)

    # plot parameters
    x = list(np.arange(len(applications) + 1))

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.4
    offset = -0.5 * width

    hatches = ['', '/']
    colors = [colormap[2], colormap[8], colormap[10]]
    edgecolors = [colormap[3], colormap[9], colormap[11]]

    for st_index, st in enumerate(switch_types):
        bottom = [0 for i in x]

        for sr_index, sr in enumerate(switch_reasons):
            label = ''
            if st_index == 0: label = sr

            add_bar(switches[st][sr], colors[sr_index], edgecolors[sr_index],
                    hatches[st_index])

            bottom = [bottom[i] + switches[st][sr][i] for i in x]

        offset += width

    plt.xticks(x, [app_labels[app] for app in applications] + ['AMean'],
            fontsize=25)
    plt.ylabel('Switch Type Frequency (%)', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 100])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_pim_frfcfs_util_breakdown.pdf',
            bbox_inches='tight')

def gen_plot_all_pim():
    def add_bar(yval, color, edgecolor, hatch):
        plt.bar([i+offset for i in x], yval, edgecolor=edgecolor, width=width,
                label=label, fc=color, hatch=hatch, bottom=bottom, zorder=1)
        plt.bar([i+offset for i in x], yval, edgecolor='k', width=width,
                fc='none', bottom=bottom, zorder=2)

    # plot parameters
    x = list(np.arange(len(pim_kernels) + 1))

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.4
    offset = -0.5 * width

    hatches = ['', '/']
    colors = [colormap[2], colormap[8], colormap[10]]
    edgecolors = [colormap[3], colormap[9], colormap[11]]

    for st_index, st in enumerate(switch_types):
        bottom = [0 for i in x]

        for sr_index, sr in enumerate(switch_reasons):
            label = ''
            if st_index == 0: label = sr

            add_bar(avg_switches[st][sr], colors[sr_index],
                    edgecolors[sr_index], hatches[st_index])

            bottom = [bottom[i] + avg_switches[st][sr][i] for i in x]

        offset += width

    plt.xticks(x, [pim_labels[pim] for pim in pim_kernels] + ['AMean'],
            fontsize=25)
    plt.ylabel('Switch Type Frequency (%)', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 100])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_pim_frfcfs_util_breakdown.pdf',
            bbox_inches='tight')

def gen_plot_all_pim_average_only():
    def add_bar(yval, color, edgecolor, hatch):
        plt.bar([i+offset for i in x], yval, edgecolor=edgecolor, width=width,
                label=label, fc=color, hatch=hatch, bottom=bottom, zorder=1)
        plt.bar([i+offset for i in x], yval, edgecolor='k', width=width,
                fc='none', bottom=bottom, zorder=2)

    # plot parameters
    x = [0]

    # add the bars
    plt.clf()
    plt.figure(figsize=(4, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.4
    offset = -0.5 * width

    hatches = ['', '/']
    colors = [colormap[2], colormap[8], colormap[10]]
    edgecolors = [colormap[3], colormap[9], colormap[11]]

    for st_index, st in enumerate(switch_types):
        bottom = [0]

        for sr_index, sr in enumerate(switch_reasons):
            label = ''
            if st_index == 0: label = sr

            add_bar([avg_switches[st][sr][-1]], colors[sr_index],
                    edgecolors[sr_index], hatches[st_index])

            bottom[0] += avg_switches[st][sr][-1]

        offset += width

    plt.xticks(x, ['AMean'], fontsize=25)
    plt.ylabel('Switch Type Frequency (%)', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 100])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=1, mode='expand', borderaxespad=0, fontsize=18)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_pim_frfcfs_util_breakdown_average_only.pdf',
            bbox_inches='tight')

switch_types = ['MEM2PIM', 'PIM2MEM']
switch_reasons = ['OutOfRequests', 'CapExceeded', 'OldestFirst']

avg_switches = {}

for st in switch_types:
    avg_switches[st] = {}
    for sr in switch_reasons:
        avg_switches[st][sr] = []

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        continue

    switches = {}
    for st in switch_types:
        switches[st] = {}
        for sr in switch_reasons:
            switches[st][sr] = []

    for app in applications:
        print(pim, app)

        for st in switch_types:
            for sr in switch_reasons:
                switches[st][sr].append([0 for c in range(num_channels)])

        channel = -1
        curr_switch_type = ''

        for line in open('../pim_frfcfs_util/cap_128_slowdown_4/' + app + \
                '_' + pim):
            if 'Memory Partition' in line:
                tokens = line.split()
                assert(len(tokens) == 3)
                channel = int(tokens[2][:-1])
            elif 'Switch Breakdown' in line:
                tokens = line.split()
                assert(len(tokens) == 3)
                curr_switch_type = tokens[0].strip()

            else:
                for sr in switch_reasons:
                    if sr in line:
                        tokens = line.split()
                        assert(len(tokens) == 2)
                        switches[curr_switch_type][sr][-1][channel] = \
                                int(tokens[1])

        for st in switch_types:
            num_switches = 0

            for sr in switch_reasons:
                switches[st][sr][-1] = amean(switches[st][sr][-1])
                num_switches += switches[st][sr][-1]

            for sr in switch_reasons:
                switches[st][sr][-1] /= (num_switches / 100)

    for st in switch_types:
        for sr in switch_reasons:
            avg = amean(switches[st][sr])
            switches[st][sr].append(avg)
            avg_switches[st][sr].append(avg)

    gen_plot_single_pim()

for st in switch_types:
    for sr in switch_reasons:
        avg_switches[st][sr].append(amean(avg_switches[st][sr]))

#gen_plot_all_pim()
gen_plot_all_pim_average_only()
