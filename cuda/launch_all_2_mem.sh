#!/bin/bash

declare -a mem_apps=("b+tree" "backprop" "bfs" "cfd" "dwt2d" "gaussian"
    "heartwall" "hotspot" "hotspot3D" "huffman" "kmeans" "lavaMD"
    "lud" "mummergpu" "nn" "nw" "pathfinder" "srad_v1" "srad_v2"
    "streamcluster")

#mem1_app="gaussian"
#mem1_app="nn"
mem1_app="pathfinder"

policy=$1
OUTPUT_DIR=/u/sgupta45/PIM_apps/rodinia_3.1_new/cuda/output

mkdir -p output/${policy}

for mem2_app in "${mem_apps[@]}"; do
    ./launch_2_mem.sh ${mem1_app} ${mem2_app} &> \
        ${OUTPUT_DIR}/${policy}/${mem2_app}_${mem1_app}_mem &
done

wait
