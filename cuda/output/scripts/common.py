import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
import numpy as np
import sys

###################
# Apps and policies
###################

applications = ['b+tree', 'backprop', 'bfs', 'cfd', 'dwt2d', 'gaussian',
        'heartwall', 'hotspot3D', 'hotspot', 'huffman', 'kmeans', 'lavaMD',
        'lud', 'mummergpu', 'nn', 'nw', 'pathfinder', 'srad_v1', 'srad_v2',
        'streamcluster']

pim_kernels = ['stream_add', 'stream_copy', 'stream_daxpy', 'stream_scale',
        'bn_fwd', 'bn_bwd', 'fully_connected', 'kmeans',
        'histogram', 'grim']

base_gpu_filename = {'fully_connected': 'fc_262144', 'grim': 'grim_32',
        'histogram': 'histogram_262144', 'kmeans': 'kmeans_262144'}
base_pim_files = {'kmeans': 'kmeans_1', 'fully_connected': 'fc_256',
        'histogram': 'histogram_1', 'grim': 'grim_32'}

all_policies = [
        'fifo',
        'mem_first',
        'pim_first',
        'frfcfs/cap_0',
        'frfcfs/cap_32',
        'bliss/interval_10000_threshold_4',
        'fr_rr_fcfs',
        'gi',
        #'gi_mem',
        'pim_frfcfs/cap_256',
        'paws/cap_128_slowdown_3'
]
policies = all_policies

policies_vc_2 = []
for policy in policies:
    tokens = policy.split("/")
    tokens[0] += "_vc_2"
    policies_vc_2.append("/".join(tokens))

#################
# Plot parameters
#################

colormap = matplotlib.cm.get_cmap("tab20").colors
colors = {policy:colormap[i*2] for i, policy in enumerate(all_policies)}

labels = {
        'fifo': 'FCFS',
        'mem_first': 'MEM',
        'pim_first': 'PIM',
        'frfcfs/cap_0': 'FR-FCFS',
        'frfcfs/cap_32': 'FR-FCFS-Cap',
        'bliss/interval_10000_threshold_4': 'BLISS',
        'fr_rr_fcfs': 'FR-RR-FCFS',
        'gi': 'G&I',
        'gi_mem': 'G&I-MEM',
        'pim_frfcfs/cap_256': 'F3FS',
        'paws/cap_128_slowdown_3': 'AC-FR-FCFS'
}

app_labels = {applications[i] : 'G'+str(i+1) for i in range(len(applications))}
app_labels['llm'] = 'LLM'
pim_labels = {pim_kernels[i] : 'P'+str(i+1) for i in range(len(pim_kernels))}

############
# PIM config
############

num_channels = 32
pim_rf_size = 8
pim_num_sm = 8

################
# Helper methods
################

non_zeros = lambda l : [v for v in l if v != 0]

amean = lambda l : sum(l) / len(l)

def hmean(a):
    return len(a) / sum(1/i for i in a)

def gmean(iterable):
    a = np.array(iterable)
    return a.prod() ** (1.0 / len(a))

INFINITE = int(sys.float_info.max)

#########################
# Data load/store methods
#########################

stats_db_fields = ["mem_time", "pim_time", "dram_mem_arrival_latency",
        "num_mode_switches", "switch_latency", "switch_conflicts", "bwutil"]
stats_db_filename = "stats_db.txt"
stats_db = None

def recreate_and_return_stats_db():
    def print_warning(msg):
        print("WARNING (" + ",".join([policy, pim, app]) + "): " + msg)

    def write_to_file():
        line_tokens = [policy, pim, app] + \
                [str(stats_db[policy][pim][app][f]) for f in stats_db_fields]
        stats_db_file.write(",".join(line_tokens) + "\n")

    global stats_db
    stats_db = {}

    with open(stats_db_filename, "w") as stats_db_file:
        for policy in policies + policies_vc_2:
            stats_db[policy] = {}

            for pim in pim_kernels:
                stats_db[policy][pim] = {}

                for app in applications:
                    print(policy, pim, app)
                    stats_db[policy][pim][app] = {}

                    # execution time
                    mem_time = -1
                    pim_time = -1
                    cycles = -1
                    mem_time_found = False
                    pim_time_found = False

                    # DRAM MEM arrival latency
                    arrival_latency = [0 for c in range(num_channels)]

                    # number of switches
                    pim2mem_mode_switches = [0 for c in range(num_channels)]
                    mem2pim_mode_switches = [0 for c in range(num_channels)]
                    num_mem_iterations = 0
                    num_pim_iterations = 0
                    channel = -1

                    # switch overheads
                    switch_latency = [0 for c in range(num_channels)]
                    switch_conflicts = [0 for c in range(num_channels)]

                    # bandwidth utilization
                    bwutil = [0 for c in range(num_channels)]

                    for line in open('../' + policy + '/' + app + '_' + pim):
                        if 'launching kernel' in line:
                            tokens = line.split()
                            assert len(tokens) == 10, "/".join(
                                    [policy, pim, app])
                            stream = int(tokens[3])
                            cycles = int(tokens[9])

                            if stream == 1:
                                if pim_time == -1:
                                    pim_time = cycles
                            else:
                                if mem_time == -1:
                                    mem_time = cycles

                        elif 'gpu_tot_sim_cycle' in line:
                            tokens = line.split()
                            assert(len(tokens) == 3)
                            cycles = int(tokens[2])

                        elif '<<< MEM FINISHED >>>' in line:
                            num_mem_iterations += 1
                            if not mem_time_found:
                                mem_time = cycles - mem_time
                                mem_time_found = True

                        elif '<<< PIM FINISHED >>>' in line:
                            num_pim_iterations += 1
                            if not pim_time_found:
                                pim_time = cycles - pim_time
                                pim_time_found = True

                        elif 'Memory Partition' in line:
                            tokens = line.split()
                            assert(len(tokens) == 3)
                            channel = int(tokens[2][:-1])

                        elif 'AvgNonPimReqArrivalLatency' in line:
                            tokens = line.split()
                            assert(len(tokens) == 3)
                            arrival_latency[channel] = float(tokens[2])

                        elif 'pim2nonpimswitches' in line:
                            tokens = line.split()
                            assert(len(tokens) == 3)
                            pim2mem_mode_switches[channel] = int(tokens[2])

                        elif 'nonpim2pimswitches' in line:
                            tokens = line.split()
                            assert(len(tokens) == 3)
                            mem2pim_mode_switches[channel] = int(tokens[2])

                        elif "nonpim2pimswitchlatency" in line:
                            tokens = line.split()
                            assert(len(tokens) == 3)
                            switch_latency[channel] = float(tokens[2])

                        elif "nonpim2pimswitchconflicts" in line:
                            tokens = line.split()
                            assert(len(tokens) == 3)
                            switch_conflicts[channel] = float(tokens[2])

                        elif 'bwutil' in line:
                            tokens = line.split()
                            assert(len(tokens) == 3)
                            bwutil[channel] = float(tokens[2])

                    # Accumulate DRAM MEM arrival latency stats
                    arrival_latency = amean(arrival_latency)

                    # Accumulate exec time stats
                    if not mem_time_found:
                        mem_time = INFINITE
                        print_warning("mem_app did not finish")

                    if not pim_time_found:
                        pim_time = INFINITE
                        print_warning("pim_app did not finish")

                    # Accumulate mode switch stats
                    avg_mode_switches = [0 for c in range(num_channels)]

                    for c in range(num_channels):
                        # Some PIM-First/MEM-First may not have recorded
                        # MEM->PIM/PIM->MEM switches, so account for that here
                        if pim2mem_mode_switches[c] == 0 and \
                                mem2pim_mode_switches[c] > 0:
                            pim2mem_mode_switches[c] = mem2pim_mode_switches[c]
                        elif mem2pim_mode_switches[c] == 0 and \
                                pim2mem_mode_switches[c] > 0:
                            mem2pim_mode_switches[c] = pim2mem_mode_switches[c]

                        avg_mode_switches[c] = pim2mem_mode_switches[c] + \
                                mem2pim_mode_switches[c]

                    avg_mode_switches = sum(avg_mode_switches) / \
                            max(num_mem_iterations, num_pim_iterations)

                    # Accumulate switch overhead stats
                    for c in range(num_channels):
                        if mem2pim_mode_switches[c] > 0:
                            switch_latency[c] /= mem2pim_mode_switches[c]
                            switch_conflicts[c] /= mem2pim_mode_switches[c]
                        else:
                            assert switch_latency[c] == 0
                            assert switch_conflicts[c] == 0

                    switch_latency = amean(switch_latency)
                    switch_conflicts = amean(switch_conflicts)

                    # Accumulate bandwidth utilization stats
                    assert(0 not in bwutil)
                    bwutil = gmean(bwutil)

                    # Write to stats_db and stats_db_file
                    stats_db[policy][pim][app]["mem_time"] = mem_time
                    stats_db[policy][pim][app]["pim_time"] = pim_time
                    stats_db[policy][pim][app]["dram_mem_arrival_latency"] = \
                            arrival_latency
                    stats_db[policy][pim][app]["num_mode_switches"] = \
                            avg_mode_switches
                    stats_db[policy][pim][app]["switch_latency"] = \
                            switch_latency
                    stats_db[policy][pim][app]["switch_conflicts"] = \
                            switch_conflicts
                    stats_db[policy][pim][app]["bwutil"] = bwutil

                    write_to_file()

    return stats_db

def load_db():
    global stats_db
    stats_db = {}

    all_policies = policies + policies_vc_2

    for policy in all_policies:
        stats_db[policy] = {}
        for pim in pim_kernels:
            stats_db[policy][pim] = {}
            for app in applications:
                stats_db[policy][pim][app] = {}

    with open(stats_db_filename, "r") as stats_db_file:
        for line in stats_db_file:
            tokens = line.split(",")
            policy, pim, app = tokens[:3]

            if (policy not in all_policies) or (pim not in pim_kernels) or \
                    (app not in applications):
                continue

            for i in range(len(stats_db_fields)):
                stats_db[policy][pim][app][stats_db_fields[i]] = \
                        float(tokens[i + 3])

    return stats_db

def get_base_mem_exec_time():
    base_mem_time = {app:0 for app in applications}

    for app in applications:
        for line in open('../pim_frfcfs/single_apps/' + app + '_nop'):
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
    if (policy in stats_db) and (pim in stats_db[policy]) and \
            (app in stats_db[policy][pim]):
        mem_time = stats_db[policy][pim][app]["mem_time"]
        pim_time = stats_db[policy][pim][app]["pim_time"]
    else:
        mem_time, pim_time = get_exec_time_from_file(policy, pim, app)

    if do_mem and do_pim:
        return mem_time, pim_time
    elif do_mem:
        return mem_time
    elif do_pim:
        return pim_time
    else:
        print("ERROR: " + __name__ + \
                " called with do_mem=False and do_pim=False")
        exit(-1)

def get_exec_time_from_file(policy, pim, app):
    mem_time = -1
    pim_time = -1
    cycles = -1
    mem_time_found = False
    pim_time_found = False

    for line in open('../' + policy + '/' + app + '_' + pim):
        if 'launching kernel' in line:
            tokens = line.split()
            assert len(tokens) == 10, "/".join(
                    [policy, pim, app])
            stream = int(tokens[3])
            cycles = int(tokens[9])

            if stream == 1:
                if pim_time == -1:
                    pim_time = cycles
            else:
                if mem_time == -1:
                    mem_time = cycles

        elif 'gpu_tot_sim_cycle' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            cycles = int(tokens[2])

        elif '<<< MEM FINISHED >>>' in line:
            if not mem_time_found:
                mem_time = cycles - mem_time
                mem_time_found = True

                if pim_time_found:
                    break

        elif '<<< PIM FINISHED >>>' in line:
            if not pim_time_found:
                pim_time = cycles - pim_time
                pim_time_found = True

                if mem_time_found:
                    break

    if not mem_time_found:
        mem_time = INFINITE

    if not pim_time_found:
        pim_time = INFINITE

    return mem_time, pim_time

def get_mem2_exec_time(policy, mem_app1, mem_app2):
    mem_time = -1
    cycles = -1
    did_app2_finish = False

    for line in open('../' + policy + '/' + mem_app2 + '_' + mem_app1):
        if 'launching kernel' in line:
            tokens = line.split()
            assert len(tokens) == 10, "/".join([policy, mem_app2, mem_app1])

            stream = int(tokens[3])
            if stream == 0 and mem_time == -1:
                mem_time = int(tokens[9])
        elif 'gpu_tot_sim_cycle' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            cycles = int(tokens[2])
        elif '<<< MEM2 FINISHED >>>' in line:
            mem_time = cycles - mem_time
            did_app2_finish = True
            break

    if not did_app2_finish:
        mem_time = INFINITE
        print("WARNING (" + __name__ + "(" + policy + "," + mem_app1 + "," + \
                mem_app2 + "): app2 did not finish. Setting mem_time to " + \
                str(mem_time))

    return mem_time
