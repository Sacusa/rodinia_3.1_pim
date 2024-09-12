#!/bin/bash

declare -a policy_ids=(
    0   # fifo
    1   # frfcfs
    2   # gi
    14  # gi_mem
    21  # mem_first
    22  # pim_first
    15  # bliss/interval_10000_threshold_4
    11  # i3/batch_8_slowdown_2
    20  # pim_frfcfs_util/cap_128_slowdown_4
)
declare -a outdirs=(
    "fifo"
    "frfcfs"
    "gi"
    "gi_mem"
    "mem_first"
    "pim_first"
    "bliss/interval_10000_threshold_4"
    "i3/batch_8_slowdown_2"
    "pim_frfcfs_util/cap_128_slowdown_4"
)

min () {
    a=$1
    b=$2
    c=$(( a < b ? a : b  ))
    echo "$c"
}

root_dir=/home/sgupta45/PIM/PIM_apps/rodinia_3.1_pim/cuda
bin="${root_dir}/main"
config_file=${root_dir}/gpgpusim.config

max_frfcfs_cap=128
max_i3_batches=16
max_bliss_threshold=32

pim_slowdown_i3=1
pim_slowdown_pim_frfcfs_util=3

frfcfs_cap=0
i3_batches=1
bliss_threshold=4

sed -i '/-frfcfs_cap/s/.*/-frfcfs_cap '"${frfcfs_cap}"'/' ${config_file}
sed -i '/-dram_min_pim_batches/s/.*/-dram_min_pim_batches '"${i3_batches}"'/' ${config_file}
sed -i '/-bliss_blacklisting_threshold/s/.*/-bliss_blacklisting_threshold '"${bliss_threshold}"'/' ${config_file}

for p in ${!policy_ids[@]}; do
    policy_id="${policy_ids[$p]}"
    policy_name=""

    if [ "${policy_id}" = "11" ]; then
        policy_name="i3_${i3_batches}"
    elif [ "${policy_id}" = "20" ]; then
        policy_name="pim_frfcfs_util_${frfcfs_cap}"
    elif [ "${policy_id}" = "15" ]; then
        policy_name="bliss_${bliss_threshold}"
    else
        policy_name="${outdirs[$p]}"
    fi

    # Create output and run directories
    outdir="/scratch/sgupta45/pim/${outdirs[$p]}"
    mkdir -p ${outdir}

    tmp_dir="tmp/tmp_${policy_name}_llm"
    mkdir -p ${tmp_dir}
    cd ${tmp_dir}

    # Clean the directory
    cp ${root_dir}/clean.sh .
    ./clean.sh

    # Create GPGPU-Sim config
    cp ${root_dir}/gpgpusim.config .

    sed -i '/-gpgpu_dram_scheduler/s/.*/-gpgpu_dram_scheduler '"${policy_id}"'/' gpgpusim.config

    if [ "${policy_id}" = "11" ]; then
        sed -i '/-dram_min_pim_batches/s/.*/-dram_min_pim_batches '"${i3_batches}"'/' gpgpusim.config
        sed -i '/-dram_max_pim_slowdown/s/.*/-dram_max_pim_slowdown '"${pim_slowdown_i3}"'/' gpgpusim.config
    elif [ "${policy_id}" = "20" ]; then
        sed -i '/-frfcfs_cap/s/.*/-frfcfs_cap '"${frfcfs_cap}"'/' gpgpusim.config
        sed -i '/-dram_max_pim_slowdown/s/.*/-dram_max_pim_slowdown '"${pim_slowdown_pim_frfcfs_util}"'/' gpgpusim.config
    elif [ "${policy_id}" = "15" ]; then
        sed -i '/-bliss_blacklisting_threshold/s/.*/-bliss_blacklisting_threshold '"${bliss_threshold}"'/' ${config_file}
    fi

    echo "${policy_name} / llm"
    cp ${root_dir}/batch_app.sh .
    sed -i '/SBATCH_NAME/s/.*/#SBATCH -J '"${policy_name}"'_llm/' batch_app.sh
    sed -i '\|LAUNCH_CMD|s|.*|'"${bin}"' llm \&> '"${outdir}/llm"'|' batch_app.sh

    sbatch batch_app.sh
    cd ${root_dir}

    if [ "${policy_id}" = "11" ]; then
        i3_batches=$((i3_batches * 2))
        i3_batches=$(min "${i3_batches}" "${max_i3_batches}")
    elif [ "${policy_id}" = "20" ]; then
        if [ "${frfcfs_cap}" = "0" ]; then
            frfcfs_cap="8"
        else
            frfcfs_cap=$((frfcfs_cap * 2))
        fi
        frfcfs_cap=$(min "${frfcfs_cap}" "${max_frfcfs_cap}")
    elif [ "${policy_id}" = "15" ]; then
        bliss_threshold=$((bliss_threshold * 2))
        bliss_threshold=$(min "${bliss_threshold}" "${max_bliss_threshold}")
    fi
done
