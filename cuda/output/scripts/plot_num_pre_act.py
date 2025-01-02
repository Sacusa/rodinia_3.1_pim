#! /u/sgupta45/conda/bin/python3
from common import *
import numpy as np

def add_plot(pim):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], num_pre_act[policy], edgecolor='k',
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

    plt.xticks(x, applications + ['GMean'], fontsize=30, rotation='vertical')
    plt.ylabel('PRE & ACT (normalized)', fontsize=30)
    plt.yticks(fontsize=30)
    #plt.ylim([0, 1])
    #plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", ncol=6,
            mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)
    #plt.axhline(y=1, color='r', linestyle='-', linewidth=2)

    # save the image
    plt.savefig('../plots/' + pim + '_num_pre_act.pdf', bbox_inches='tight')

#####################################
# Baseline number of PRE/ACT commands
#####################################

base_pre_act_mem = {}

for app in applications:
    channel = -1
    n_pre = [0 for c in range(num_channels)]
    n_act = [0 for c in range(num_channels)]

    for line in open('../pim_frfcfs/single_apps/' + app + '_nop'):
        if 'Memory Partition' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            channel = int(tokens[2][:-1])
        elif 'n_pre =' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            n_pre[channel] = int(tokens[2])
        elif 'n_act =' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            n_act[channel] = int(tokens[2])

    base_pre_act_mem[app] = sum(n_pre) + sum(n_act)

base_pre_act_pim = {}

for pim in pim_kernels:
    channel = -1
    n_pre = [0 for c in range(num_channels)]
    n_act = [0 for c in range(num_channels)]

    for line in open('/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_' +
            str(pim_rf_size) + '/' + pim + '_256_sm_' + str(pim_num_sm)):
        if 'Memory Partition' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            channel = int(tokens[2][:-1])
        elif 'n_pre =' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            n_pre[channel] = int(tokens[2])
        elif 'n_act =' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            n_act[channel] = int(tokens[2])

    base_pre_act_pim[pim] = sum(n_pre) + sum(n_act)

########################
# Load number of PRE/ACT
########################

for pim in pim_kernels:
    num_pre_act = {p:[] for p in policies}

    for policy in policies:
        for app in applications:
            num_pre_act[policy].append([0 for c in range(num_channels)])

            channel = -1
            num_mem_iterations = 0
            num_pim_iterations = 0

            for line in open('../' + policy + '/' + app + '_' + pim):
                if 'Memory Partition' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    channel = int(tokens[2][:-1])
                elif 'n_act =' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_pre_act[policy][-1][channel] = int(tokens[2])
                elif 'n_pre =' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_pre_act[policy][-1][channel] += int(tokens[2])
                elif '<<< MEM FINISHED >>>' in line:
                    num_mem_iterations += 1
                elif '<<< PIM FINISHED >>>' in line:
                    num_pim_iterations += 1

            num_pre_act[policy][-1] = sum(num_pre_act[policy][-1]) / \
                    ((base_pre_act_mem[app] * num_mem_iterations) + \
                     (base_pre_act_pim[pim] * num_pim_iterations))
            #num_pre_act[policy][-1] = \
            #        ((base_pre_act_mem[app] * num_mem_iterations) + \
            #         (base_pre_act_pim[pim] * num_pim_iterations)) / \
            #        sum(num_pre_act[policy][-1])

    for policy in policies:
        num_pre_act[policy].append(gmean(num_pre_act[policy]))

    add_plot(pim)
