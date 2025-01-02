#! /u/sgupta45/conda/bin/python3
from common import *

compute_units = ["GPU", "GPU(8)", "PIM"]
metrics = ["MPKC", "BLP", "RBHR"]

avg_method = {"MPKC": hmean, "BLP": amean, "RBHR": hmean}
ylim = {"MPKC": 6000, "BLP": 16, "RBHR": 1}

def get_filename(cu, app):
    if cu == "GPU":
        return "../pim_frfcfs/single_apps/" + app + "_nop"
    elif cu == "GPU(8)":
        return "../pim_frfcfs/single_apps/" + app + "_nop_max_cores_8"
    elif cu == "PIM":
        return "/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_" + \
            str(pim_rf_size) + "/" + (base_pim_files[app] if app in \
            base_pim_files else app + "_256") + "_sm_" + str(pim_num_sm)

def get_stats(filename):
    stats = {}
    stats["MPKC"] = 0
    stats["BLP"] = [0 for c in range(num_channels)]
    stats["RBHR"] = [0 for c in range(num_channels)]

    line_no = 0

    for line in open(filename):
        line_no += 1

        if "gpu_tot_sim_cycle" in line:
            tokens = line.split()
            assert len(tokens) == 3, filename + "(" + str(line_no) + ")"
            stats["MPKC"] = float(tokens[2])
        elif "tot_mrq_num" in line:
            tokens = line.split()
            assert len(tokens) == 3, filename + "(" + str(line_no) + ")"
            stats["MPKC"] = (float(tokens[2]) * 1000) / stats["MPKC"]
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

    stats["BLP"] = avg_method["BLP"](stats["BLP"])
    stats["RBHR"] = avg_method["RBHR"](stats["RBHR"])

    return stats

def add_plot_for_each_metric():
    def add_bars(color, min_threshold):
        plt.bar([i for i in x], values, edgecolor="k", width=width,
                fc=color)

        for i, val in enumerate(values):
            if val < min_threshold:
                plt.text(i - 0.18, val + min_threshold, int(val),
                        fontsize=25)

    # plot parameters
    x = np.arange(len(compute_units))

    for m in metrics:
        plt.clf()
        plt.figure(figsize=(4, 8), dpi=600)
        plt.rc("axes", axisbelow=True)

        width = 0.5
        values = [stats[m][cu] for cu in compute_units]
        add_bars('k', stats[m]['PIM'] / 100)

        plt.xticks(x, compute_units, fontsize=30, rotation='vertical')
        plt.ylabel(m, fontsize=30)
        plt.yticks(fontsize=30)

        if m in ylim:
            plt.ylim([0, ylim[m]])

        plt.grid(axis="y", color="silver", linestyle="-", linewidth=1)

        # save the image
        plt.savefig("../plots/mem_characteristics_" + m + "_gpu_vs_pim.pdf",
                bbox_inches="tight")

stats = {m:{cu:[] for cu in compute_units} for m in metrics}

for m in metrics:
    for cu in ["GPU", "GPU(8)"]:
        for app in applications:
            app_stats = get_stats(get_filename(cu, app))
            stats[m][cu].append(app_stats[m])
        stats[m][cu] = avg_method[m](stats[m][cu])

    for cu in ["PIM"]:
        for app in pim_kernels:
            app_stats = get_stats(get_filename(cu, app))
            stats[m][cu].append(app_stats[m])
        stats[m][cu] = avg_method[m](stats[m][cu])

        if m == "RBHR":
            stats[m][cu] /= 16

add_plot_for_each_metric()
