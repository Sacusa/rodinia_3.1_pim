#!/bin/bash

declare -a mem_apps=("b+tree" "backprop" "bfs" "cfd" "dwt2d" "gaussian"
    "heartwall" "hotspot" "hotspot3D" "huffman" "kmeans" "lavaMD"
    "lud" "mummergpu" "nn" "nw" "pathfinder" "srad_v1" "srad_v2"
    "streamcluster")

policy=$1
OUTPUT_DIR=/u/sgupta45/PIM_apps/rodinia_3.1_new/cuda/output

mkdir -p output/${policy}

for mem_app in "${mem_apps[@]}"; do
    #./launch_1_mem.sh ${mem_app} &> ${OUTPUT_DIR}/${policy}/${mem_app}_nop &
    ./launch_1_mem.sh ${mem_app} &> \
        ${OUTPUT_DIR}/${policy}/${mem_app}_nop_max_cores_72 &
done

wait
