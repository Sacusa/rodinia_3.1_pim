#!/bin/bash

declare -a mem_apps=("b+tree" "backprop" "bfs" "cfd" "dwt2d" "gaussian"
    "heartwall" "hotspot" "hotspot3D" "huffman" "kmeans" "lavaMD"
    "lud" "mummergpu" "nn" "nw" "pathfinder" "srad_v1" "srad_v2"
    "streamcluster")

declare -a pim_apps=("stream_add")

policy=$1
max_concurrent_policies=3
num_concurrent_policies=0

mkdir -p output/${policy}

for pim_app in "${pim_apps[@]}"; do
    for mem_app in "${mem_apps[@]}"; do
        ./launch.sh ${pim_app} ${mem_app} &> \
            output/${policy}/${mem_app}_${pim_app} &
    done

    ((num_concurrent_policies++))

    if (( num_concurrent_policies == max_concurrent_policies  )); then
        wait
        num_concurrent_policies=0
    fi
done

wait
