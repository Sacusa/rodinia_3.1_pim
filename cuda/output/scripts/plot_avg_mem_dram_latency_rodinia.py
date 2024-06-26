#! /u/sgupta45/conda/bin/python3
from common import *
from functools import partial

def gen_plot_all_pim():
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], avg_mem_dram_latency[policy],
                edgecolor='k', width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(48, 8), dpi=600)
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
            fontsize=25)
    plt.ylabel('DRAM Access Latency\n(MEM only, normalized)', fontsize=30)
    plt.yticks(fontsize=30)

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_avg_mem_dram_latency_rodinia.pdf',
            bbox_inches='tight')

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

avg_mem_dram_latency = {p:[] for p in policies}

for app in applications:
    mem_dram_latency = {p:[] for p in policies}

    for policy in policies:
        print(app, policy)

        for pim in pim_kernels:
            if pim == 'stream_triad':
                stream_add_index = pim_kernels.index('stream_add')
                mem_dram_latency[policy].append(
                        mem_dram_latency[policy][stream_add_index])
                continue

            mem_dram_latency[policy].append(0)

            for line in open('../' + policy + '/' + app + '_' + pim):
                if 'avg_non_pim_mrq_latency' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    mem_dram_latency[policy][-1] = float(tokens[2])
                elif 'avg_non_pim_dram_service_latency' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    mem_dram_latency[policy][-1] += float(tokens[2])

            mem_dram_latency[policy][-1] /= base_mem_dram_latency[app]

        avg_mem_dram_latency[policy].append(gmean(mem_dram_latency[policy]))

for policy in policies:
    avg_mem_dram_latency[policy].append(gmean(avg_mem_dram_latency[policy]))

gen_plot_all_pim()
