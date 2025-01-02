#! /u/sgupta45/conda/bin/python3
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def gen_plot():
    def add_bar(offset, yval, label, color):
        plt.bar([i+offset for i in x], yval, edgecolor='k', width=width,
                label=label, fc=color)

    # plot parameters
    x = np.arange(len(policies))

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.4

    add_bar(0, num_mode_switches, '', colormap[0])

    plt.xticks(x, [labels[policy] for policy in policies], fontsize=25)
    plt.yticks(fontsize=30)
    plt.ylabel('Mode Switches', fontsize=30)

    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)
    plt.axhline(y=1, color='r', linestyle='-', linewidth=3)

    # save the image
    plt.savefig('../plots/llm_num_mode_switches.pdf', bbox_inches='tight')

num_mode_switches = []

for policy in policies:
    num_mode_switches.append([0 for c in range(num_channels)])

    channel = -1

    for line in open('../' + policy + '/llm'):
        if 'Memory Partition' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            channel = int(tokens[2][:-1])
        elif 'pim2nonpimswitches' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            num_mode_switches[-1][channel] = int(tokens[2])
        elif 'nonpim2pimswitches' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            num_mode_switches[-1][channel] += int(tokens[2])

    num_mode_switches[-1] = sum(num_mode_switches[-1]) / num_channels

gen_plot()
