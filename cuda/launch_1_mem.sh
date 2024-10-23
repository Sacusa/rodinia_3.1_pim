#!/bin/bash
source common.sh

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <mem>"
    exit -1
fi

mem_app="$1"

BIN="${ROOT_DIR}/main"
args=('0')
args+=("$(get_mem_args "${mem_app}")")

${BIN} "${args[@]}"
