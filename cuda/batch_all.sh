#!/bin/bash

declare -a mem_apps=("b+tree" "backprop" "bfs" "cfd" "dwt2d" "gaussian"
    "heartwall" "hotspot" "hotspot3D" "huffman" "kmeans" "lavaMD"
    "lud" "mummergpu" "nn" "nw" "pathfinder" "srad_v1" "srad_v2"
    "streamcluster")

declare -a pim_apps=("stream_copy" "stream_daxpy" "stream_scale" "bn_fwd"
    "bn_bwd" "fully_connected" "kmeans" "histogram" "grim")

declare -a policy_ids=(
    0   # fifo
    1   # frfcfs
    2   # gi
    14  # gi_mem
    21  # mem_first
    22  # pim_first
    15  # bliss/interval_10000_threshold_4
    15  # bliss/interval_10000_threshold_8
    15  # bliss/interval_10000_threshold_16
    15  # bliss/interval_10000_threshold_32
    11  # i3/batch_1_slowdown_2
    11  # i3/batch_2_slowdown_2
    11  # i3/batch_4_slowdown_2
    11  # i3/batch_8_slowdown_2
    11  # i3/batch_16_slowdown_2
    20  # pim_frfcfs_util/cap_0_slowdown_4
    20  # pim_frfcfs_util/cap_8_slowdown_4
    20  # pim_frfcfs_util/cap_16_slowdown_4
    20  # pim_frfcfs_util/cap_32_slowdown_4
    20  # pim_frfcfs_util/cap_64_slowdown_4
    20  # pim_frfcfs_util/cap_128_slowdown_4
)
#declare -a outdirs=(
#    "fifo"
#    "frfcfs"
#    "gi"
#    "gi_mem"
#    "mem_first"
#    "pim_first"
#    "bliss/interval_10000_threshold_4"
#    "bliss/interval_10000_threshold_8"
#    "bliss/interval_10000_threshold_16"
#    "bliss/interval_10000_threshold_32"
#    "i3/batch_1_slowdown_2"
#    "i3/batch_2_slowdown_2"
#    "i3/batch_4_slowdown_2"
#    "i3/batch_8_slowdown_2"
#    "i3/batch_16_slowdown_2"
#    "pim_frfcfs_util/cap_0_slowdown_4"
#    "pim_frfcfs_util/cap_8_slowdown_4"
#    "pim_frfcfs_util/cap_16_slowdown_4"
#    "pim_frfcfs_util/cap_32_slowdown_4"
#    "pim_frfcfs_util/cap_64_slowdown_4"
#    "pim_frfcfs_util/cap_128_slowdown_4"
#)
declare -a outdirs=(
    "fifo_vc_2"
    "frfcfs_vc_2"
    "gi_vc_2"
    "gi_mem_vc_2"
    "mem_first_vc_2"
    "pim_first_vc_2"
    "bliss_vc_2/interval_10000_threshold_4"
    "bliss_vc_2/interval_10000_threshold_8"
    "bliss_vc_2/interval_10000_threshold_16"
    "bliss_vc_2/interval_10000_threshold_32"
    "i3_vc_2/batch_1_slowdown_2"
    "i3_vc_2/batch_2_slowdown_2"
    "i3_vc_2/batch_4_slowdown_2"
    "i3_vc_2/batch_8_slowdown_2"
    "i3_vc_2/batch_16_slowdown_2"
    "pim_frfcfs_util_vc_2/cap_0_slowdown_4"
    "pim_frfcfs_util_vc_2/cap_8_slowdown_4"
    "pim_frfcfs_util_vc_2/cap_16_slowdown_4"
    "pim_frfcfs_util_vc_2/cap_32_slowdown_4"
    "pim_frfcfs_util_vc_2/cap_64_slowdown_4"
    "pim_frfcfs_util_vc_2/cap_128_slowdown_4"
)

min () {
    a=$1
    b=$2
    c=$(( a < b ? a : b  ))
    echo "$c"
}

root_dir=/home/sgupta45/PIM/PIM_apps/rodinia_3.1_pim/cuda
config_file=${root_dir}/gpgpusim.config

max_frfcfs_cap=128
max_i3_batches=16
max_bliss_threshold=32

pim_slowdown_i3=1
pim_slowdown_pim_frfcfs_util=3

for pim_app in "${pim_apps[@]}"; do
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

        for mem_app in "${mem_apps[@]}"; do
            tmp_dir="tmp/tmp_${policy_name}_${pim_app}_${mem_app}"
            mkdir -p ${tmp_dir}
            cd ${tmp_dir}

            # Clean the directory
            cp ${root_dir}/clean.sh .
            ./clean.sh

            # Create GPGPU-Sim config
            cp ${root_dir}/launch.sh .
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

            echo "${policy_name} / ${pim_app} / ${mem_app}"
            cp ${root_dir}/batch_app.sh .
            sed -i '/SBATCH_NAME/s/.*/#SBATCH -J '"${policy_name}"'_'"${pim_app}"'_'"${mem_app}"'/' batch_app.sh
            sed -i '\|LAUNCH_CMD|s|.*|./launch.sh '"${pim_app}"' '"${mem_app}"' \&> '"${outdir}/${mem_app}_${pim_app}"'|' batch_app.sh

            sbatch batch_app.sh
            cd ${root_dir}
        done

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
done
