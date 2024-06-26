#! /u/sgupta45/conda/bin/python3
from common import *
from functools import partial

def gen_plot_single_pim(pim):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], dram_latency[policy],
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
    plt.ylabel('DRAM Access Latency\n(normalized)', fontsize=30)
    plt.yticks(fontsize=30)
    plt.yscale('log')

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_avg_dram_latency.pdf',
            bbox_inches='tight')

def gen_plot_all_pim():
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], avg_dram_latency[policy],
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
    plt.ylabel('DRAM Access Latency\n(normalized)', fontsize=30)
    plt.yticks(fontsize=30)

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_avg_dram_latency.pdf', bbox_inches='tight')

base_mem_dram_latency = {app:0 for app in applications}

for app in applications:
    for line in open('../frfcfs/' + app + '_nop'):
        if 'avg_mrq_latency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_mem_dram_latency[app] = float(tokens[2])
        elif 'avg_dram_service_latency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_mem_dram_latency[app] += float(tokens[2])

base_pim_dram_latency = {pim:0 for pim in pim_kernels}

for pim in pim_kernels:
    filename = base_pim_files[pim] if pim in base_pim_files else pim + '_256'

    for line in open('/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_' +
            str(pim_rf_size) + '/' + filename + '_sm_' + str(pim_num_sm)):
        if 'avg_mrq_latency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_pim_dram_latency[pim] = float(tokens[2])
        elif 'avg_dram_service_latency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_pim_dram_latency[pim] += float(tokens[2])

avg_dram_latency = {p:[] for p in policies}

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in policies:
            avg_dram_latency[policy].append(
                    avg_dram_latency[policy][stream_add_index])
        continue

    dram_latency = {p:[] for p in policies}

    for policy in policies:
        print(pim, policy)

        for app in applications:
            dram_latency[policy].append(0)

            channel = -1
            num_mem_requests = [0 for c in range(num_channels)]
            num_pim_requests = [0 for c in range(num_channels)]

            for line in open('../' + policy + '/' + app + '_' + pim):
                if 'Memory Partition' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    channel = int(tokens[2][:-1])
                elif 'avg_mrq_latency' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    dram_latency[policy][-1] = float(tokens[2])
                elif 'avg_dram_service_latency' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    dram_latency[policy][-1] += float(tokens[2])
                elif 'Read =' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_mem_requests[channel] = int(tokens[2])
                elif 'L2_WB =' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_mem_requests[channel] += int(tokens[2])
                elif 'PIM =' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    num_pim_requests[channel] = int(tokens[2])

            num_mem_requests = sum(num_mem_requests)
            num_pim_requests = sum(num_pim_requests)

            ideal_dram_latency = \
                    ((num_mem_requests * base_mem_dram_latency[app]) + \
                     (num_pim_requests * base_pim_dram_latency[pim])) / \
                    (num_mem_requests + num_pim_requests)

            dram_latency[policy][-1] /= ideal_dram_latency

        avg = gmean(dram_latency[policy])
        dram_latency[policy].append(avg)
        avg_dram_latency[policy].append(avg)

    gen_plot_single_pim(pim)

for policy in policies:
    avg_dram_latency[policy].append(gmean(avg_dram_latency[policy]))

gen_plot_all_pim()
