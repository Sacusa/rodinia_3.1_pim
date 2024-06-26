#! /u/sgupta45/conda/bin/python3
from common import *
from functools import partial

def gen_plot_single_pim(pim):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], mrq_percent[policy],
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

    #plt.xticks(x, applications + ['GMean'], fontsize=30, rotation='vertical')
    plt.xticks(x, [app_labels[app] for app in applications] + ['GMean'],
            fontsize=30)
    plt.ylabel('% DRAM Access Latency\nSpent Queuing', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 100])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_avg_mrq_percent.pdf',
            bbox_inches='tight')

def gen_plot_all_pim():
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], avg_mrq_percent[policy],
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
    plt.ylabel('% DRAM Access Latency\nSpent Queuing', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 100])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(10))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_avg_mrq_percent.pdf', bbox_inches='tight')

avg_mrq_percent = {p:[] for p in policies}

for pim in pim_kernels:
    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in policies:
            avg_mrq_percent[policy].append(
                    avg_mrq_percent[policy][stream_add_index])
        continue

    mrq_percent = {p:[] for p in policies}
    dram_latency = {p:[] for p in policies}

    for policy in policies:
        print(pim, policy)

        for app in applications:
            mrq_percent[policy].append(0)
            dram_latency[policy].append(0)

            for line in open('../' + policy + '/' + app + '_' + pim):
                if 'avg_mrq_latency' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    latency = float(tokens[2])
                    mrq_percent[policy][-1] = latency
                    dram_latency[policy][-1] = latency
                elif 'avg_dram_service_latency' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    dram_latency[policy][-1] += float(tokens[2])

            mrq_percent[policy][-1] /= (dram_latency[policy][-1] / 100)

        avg = gmean(mrq_percent[policy])
        mrq_percent[policy].append(avg)
        avg_mrq_percent[policy].append(avg)

    gen_plot_single_pim(pim)

for policy in policies:
    avg_mrq_percent[policy].append(gmean(avg_mrq_percent[policy]))

gen_plot_all_pim()
