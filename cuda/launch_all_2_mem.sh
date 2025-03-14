#!/bin/bash
source common.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <policy>"
    exit
fi

declare -a mem1_apps=("gaussian" "nn" "pathfinder")

policy=$1
output_dir=output/${policy}
mkdir -p ${output_dir}

max_concurrent_apps=$((`nproc` / 2))
num_concurrent_apps=0

for mem1_app in "${mem1_apps[@]}"; do
    for mem2_app in "${mem_apps[@]}"; do
        ./launch_2_mem.sh ${mem1_app} ${mem2_app} &> \
            ${output_dir}/${mem2_app}_${mem1_app}_mem &

        ((num_concurrent_apps++))

        if (( num_concurrent_apps == max_concurrent_apps )); then
            num_concurrent_apps=0
            wait
        fi
    done
done

wait
