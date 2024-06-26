#! /u/sgupta45/conda/bin/python3
from common import *

colors['GPU'] = 'k'

def add_plot_single_pim(pim, speedup, ylabel, filename):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], speedup[policy], edgecolor='k',
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

    avg_label = 'GMean'
    if 'HMean' in ylabel: avg_label = 'HMean'
    plt.xticks(x, [app_labels[app] for app in applications] + [avg_label],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 1])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/' + pim + '_' + filename + '.pdf',
            bbox_inches='tight')

def add_plot_all_pim(speedup, ylabel, filename):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], speedup[policy], edgecolor='k',
                width=width, label=plabel, fc=colors[policy])

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

    avg_label = 'GMean'
    if 'HMean' in ylabel: avg_label = 'HMean'
    plt.xticks(x, [pim_labels[pim] for pim in pim_kernels] + [avg_label],
            fontsize=30)
    plt.ylabel(ylabel, fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 1])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_' + filename + '.pdf',
            bbox_inches='tight')

# Load baseline execution times
base_mem_time = get_base_mem_exec_time()

base_pim_time = {pim:0 for pim in pim_kernels}
base_pim_speedup = {pim:0 for pim in pim_kernels}

for pim in pim_kernels:
    filename = base_pim_files[pim] if pim in base_pim_files else pim + '_256'

    for line in open('/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_' +
            str(pim_rf_size) + '/' + filename + '_sm_' + str(pim_num_sm)):
        if 'gpu_tot_sim_cycle' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_pim_time[pim] = int(tokens[2])

    # Load GPU time
    filename = ''
    if pim in base_gpu_filename: filename = base_gpu_filename[pim]
    else:                        filename = pim + '_67108864'

    for line in open('/u/sgupta45/PIM_apps/STREAM_GPU/output/' + filename):
        if 'gpu_tot_sim_cycle' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_pim_speedup[pim] = base_pim_time[pim] / int(tokens[2])
            break

avg_mem_speedup = {p:[] for p in policies}
avg_pim_speedup = {p:[] for p in policies}
avg_hmean_speedup = {p:[] for p in policies}

for pim in pim_kernels:
    ##############################################
    # Load execution times when run in combination
    ##############################################

    if pim == 'stream_triad':
        stream_add_index = pim_kernels.index('stream_add')
        for policy in policies:
            avg_mem_speedup[policy].append(
                    avg_mem_speedup[policy][stream_add_index])
            avg_pim_speedup[policy].append(
                    avg_pim_speedup[policy][stream_add_index])
        continue

    mem_speedup = {p:[] for p in policies}
    pim_speedup = {p:[] for p in policies}
    hmean_speedup = {p:[] for p in policies}

    for policy in policies:
        print(pim, policy)

        for app in applications:
            mem_time, pim_time = get_exec_time(policy, pim, app, True, True)

            mem_speedup[policy].append(base_mem_time[app] / mem_time)
            pim_speedup[policy].append(base_pim_time[pim] / pim_time)
            hmean_speedup[policy].append(hmean([mem_speedup[policy][-1],
                pim_speedup[policy][-1]]))

        avg = gmean(mem_speedup[policy])
        mem_speedup[policy].append(avg)
        avg_mem_speedup[policy].append(avg)

        avg = gmean(pim_speedup[policy])
        pim_speedup[policy].append(avg)
        avg_pim_speedup[policy].append(avg)

        avg = hmean(hmean_speedup[policy])
        hmean_speedup[policy].append(avg)
        avg_hmean_speedup[policy].append(avg)

    add_plot_single_pim(pim, mem_speedup, 'GPU Speedup', 'speedup_mem')
    add_plot_single_pim(pim, hmean_speedup, 'HMean Speedup', 'speedup_hmean')

    # Add 'GPU' as a policy for PIM speedup
    policies = ['GPU'] + policies
    pim_speedup['GPU'] = [base_pim_speedup[pim] for i in \
            range(len(applications) + 1)]
    add_plot_single_pim(pim, pim_speedup, 'PIM Speedup', 'speedup_pim')
    policies = policies[1:]

for policy in policies:
    avg_mem_speedup[policy].append(gmean(avg_mem_speedup[policy]))
    avg_pim_speedup[policy].append(gmean(avg_pim_speedup[policy]))
    avg_hmean_speedup[policy].append(hmean(avg_hmean_speedup[policy]))

add_plot_all_pim(avg_mem_speedup, 'GPU Speedup', 'speedup_mem')
add_plot_all_pim(avg_mem_speedup, 'HMean Speedup', 'speedup_hmean')

# Add 'GPU' as a policy for PIM speedup
policies = ['GPU'] + policies
avg_pim_speedup['GPU'] = [base_pim_speedup[pim] for pim in pim_kernels]
avg_pim_speedup['GPU'].append(gmean(avg_pim_speedup['GPU']))
add_plot_all_pim(avg_pim_speedup, 'PIM Speedup', 'speedup_pim')
policies = policies[1:]
