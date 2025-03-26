#!/bin/bash
source common.sh

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <policy> [policy parameters]"
    exit
fi

max_concurrent_apps=$((`nproc`))
num_concurrent_apps=0

for mem_app in "${mem_apps[@]}"; do
    ./launch_1_mem.sh ${mem_app} ${@} &

    ((num_concurrent_apps++))

    if (( num_concurrent_apps == max_concurrent_apps )); then
        num_concurrent_apps=0
        wait
    fi
done

wait
