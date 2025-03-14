#!/bin/bash
source common.sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <pim> <mem>"
    exit -1
fi

pim_app="$1"
mem_app="$2"

BIN="${ROOT_DIR}/main"
args=('3' "${pim_app}")
args+=("$(get_mem_args "${mem_app}")")

${BIN} "${args[@]}"
