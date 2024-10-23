#!/bin/bash
source common.sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <mem1> <mem2>"
    exit -1
fi

mem1_app="$1"
mem2_app="$2"

BIN="${ROOT_DIR}/main"
args=('2')
args+=("$(get_mem_args "${mem1_app}")")
args+=("$(get_mem_args "${mem2_app}")")

${BIN} "${args[@]}"
