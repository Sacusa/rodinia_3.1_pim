#!/bin/bash
source common.sh

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 <mem1> <mem2> <policy> [policy parameters]"
    exit -1
fi

mem1_app="$1" ; shift
mem2_app="$2" ; shift

# Get policy name
policy_name=$(get_policy_name "$@")
if [[ $? -ne 0 ]]; then
    exit
fi

# Set output directory
output_dir=${BASE_OUT_DIR}/${policy_name}
mkdir -p ${output_dir}
output_file=${mem2_app}_${mem1_app}_mem

# Set up a private temporary directory
temp_dir=${BASE_TMP_DIR}/${policy_name}_${mem1_app}_${mem2_app}_mem
mkdir -p ${temp_dir}
cp ${ROOT_DIR}/gpgpusim.config ${temp_dir}
cd ${temp_dir}

# Set configuration file
set_policy_in_config ${temp_dir} "$@" > /dev/null
if [[ $? -ne 0 ]]; then
    exit
fi

BIN="${ROOT_DIR}/main"
args=('2')
args+=("$(get_mem_args "${mem1_app}")")
args+=("$(get_mem_args "${mem2_app}")")

${BIN} "${args[@]}" &> ${output_file}

# Cleanup
ensure_output_file_is_ascii ${output_file}
cd ${ROOT_DIR}
rm -rf ${temp_dir}
