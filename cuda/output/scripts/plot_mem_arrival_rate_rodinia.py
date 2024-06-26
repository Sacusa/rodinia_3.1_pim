#! /u/sgupta45/conda/bin/python3
from common import *

def add_plot_all_pim():
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], avg_arrival_latency[policy],
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
            fontsize=30)
    plt.ylabel('MEM Arrival Rate (normalized)', fontsize=30)
    plt.yticks(fontsize=30)
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_mem_arrival_rate_rodinia.pdf',
            bbox_inches='tight')

base_arrival_latency = {app:[] for app in applications}

for app in applications:
    base_arrival_latency[app] = [0 for c in range(num_channels)]

    channel = -1

    for line in open('../frfcfs/' + app + '_nop'):
        if 'Memory Partition' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            channel = int(tokens[2][:-1])
        elif 'AvgNonPimReqArrivalLatency' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_arrival_latency[app][channel] = float(tokens[2])

    base_arrival_latency[app] = amean(base_arrival_latency[app])

avg_arrival_latency = {p:[] for p in policies}

for app in applications:
    arrival_latency = {p:[] for p in policies}

    for policy in policies:
        print(app, policy)

        for pim in pim_kernels:
            if pim == 'stream_triad':
                stream_add_index = pim_kernels.index('stream_add')
                arrival_latency[policy].append(
                        arrival_latency[policy][stream_add_index])
                continue

            arrival_latency[policy].append([0 for c in range(num_channels)])

            channel = -1

            for line in open('../' + policy + '/' + app + '_' + pim):
                if 'Memory Partition' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    channel = int(tokens[2][:-1])
                elif 'AvgNonPimReqArrivalLatency' in line:
                    tokens = line.split()
                    assert(len(tokens) == 3)
                    arrival_latency[policy][-1][channel] = float(tokens[2])

            arrival_latency[policy][-1] = base_arrival_latency[app] / \
                    amean(arrival_latency[policy][-1])

        avg_arrival_latency[policy].append(gmean(arrival_latency[policy]))

for policy in policies:
    avg_arrival_latency[policy].append(gmean(avg_arrival_latency[policy]))

add_plot_all_pim()
