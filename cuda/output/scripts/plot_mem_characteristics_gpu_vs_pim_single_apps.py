#! /u/sgupta45/conda/bin/python3
from common import *

cont_mem_apps = ["gaussian", "nn", "pathfinder"]
cont_pim_apps = ["stream_add"]
#cont_all_apps = cont_mem_apps + cont_mem_apps + cont_pim_apps
cont_all_apps = cont_mem_apps + cont_pim_apps

cont_app_labels = {"stream_add": "STREAM-Add"}

metrics = ["ICNT_TRAFFIC", "DRAM_TRAFFIC", "BLP", "RBHR"]
metric_labels = {"ICNT_TRAFFIC": "NoC requests/cycle",
        "DRAM_TRAFFIC": "DRAM requests/cycle"}

avg_method = {"BLP": amean, "RBHR": hmean}
#ylim = {"ICNT_TRAFFIC": 21, "BLP": 16, "RBHR": 1}
#ytick_interval = {"ICNT_TRAFFIC": 3}
ylim = {"ICNT_TRAFFIC": 6, "DRAM_TRAFFIC": 6, "BLP": 16, "RBHR": 1}
ytick_interval = {}

def get_filename(app, app_type):
    if app_type == "GPU":
        return "../pim_frfcfs/single_apps/" + app + "_nop"
    elif app_type == "GPU(8)":
        return "../pim_frfcfs/single_apps/" + app + "_nop_max_cores_8"
    elif app_type == "PIM":
        return "/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_" + \
            str(pim_rf_size) + "/" + (base_pim_files[app] if app in \
            base_pim_files else app + "_256") + "_sm_" + str(pim_num_sm)

def get_stats(filename, is_pim):
    stats = {}
    stats["ICNT_TRAFFIC"] = 0
    stats["DRAM_TRAFFIC"] = 0
    stats["BLP"] = [0 for c in range(num_channels)]
    stats["RBHR"] = [0 for c in range(num_channels)]

    num_cycles = 0

    vc = "1" if is_pim else "0"
    network_line = "Req_Network_injected_packets_per_cycle (vc=" + vc + ")"

    line_no = 0

    for line in open(filename):
        line_no += 1

        if "gpu_tot_sim_cycle" in line:
            tokens = line.split()
            assert len(tokens) == 3, filename + "(" + str(line_no) + ")"
            num_cycles = float(tokens[2])
        elif network_line in line:
            tokens = line.split()
            assert len(tokens) == 4, filename + "(" + str(line_no) + ")"
            stats["ICNT_TRAFFIC"] = float(tokens[-1])
        elif "tot_mrq_num" in line:
            tokens = line.split()
            assert len(tokens) == 3, filename + "(" + str(line_no) + ")"
            stats["DRAM_TRAFFIC"] = float(tokens[-1])
        elif "Memory Partition" in line:
            tokens = line.split()
            assert len(tokens) == 3, filename + "(" + str(line_no) + ")"
            channel = int(tokens[2][:-1])
        elif line.startswith("Bank_Level_Parallism ="):
            tokens = line.split()
            assert len(tokens) == 3, filename + "(" + str(line_no) + ")"
            stats["BLP"][channel] = float(tokens[2])
        elif line.startswith("Row_Buffer_Locality ="):
            tokens = line.split()
            assert len(tokens) == 3, filename + "(" + str(line_no) + ")"
            stats["RBHR"][channel] = float(tokens[2])

    stats["DRAM_TRAFFIC"] = stats["DRAM_TRAFFIC"] / num_cycles
    stats["BLP"] = avg_method["BLP"](stats["BLP"])
    stats["RBHR"] = avg_method["RBHR"](stats["RBHR"])

    return stats

def gen_plots():
    def add_bar(index, value, color, min_threshold):
        plt.bar([index], [value], edgecolor="k", width=width, fc=color)

        if value < min_threshold:
            plt.text(index - 0.18, value + min_threshold, int(value),
                    fontsize=25)

    # plot parameters
    x = np.arange(len(cont_all_apps))

    for m in metrics:
        plt.clf()
        plt.figure(figsize=(4, 6), dpi=600)
        plt.rc("axes", axisbelow=True)

        max_value = 0
        for app in cont_all_apps:
            max_value = max(max_value, stats[m][app])
        min_threshold = max_value / 100

        width = 0.5
        x_index = 0

        for app in cont_mem_apps:
            add_bar(x[x_index], stats[m][app], 'r', min_threshold)
            x_index += 1

        #for app in cont_mem_apps:
        #    add_bar(x[x_index], stats[m][app + "8"], 'r', min_threshold)
        #    x_index += 1

        for app in cont_pim_apps:
            add_bar(x[x_index], stats[m][app], 'b', min_threshold)
            x_index += 1

        plt.xticks(x, [cont_app_labels[app] if app in cont_app_labels else app \
                for app in cont_all_apps], fontsize=30, rotation='vertical')
        plt.ylabel(metric_labels.get(m, m), fontsize=30)
        plt.yticks(fontsize=30)

        if m in ylim:
            plt.ylim([0, ylim[m]])

        if m in ytick_interval:
            plt.gca().yaxis.set_major_locator(
                    plt.MultipleLocator(ytick_interval[m]))

        plt.grid(axis="y", color="silver", linestyle="-", linewidth=1)

        # save the image
        plt.savefig("../plots/mem_characteristics_" + m + "_gpu_vs_pim.pdf",
                bbox_inches="tight")

stats = {m:{} for m in metrics}

#for app in cont_mem_apps:
#    app_stats = get_stats(get_filename(app, "GPU"), False)
#    for m in metrics:
#        stats[m][app] = app_stats[m]

for app in cont_mem_apps:
    app_stats = get_stats(get_filename(app, "GPU(8)"), False)
    for m in metrics:
        #stats[m][app + "8"] = app_stats[m]
        stats[m][app] = app_stats[m]

for app in cont_pim_apps:
    app_stats = get_stats(get_filename(app, "PIM"), True)
    for m in metrics:
        stats[m][app] = app_stats[m]
        if m == "RBHR":
            stats[m][app] /= 16

gen_plots()
