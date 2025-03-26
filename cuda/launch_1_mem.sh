#!/bin/bash
source common.sh

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <mem> <policy> [policy parameters]"
    exit -1
fi

mem_app="$1" ; shift

# Get policy name
policy_name=$(get_policy_name "$@")
if [[ $? -ne 0 ]]; then
    exit
fi

# Set output directory
output_dir=${BASE_OUT_DIR}/${policy_name}
mkdir -p ${output_dir}

# Set up a private temporary directory
temp_dir=${BASE_TMP_DIR}/${policy_name}_${mem_app}_nop
mkdir -p ${temp_dir}
cp ${ROOT_DIR}/gpgpusim.config ${temp_dir}
cd ${temp_dir}

# Set configuration file
set_policy_in_config ${temp_dir} "$@" > /dev/null
if [[ $? -ne 0 ]]; then
    exit
fi

BIN="${ROOT_DIR}/main"
args=('0')
args+=("$(get_mem_args "${mem_app}")")

${BIN} "${args[@]}" &> ${output_dir}/${mem_app}_nop

# Delete temporary directory
cd ${ROOT_DIR}
rm -rf ${temp_dir}
