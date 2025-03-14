#!/bin/bash
source common.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <policy>"
    exit
fi

declare -a pim_apps=("stream_copy" "stream_daxpy" "stream_scale" "bn_fwd"
    "bn_bwd" "fully_connected" "kmeans" "histogram" "grim")

policy=$1
output_dir=output/${policy}
mkdir -p ${output_dir}

max_concurrent_apps=$((`nproc` / 2))
num_concurrent_apps=0

for pim_app in "${pim_apps[@]}"; do
    for mem_app in "${mem_apps[@]}"; do
        ./launch_mem.sh ${pim_app} ${mem_app} &> \
            ${output_dir}/${mem_app}_${pim_app} &

        ((num_concurrent_apps++))

        if (( num_concurrent_apps == max_concurrent_apps )); then
            num_concurrent_apps=0
            wait
        fi
    done
done

wait
