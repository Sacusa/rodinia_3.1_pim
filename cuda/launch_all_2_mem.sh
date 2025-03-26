#!/bin/bash
source common.sh

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <policy> [policy parameters]"
    exit
fi

declare -a mem1_apps=("cfd" "gaussian" "nn" "pathfinder")

max_concurrent_apps=$((`nproc` / 2))
num_concurrent_apps=0

for mem1_app in "${mem1_apps[@]}"; do
    for mem2_app in "${mem_apps[@]}"; do
        ./launch_2_mem.sh ${mem1_app} ${mem2_app} ${@} &

        ((num_concurrent_apps++))

        if (( num_concurrent_apps == max_concurrent_apps )); then
            num_concurrent_apps=0
            wait
        fi
    done
done

wait
