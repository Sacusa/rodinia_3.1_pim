#! /u/sgupta45/conda/bin/python3
from common import *

def get_num_mode_switches(stats_db, policies):
    avg_num_mode_switches = {p:[] for p in policies}

    for pim in pim_kernels:
        num_mode_switches = {p:[] for p in policies}

        for policy in policies:
            num_mode_switches[policy] = \
                    [stats_db[policy][pim][app]["num_mode_switches"] \
                    for app in applications]

        # Normalize values
        norm_values = [stats_db['fifo'][pim][app]["num_mode_switches"] \
                for app in applications]
        for policy in policies:
            for i in range(len(applications)):
                num_mode_switches[policy][i] = max(1,
                        num_mode_switches[policy][i])
                num_mode_switches[policy][i] /= norm_values[i]

            avg_num_mode_switches[policy].append(
                    gmean(num_mode_switches[policy]))

    for policy in policies:
        avg_num_mode_switches[policy].append(
                gmean(avg_num_mode_switches[policy]))

    return [avg_num_mode_switches[policy][-1] for policy in policies]

def gen_plot():
    def add_bar(offset, yval, label, color):
        plt.bar([i+offset for i in x], yval, edgecolor='k', width=width,
                label=label, fc=color)

    # plot parameters
    x = np.arange(len(policies))

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 6), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.4

    add_bar(-(width / 2), num_mode_switches_vc_1, 'VC1', colormap[0])
    add_bar(  width / 2,  num_mode_switches_vc_2, 'VC2', colormap[2])

    plt.xticks(x, [labels[policy] for policy in policies], fontsize=25)
    plt.yticks(fontsize=30)
    plt.ylabel('Mode Switches (normalized)', fontsize=30)
    #plt.ylim([0, 1])
    #plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=2, mode='expand', borderaxespad=0, fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_num_mode_switches_all_vcs.pdf',
            bbox_inches='tight')

# Load stats_db
stats_db = None

if len(sys.argv) == 2:
    if sys.argv[1] == "refresh":
        stats_db = recreate_and_return_stats_db()
    else:
        print("Incorrect argv\n")
        exit(-1)
else:
    stats_db = load_db()

num_mode_switches_vc_1 = get_num_mode_switches(stats_db, policies)
num_mode_switches_vc_2 = get_num_mode_switches(stats_db, policies_vc_2)

gen_plot()
