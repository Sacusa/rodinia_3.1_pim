#!/bin/bash
source common.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <policy>"
    exit
fi

policy=$1
output_dir=output/${policy}
mkdir -p ${output_dir}

max_concurrent_apps=$((`nproc`))
num_concurrent_apps=0

for mem_app in "${mem_apps[@]}"; do
    ./launch_1_mem.sh ${mem_app} &> ${output_dir}/${mem_app}_nop &

    ((num_concurrent_apps++))

    if (( num_concurrent_apps == max_concurrent_apps )); then
        num_concurrent_apps=0
        wait
    fi
done

wait
