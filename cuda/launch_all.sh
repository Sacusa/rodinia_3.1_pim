#!/bin/bash

declare -a mem_apps=("b+tree" "backprop" "bfs" "cfd" "dwt2d" "gaussian"
    "heartwall" "hotspot" "hotspot3D" "huffman" "kmeans" "lavaMD"
    "lud" "mummergpu" "nn" "nw" "pathfinder" "srad_v1" "srad_v2"
    "streamcluster")

declare -a pim_apps=("stream_copy")

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <policy>"
    exit
fi

policy=$1

OUTPUT_DIR=/u/sgupta45/PIM_apps/rodinia_3.1_new/cuda/output
mkdir -p output/${policy}

max_concurrent_pim_apps=3
num_concurrent_pim_apps=0

for pim_app in "${pim_apps[@]}"; do
    for mem_app in "${mem_apps[@]}"; do
        ./launch.sh ${pim_app} ${mem_app} &> \
            ${OUTPUT_DIR}/${policy}/${mem_app}_${pim_app} &
    done

    ((num_concurrent_pim_apps++))

    if (( num_concurrent_pim_apps == max_concurrent_pim_apps  )); then
        wait
        num_concurrent_pim_apps=0
    fi
done

wait
