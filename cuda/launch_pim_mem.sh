#!/bin/bash
source common.sh

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <pim> <mem> <policy> [policy parameters]"
    exit -1
fi

pim_app="$1" ; shift
mem_app="$1" ; shift

# Set configuration file and get a name for the policy
policy_name=$(set_policy_in_config "$@")
if [[ $? -ne 0 ]]; then
    exit
fi

# Set output directory
output_dir=${BASE_OUT_DIR}/${policy_name}
mkdir -p ${output_dir}

# Copy config to temporary directory and run simulation
temp_dir=${BASE_TMP_DIR}/${policy_name}_${pim_app}_${mem_app}
mkdir -p ${temp_dir}
cp ${ROOT_DIR}/gpgpusim.config ${temp_dir}
cd ${temp_dir}

BIN="${ROOT_DIR}/main"
args=('3' "${pim_app}")
args+=("$(get_mem_args "${mem_app}")")

${BIN} "${args[@]}" &> ${output_dir}/${mem_app}_${pim_app}

# Delete temporary directory
cd ${ROOT_DIR}
rm -rf ${temp_dir}
