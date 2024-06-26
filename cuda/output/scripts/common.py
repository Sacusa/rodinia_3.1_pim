import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
import numpy as np

applications = ['b+tree', 'backprop', 'bfs', 'cfd', 'dwt2d', 'gaussian',
        'heartwall', 'hotspot3D', 'hotspot', 'huffman', 'kmeans', 'lavaMD',
        'lud', 'mummergpu', 'nn', 'nw', 'pathfinder', 'srad_v1', 'srad_v2',
        'streamcluster']

pim_kernels = ['stream_add', 'stream_copy', 'stream_daxpy', 'stream_scale',
        'stream_triad', 'bn_fwd', 'bn_bwd', 'fully_connected', 'kmeans',
        'histogram', 'grim']

base_gpu_filename = {'fully_connected': 'fc_262144', 'grim': 'grim_32',
        'histogram': 'histogram_262144', 'kmeans': 'kmeans_262144'}
base_pim_files = {'kmeans': 'kmeans_1', 'fully_connected': 'fc_256',
        'histogram': 'histogram_1', 'grim': 'grim_32'}

all_policies = [
        'fifo',
        'frfcfs',
        'mem_first',
        'pim_first',
        'bliss/interval_10000_threshold_4',
        'gi',
        'gi_mem',
        'i3/batch_8_slowdown_2',
        'pim_frfcfs_util/cap_128_slowdown_4']
policies = [
        'fifo',
        'frfcfs',
        'mem_first',
        'pim_first',
        'bliss/interval_10000_threshold_4',
        'gi',
        'gi_mem',
        'i3/batch_8_slowdown_2']

colormap = matplotlib.cm.get_cmap("tab20").colors
colors = {policy:colormap[i*2] for i, policy in enumerate(all_policies)}
#colors = {policy:colormap[i] for i, policy in enumerate(all_policies)}

labels = {'fifo': 'FIFO', 'mem_first': 'MEM', 'pim_first': 'PIM',
        'frfcfs': 'FR-FCFS', 'bliss/interval_10000_threshold_4': 'BLISS',
        'gi': 'G&I', 'i3/batch_8_slowdown_2': 'RR', 'pim_frfcfs': 'FR-FCFS+',
        'pim_frfcfs_util/cap_128_slowdown_4': 'PAWS', 'gi_mem': 'G&I-MEM'}

app_labels = {applications[i] : 'G'+str(i+1) for i in range(len(applications))}
pim_labels = {pim_kernels[i] : 'P'+str(i+1) for i in range(len(pim_kernels))}

num_channels = 32
pim_rf_size = 8
pim_num_sm = 8

non_zeros = lambda l : [v for v in l if v != 0]

amean = lambda l : sum(l) / len(l)

def hmean(a):
    return len(a) / sum(1/i for i in a)

def gmean(iterable):
    a = np.array(iterable)
    return a.prod() ** (1.0 / len(a))

def get_base_mem_exec_time():
    base_mem_time = {app:0 for app in applications}

    for app in applications:
        for line in open('../frfcfs/' + app + '_nop'):
            if 'gpu_tot_sim_cycle' in line:
                tokens = line.split()
                assert(len(tokens) == 3)
                base_mem_time[app] = int(tokens[2])

    return base_mem_time

def get_base_pim_exec_time():
    base_pim_time = {pim:0 for pim in pim_kernels}

    for pim in pim_kernels:
        filename = base_pim_files[pim] if pim in base_pim_files \
                else pim + '_256'

        for line in open('/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_' +
                str(pim_rf_size) + '/' + filename + '_sm_' + str(pim_num_sm)):
            if 'gpu_tot_sim_cycle' in line:
                tokens = line.split()
                assert(len(tokens) == 3)
                base_pim_time[pim] = int(tokens[2])

    return base_pim_time

def get_exec_time(policy, pim, app, do_mem, do_pim):
    mem_time = 0
    pim_time = 0

    cycles = -1
    mem_found = not do_mem
    pim_found = not do_pim

    for line in open('../' + policy + '/' + app + '_' + pim):
        if 'gpu_tot_sim_cycle' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            cycles = int(tokens[2])
        elif '<<< MEM FINISHED >>>' in line:
            if not mem_found:
                mem_time = cycles
                mem_found = True
        elif '<<< PIM FINISHED >>>' in line:
            if not pim_found:
                pim_time = cycles
                pim_found = True

        if mem_found and pim_found: break

    if do_mem and do_pim:
        return mem_time, pim_time
    elif do_mem:
        return mem_time
    elif do_pim:
        return pim_time
    else:
        print("ERROR: get_exec_time called with do_mem=False and do_pim=False")
        exit(-1)
