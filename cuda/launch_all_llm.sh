#!/bin/bash
source common.sh

if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <policy> [policy parameters]"
    exit
fi

policy_out_dir=$(set_policy_in_config "$@")

if [[ $? -ne 0 ]]; then
    exit
fi

output_dir=output/${policy_out_dir}
mkdir -p ${output_dir}

./launch_llm.sh &> ${output_dir}/llm &

wait

./clean.sh
