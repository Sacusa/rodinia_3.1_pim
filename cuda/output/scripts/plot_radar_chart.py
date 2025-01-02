#! /u/sgupta45/conda/bin/python3
from common import *

colors = {policy:colormap[i*2] for i, policy in enumerate(policies)}

def gen_plot():
    # Each attribute we'll plot in the radar chart.
    metrics = ['Throughput', 'Fairness', 'Utilization']

    # Number of variables we're plotting.
    num_vars = len(metrics)

    # Split the circle into even parts and save the angles
    # so we know where to put each axis.
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # The plot is a circle, so we need to "complete the loop"
    # and append the start value to the end.
    angles += angles[:1]

    # ax = plt.subplot(polar=True)
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True),
            dpi=600)

    # Helper function to plot each car on the radar chart.
    def add_to_radar(policy, color):
        values = [avg_weighted_speedup[policy], avg_fairness_index[policy],
                avg_bwutil[policy]]
        values += values[:1]
        ax.plot(angles, values, color=color, linewidth=2, label=labels[policy])
        #ax.fill(angles, values, color=color, alpha=0.25)

    # Add each car to the chart.
    for policy in policies:
        add_to_radar(policy, colors[policy])

    # Fix axis to go in the right order and start at 12 o'clock.
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Draw axis lines for each angle and label.
    ax.set_thetagrids(np.degrees(angles), [''] + metrics[1:] + metrics[:1],
            fontsize=25)

    # Go through metrics and adjust alignment based on where
    # it is in the circle.
    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')

    # Ensure radar goes from 0 to 100.
    ax.set_ylim(0, 100)
    # You can also set gridlines manually like this:
    # ax.set_rgrids([20, 40, 60, 80, 100])

    # Set position of y-labels (0-100) to be in the middle
    # of the first two axes.
    ax.set_rlabel_position(180 / num_vars)

    # Add some custom styling.
    # Change the color of the tick labels.
    ax.tick_params(colors='#222222')
    # Make the y-axis (0-100) labels smaller.
    ax.tick_params(axis='y', labelsize=20)
    # Change the color of the circular gridlines.
    ax.grid(color='#AAAAAA')
    # Change the color of the outermost gridline (the spine).
    ax.spines['polar'].set_color('#222222')
    # Change the background color inside the circle itself.
    ax.set_facecolor('#FAFAFA')

    # Add a legend as well.
    #ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

    ax.legend(bbox_to_anchor=(-0.2, 1.10, 1.35, 0.2), loc="lower left",
            ncol=len(policies), mode='expand', borderaxespad=0, fontsize=25)

    plt.savefig('../plots/all_radar_chart.pdf', bbox_inches='tight')

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

base_mem_time = get_base_mem_exec_time()

base_pim_time = {pim:0 for pim in pim_kernels}
base_pim_bwutil = {pim:[] for pim in pim_kernels}

for pim in pim_kernels:
    base_pim_bwutil[pim] = [0 for c in range(num_channels)]

    channel = -1

    filename = base_pim_files[pim] if pim in base_pim_files else pim + '_256'

    for line in open('/u/sgupta45/PIM_apps/STREAM/output/pim_rf_size_' +
            str(pim_rf_size) + '/' + filename + '_sm_' + str(pim_num_sm)):
        if 'gpu_tot_sim_cycle' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_pim_time[pim] = int(tokens[2])
        elif 'Memory Partition' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            channel = int(tokens[2][:-1])
        elif 'bwutil' in line:
            tokens = line.split()
            assert(len(tokens) == 3)
            base_pim_bwutil[pim][channel] = float(tokens[2])

    base_pim_bwutil[pim] = gmean(base_pim_bwutil[pim])

avg_weighted_speedup = {p:[] for p in policies}
avg_fairness_index = {p:[] for p in policies}
avg_bwutil = {p:[] for p in policies}

for pim in pim_kernels:
    ##############################################
    # Load execution times when run in combination
    ##############################################

    weighted_speedup = {p:[] for p in policies}
    fairness_index = {p:[] for p in policies}
    bwutil = {p:[] for p in policies}

    for policy in policies:
        for app in applications:
            mem_time, pim_time = get_exec_time(policy, pim, app, True, True)

            mem_speedup = base_mem_time[app] / mem_time
            pim_speedup = base_pim_time[pim] / pim_time

            weighted_speedup[policy].append(mem_speedup + pim_speedup)
            fairness_index[policy].append(min(mem_speedup / pim_speedup,
                        pim_speedup / mem_speedup))
            bwutil[policy].append(stats_db[policy][pim][app]["bwutil"])

    for policy in policies:
        avg_weighted_speedup[policy].append(
                (gmean(weighted_speedup[policy]) / 2) * 100)
        avg_fairness_index[policy].append(gmean(fairness_index[policy]) * 100)
        avg_bwutil[policy].append((gmean(bwutil[policy]) / \
                base_pim_bwutil[pim]) * 100)

for policy in policies:
    avg_weighted_speedup[policy] = gmean(avg_weighted_speedup[policy])
    avg_fairness_index[policy] = gmean(avg_fairness_index[policy])
    avg_bwutil[policy] = gmean(avg_bwutil[policy])

gen_plot()
