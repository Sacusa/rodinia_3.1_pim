#! /u/sgupta45/conda/bin/python3
from common import *

cont_nop_apps = ["nop_72"]
cont_mem_apps = ["gaussian", "nn", "pathfinder"]
cont_pim_apps = ["stream_add"]
cont_all_apps = cont_nop_apps + cont_mem_apps + cont_pim_apps
cont_all_lists = [cont_nop_apps, cont_mem_apps, cont_pim_apps]

cont_app_labels = {"nop_72": "72 SMs", "stream_add": "+STREAM-Add"}

all_colors = ['k', 'r', 'b', 'g', 'y']

# Removing mummergpu from applications because it didn't finish with nn
applications.remove("mummergpu")

def add_plot_all_apps():
    def add_bar(offset, cont_app, color):
        plt.bar([i+offset for i in x], speedup[cont_app], edgecolor='k',
                width=width, label=cont_app, fc=color)

    # plot parameters
    x = np.arange(len(applications) + 1)

    # add the bars
    plt.clf()
    plt.figure(figsize=(24, 8), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.8 / len(cont_all_apps)
    if len(cont_all_apps) % 2 == 0:
        offset = -width * (0.5 + ((len(cont_all_apps) / 2) - 1))
    else:
        offset = -width * ((len(cont_all_apps) - 1) / 2)

    for i, cont_app in enumerate(cont_all_apps):
        add_bar(offset, cont_app, all_colors[i])
        offset += width

    plt.xticks(x, [app_labels[app] for app in applications] + ['GMean'],
            fontsize=30)
    plt.ylabel('Speedup', fontsize=30)
    plt.yticks(fontsize=30)
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.1))

    plt.legend(bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left",
            ncol=len(cont_all_apps), mode='expand', borderaxespad=0,
            fontsize=25)
    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_speedup_gpu_vs_pim.pdf',
            bbox_inches='tight')

def add_plot_avg_only():
    def add_bar(index, value, color):
        plt.bar([index], [value], edgecolor="k", width=width, fc=color)

    # plot parameters
    x = np.arange(len(cont_all_apps))

    # add the bars
    plt.clf()
    plt.figure(figsize=(4, 6), dpi=600)
    plt.rc('axes', axisbelow=True)

    width = 0.5
    x_index = 0

    for c, app_list in enumerate(cont_all_lists):
        for cont_app in app_list:
            add_bar(x[x_index], speedup[cont_app][-1], all_colors[c])
            x_index += 1

    plt.xticks(x, [cont_app_labels[app] if app in cont_app_labels \
            else "+" + app for app in cont_all_apps], fontsize=30,
            rotation='vertical')
    plt.ylabel('Speedup', fontsize=30)
    plt.yticks(fontsize=30)
    plt.ylim([0, 1])
    plt.gca().yaxis.set_major_locator(plt.MultipleLocator(0.2))

    plt.grid(axis='y', color='silver', linestyle='-', linewidth=1)

    # save the image
    plt.savefig('../plots/all_speedup_gpu_vs_pim_avg_only.pdf',
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

# Load baseline execution times
base_mem_time = get_base_mem_exec_time()

speedup = {app:[] for app in cont_all_apps}

for app in applications:
    # Execution time alone on limited SMs
    for cont_app in cont_nop_apps:
        speedup[cont_app].append(base_mem_time[app] / \
                get_exec_time("pim_frfcfs/single_apps", "nop_max_cores_72",
                    app, True, False))

    # Execution time with GPU
    for cont_app in cont_mem_apps:
        speedup[cont_app].append(base_mem_time[app] / \
            get_mem2_exec_time("pim_frfcfs/two_mem", cont_app + "_mem_8_72",
                app))

    # Execution time with PIM
    for cont_app in cont_pim_apps:
        speedup[cont_app].append(base_mem_time[app] / \
                get_exec_time("pim_frfcfs/cap_0", cont_app, app, True, False))

for cont_app in cont_all_apps:
    speedup[cont_app].append(gmean(speedup[cont_app]))

add_plot_all_apps()
add_plot_avg_only()
