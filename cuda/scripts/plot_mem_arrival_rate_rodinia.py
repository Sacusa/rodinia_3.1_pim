#! /usr/bin/python3
from common import *

def get_avg_arrival_rate(stats_db, policies, is_vc2):
    avg_arrival_rate = {p:[] for p in policies}

    for app in applications:
        if app == "llm":
            base_arrival_latency = get_arrival_latency(stats_db,
                    "frfcfs_cap_0", "llm_mem_only", "", False)
        else:
            base_arrival_latency = get_arrival_latency(stats_db,
                    "frfcfs_cap_0", app, "nop", False)

        arrival_rate = {p:[] for p in policies}

        for policy in policies:
            if app == "llm":
                app_arrival_latency = get_arrival_latency(stats_db,
                        policy, app, "", is_vc2)
            else:
                for pim in pim_kernels:
                    app_arrival_latency = get_arrival_latency(stats_db,
                            policy, app, pim, is_vc2)

            if app_arrival_latency > 0:
                arrival_rate[policy].append(\
                        base_arrival_latency / \
                        app_arrival_latency)
            else:
                arrival_rate[policy].append(0)

            avg_arrival_rate[policy].append(gmean(arrival_rate[policy]))

    for policy in policies:
        avg_arrival_rate[policy].append(gmean(avg_arrival_rate[policy]))

    return avg_arrival_rate

def get_arrival_latency(stats_db, policy, app, pim, is_vc2):
    policy_name = policies_vc_2[policies.index(policy)] if is_vc2 else policy

    if policy_name in stats_db:
        if pim in stats_db[policy_name]:
            if app in stats_db[policy_name][pim]:
                return stats_db[policy_name][pim][app]["dram_mem_arrival_latency"]

    arrival_latency = [0 for c in range(num_channels)]

    channel = -1

    outdir = "../output_vc2/" if is_vc2 else "../output_vc1/"
    filename = outdir + policy + "/" + app
    if pim: filename += "_" + pim

    for line in open(filename):
        if "Memory Partition" in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            channel = int(tokens[2][:-1])
        elif "AvgNonPimReqArrivalLatency" in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            arrival_latency[channel] = float(tokens[2])

    return amean(arrival_latency)

def add_plot_all_pim(avg_arrival_rate, vc):
    def add_bar(offset, policy):
        plabel = labels[policy] if policy in labels else policy
        plt.bar([i+offset for i in x], avg_arrival_rate[policy],
                edgecolor="k", width=width, label=plabel, fc=colors[policy])

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(54, 6), dpi=600)
    plt.rc("axes", axisbelow=True)

    width = 0.8 / len(policies)
    if len(policies) % 2 == 0:
        offset = -width * (0.5 + ((len(policies) / 2) - 1))
    else:
        offset = -width * ((len(policies) - 1) / 2)

    for policy in policies:
        add_bar(offset, policy)
        offset += width

    plt.xticks(x, [app_labels[app] for app in applications] + ["GMean"],
            fontsize=30)
    plt.ylabel("DRAM requests/cycle\n(normalized)", fontsize=30)
    plt.yticks(fontsize=30)
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(policies), mode="expand", borderaxespad=0, fontsize=25)
    plt.grid(axis="y", color="silver", linestyle="-", linewidth=1)

    # save the image
    plt.savefig("plots/mem_arrival_rate_vc_" + str(vc) + ".pdf",
            bbox_inches="tight")

# Load stats_db
stats_db = None

if stats_db_exists():
    stats_db = load_db()
else:
    stats_db = recreate_and_return_stats_db()

applications += ["llm"]

avg_arrival_rate_vc_1 = get_avg_arrival_rate(stats_db, policies, False)
avg_arrival_rate_vc_2 = get_avg_arrival_rate(stats_db, policies, True)

add_plot_all_pim(avg_arrival_rate_vc_1, 1)
add_plot_all_pim(avg_arrival_rate_vc_2, 2)
