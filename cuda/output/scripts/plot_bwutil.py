#! /u/sgupta45/conda/bin/python3
from common import *

def add_single_pim_plot():
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], bwutil[policy],
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

    plt.xticks(x, [app_labels[app] for app in applications] + ['GMean'],
            fontsize=30)
    plt.ylabel('DRAM B/W Utilization\n(normalized to PIM only)', fontsize=30)
    plt.yticks(fontsize=30)

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_bwutil.pdf',
            bbox_inches='tight')

def add_all_pim_plot():
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], avg_bwutil[policy],
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
    plt.ylabel('DRAM B/W Utilization\n(normalized to PIM only)', fontsize=30)
    plt.yticks(fontsize=30)

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_bwutil.pdf',
            bbox_inches='tight')

base_pim_bwutil = {pim:[] for pim in pim_kernels}

for pim in pim_kernels:
    base_pim_bwutil[pim] = [0 for c in range(num_channels)]

    channel = -1

    filename = base_pim_files[pim] if pim in base_pim_files else pim + '_256'

    for line in open('/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_' +
            str(pim_rf_size) + '/' + filename + '_sm_' + str(pim_num_sm)):
        if 'Memory Partition' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            channel = int(tokens[2][:-1])
        elif 'bwutil' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_pim_bwutil[pim][channel] = float(tokens[2])

    base_pim_bwutil[pim] = gmean(base_pim_bwutil[pim])

avg_bwutil = {p:[] for p in policies}

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in policies:
            avg_bwutil[policy].append(
                    avg_bwutil[policy][stream_add_index])
        continue

    bwutil = {p:[] for p in policies}

    for policy in policies:
        print(pim, policy)

        for app in applications:
            bwutil[policy].append([0 for c in range(num_channels)])

            channel = -1

            for line in open('../' + policy + '/' + app + '_' + pim):
                if 'Memory Partition' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    channel = int(tokens[2][:-1])
                elif 'bwutil' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    bwutil[policy][-1][channel] = float(tokens[2])

            assert(0 not in bwutil[policy][-1])
            bwutil[policy][-1] = gmean(bwutil[policy][-1]) / \
                    base_pim_bwutil[pim]

    for policy in policies:
        avg = gmean(bwutil[policy])
        bwutil[policy].append(avg)
        avg_bwutil[policy].append(avg)

    add_single_pim_plot()

for policy in policies:
    avg_bwutil[policy].append(amean(avg_bwutil[policy]))

add_all_pim_plot()
