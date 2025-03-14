#!/bin/bash

# We use the following two papers as reference for input sizes
# ANL paper: Jin, "The Rodinia Benchmark Suite in SYCL"
# CGO paper: Ivanov et al., "Retargeting and Respecializing GPU Workloads for
#            Performance Portability," CGO 2024

ROOT_DIR=/u/sgupta45/PIM_apps/rodinia_3.1_new/cuda
DATA_DIR=/u/sgupta45/rodinia_3.1/data

declare -a mem_apps=("b+tree" "backprop" "bfs" "cfd" "dwt2d" "gaussian"
    "heartwall" "hotspot" "hotspot3D" "huffman" "kmeans" "lavaMD"
    "lud" "mummergpu" "nn" "nw" "pathfinder" "srad_v1" "srad_v2"
    "streamcluster")

get_mem_args () {
    MEM_APP=$1

    if [ "$MEM_APP" == "b+tree" ]; then
        ARGS="${MEM_APP} file ${DATA_DIR}/b+tree/mil.txt \
            command ${DATA_DIR}/b+tree/command.txt"  # ANL
        #ARGS="${MEM_APP} file ${DATA_DIR}/b+tree/mil.txt \
        #    command ${DATA_DIR}/b+tree/command3.txt"  # CGO
    elif [ "$MEM_APP" == "backprop" ]; then
        #ARGS="${MEM_APP} 65536"      # ANL
        #ARGS="${MEM_APP} 112097152"  # CGO
        ARGS="${MEM_APP} 655360"
    elif [ "$MEM_APP" == "bfs" ]; then
        ARGS="${MEM_APP} ${DATA_DIR}/bfs/graph1MW_6.txt"  # ANL and CGO
    elif [ "$MEM_APP" == "cfd" ]; then
        ARGS="${MEM_APP} ${DATA_DIR}/cfd/fvcorr.domn.097K"  # ANL
        #ARGS="${MEM_APP} ${DATA_DIR}/cfd/fvcorr.domn.193K"  # CGO
    elif [ "$MEM_APP" == "dwt2d" ]; then
        ARGS="${MEM_APP} ${DATA_DIR}/dwt2d/rgb.bmp \
            -d 1024x1024 -f -5 -l 3"  # ANL
        #ARGS="${MEM_APP} ${DATA_DIR}/dwt2d/rgb.bmp \
        #    -d 20480x20480 -f -5 -l 1"  # CGO
    elif [ "$MEM_APP" == "gaussian" ]; then
        #ARGS="${MEM_APP} -f ${DATA_DIR}/gaussian/matrix1024.txt -q"  # ANL
        #ARGS="${MEM_APP} -f ${DATA_DIR}/gaussian/matrix2048.txt -q"  # CGO
        ARGS="${MEM_APP} -s 2048 -q"
    elif [ "$MEM_APP" == "heartwall" ]; then
        #ARGS="${MEM_APP} ${DATA_DIR}/heartwall/test.avi 20"  # ANL and CGO
        ARGS="${MEM_APP} ${DATA_DIR}/heartwall/test.avi 2"
    elif [ "$MEM_APP" == "hotspot" ]; then
        #ARGS="${MEM_APP} 512 2 2 ${DATA_DIR}/hotspot/temp_512 \
        #    ${DATA_DIR}/hotspot/power_512 output.out"  # ANL
        #ARGS="${MEM_APP} 2048 2 2048 ${DATA_DIR}/hotspot/temp_4096 \
        #    ${DATA_DIR}/hotspot/power_4096 /dev/null"  # CGO
        ARGS="${MEM_APP} 2048 4 2 ${DATA_DIR}/hotspot/temp_2048 \
            ${DATA_DIR}/hotspot/power_2048 /dev/null"
    elif [ "$MEM_APP" == "hotspot3D" ]; then
        #ARGS="${MEM_APP} 512 8 100 ${DATA_DIR}/hotspot3D/power_512x8 \
        #    ${DATA_DIR}/hotspot3D/temp_512x8 /dev/null"  # ANL
        #ARGS="${MEM_APP} 512 8 10000 \
        #    ${DATA_DIR}/hotspot3D/power_512x8 \
        #    ${DATA_DIR}/hotspot3D/temp_512x8 /dev/null"  # CGO
        ARGS="${MEM_APP} 512 8 10 ${DATA_DIR}/hotspot3D/power_512x8 \
            ${DATA_DIR}/hotspot3D/temp_512x8 /dev/null"
    elif [ "$MEM_APP" == "huffman" ]; then
        ARGS="${MEM_APP} ${DATA_DIR}/huffman/test1024_H2.206587175259.in"
    elif [ "$MEM_APP" == "kmeans" ]; then
        ARGS="${MEM_APP} -o -i ${DATA_DIR}/kmeans/kdd_cup"  # ANL
        #ARGS="${MEM_APP} -o -i ${DATA_DIR}/kmeans/92800.txt"
    elif [ "$MEM_APP" == "lavaMD" ]; then
        ARGS="${MEM_APP} -boxes1d 10"  # ANL
        #ARGS="${MEM_APP} -boxes1d 30"  # CGO
    elif [ "$MEM_APP" == "leukocyte" ]; then
        #ARGS="${MEM_APP} ${DATA_DIR}/leukocyte/testfile.avi 10"  # ANL
        ARGS="${MEM_APP} ${DATA_DIR}/leukocyte/testfile.avi 2"
    elif [ "$MEM_APP" == "lud" ]; then
        #ARGS="${MEM_APP} -i ${DATA_DIR}/lud/2048.dat"  # ANL
        #ARGS="${MEM_APP} -s 8192"  # CGO
        ARGS="${MEM_APP} -s 2048"
    elif [ "$MEM_APP" == "mummergpu" ]; then
        ARGS="${MEM_APP} ${DATA_DIR}/mummergpu/NC_003997.20k.fna \
            ${DATA_DIR}/mummergpu/NC_003997_q25bp.50k.fna"
    elif [ "$MEM_APP" == "nn" ]; then
        #ARGS="${MEM_APP} ../nn/filelist_4 -r 5 -lat 30 -lng 90"  # ANL and CGO
        ARGS="${MEM_APP} ${ROOT_DIR}/nn/filelist_10 -r 10 -lat 30 -lng 90"
    elif [ "$MEM_APP" == "nw" ]; then
        ARGS="${MEM_APP} 2048 10"  # ANL
        #ARGS="${MEM_APP} 10240 10"  # CGO
    elif [ "$MEM_APP" == "pathfinder" ]; then
        #ARGS="${MEM_APP} 100000 100 20"  # ANL
        ARGS="${MEM_APP} 100000 100 2"  # CGO
    elif [ "$MEM_APP" == "srad_v1" ]; then
        ARGS="${MEM_APP} 100 0.5 512 512"  # ANL
        #ARGS="${MEM_APP} 1 0.5 20480 20480"  # CGO
    elif [ "$MEM_APP" == "srad_v2" ]; then
        #ARGS="${MEM_APP} 512 512 0 127 0 127 0.5 2"  # ANL
        #ARGS="${MEM_APP} 2048 2048 0 127 0 127 0.5 20"  # CGO
        ARGS="${MEM_APP} 2048 2048 0 127 0 127 0.5 2"
    elif [ "$MEM_APP" == "streamcluster" ]; then
        ARGS="${MEM_APP} 10 20 256 65536 65536 1000 none /dev/null 1"  # ANL
        #ARGS="${MEM_APP} 2 3 256 1165536 1165536 1000 none /dev/null 1"  # CGO
    else
        echo "Invalid MEM app: ${MEM_APP}" >&2
        exit 1
    fi

    echo "${ARGS}"
}

set_policy_in_config () {
    policy=$1

    if [ "${policy}" == "bliss" ]; then
        if [ "$#" -ne 3 ]; then
            echo "ERROR: Policy ${policy} requires two additional arguments:" >&2
            echo "  Clearing interval" >&2
            echo "  Blacklisting threshold" >&2
            exit 1
        fi

        clearing_interval=$2
        blacklisting_threshold=$3

        sed -i '/gpgpu_dram_scheduler/c\-gpgpu_dram_scheduler 0' gpgpusim.config
        sed -i '/bliss_clearing_interval/c\-bliss_clearing_interval '"${clearing_interval}" gpgpusim.config
        sed -i '/bliss_blacklisting_threshold/c\-bliss_blacklisting_threshold '"${blacklisting_threshold}" gpgpusim.config

        echo "bliss_interval_${clearing_interval}_threshold_${blacklisting_threshold}"

    elif [ "${policy}" == "fifo" ]; then
        sed -i '/gpgpu_dram_scheduler/c\-gpgpu_dram_scheduler 1' gpgpusim.config

        echo "fifo"

    elif [ "${policy}" == "frfcfs" ]; then
        if [ "$#" -ne 2 ]; then
            echo "ERROR: Policy ${policy} requires one additional argument:" >&2
            echo "  Cap" >&2
            exit 1
        fi

        cap=$2

        sed -i '/gpgpu_dram_scheduler/c\-gpgpu_dram_scheduler 2' gpgpusim.config
        sed -i '/frfcfs_cap/c\-frfcfs_cap '"${cap}" gpgpusim.config

        echo "frfcfs_cap_${cap}"

    elif [ "${policy}" == "fr_rr_fcfs" ]; then
        sed -i '/gpgpu_dram_scheduler/c\-gpgpu_dram_scheduler 3' gpgpusim.config

        echo "fr_rr_fcfs"

    elif [ "${policy}" == "gi" ]; then
        if [ "$#" -ne 4 ]; then
            echo "ERROR: Policy ${policy} requires three additional arguments:" >&2
            echo "  PIM queue size" >&2
            echo "  High watermark" >&2
            echo "  Low watermark" >&2
            exit 1
        fi

        queue_size_string="${2}:${3}:${4}"

        sed -i '/gpgpu_dram_scheduler/c\-gpgpu_dram_scheduler 4' gpgpusim.config
        sed -i '/dram_pim_queue_size/c\-dram_pim_queue_size '"${queue_size_string}" gpgpusim.config

        echo "gi_${2}_${3}_${4}"

    elif [ "${policy}" == "mem_first" ]; then
        sed -i '/gpgpu_dram_scheduler/c\-gpgpu_dram_scheduler 5' gpgpusim.config

        echo "mem_first"

    elif [ "${policy}" == "pim_first" ]; then
        sed -i '/gpgpu_dram_scheduler/c\-gpgpu_dram_scheduler 6' gpgpusim.config

        echo "pim_first"

    elif [ "${policy}" == "f3fs" ]; then
        if [ "$#" -ne 3 ]; then
            echo "ERROR: Policy ${policy} requires two additional arguments:" >&2
            echo "  Cap" >&2
            echo "  Maximum PIM slowdown" >&2
            exit 1
        fi

        cap=$2
        max_pim_slowdown=$3

        sed -i '/gpgpu_dram_scheduler/c\-gpgpu_dram_scheduler 7' gpgpusim.config
        sed -i '/frfcfs_cap/c\-frfcfs_cap '"${cap}" gpgpusim.config
        sed -i '/dram_max_pim_slowdown/c\-dram_max_pim_slowdown '"${max_pim_slowdown}" gpgpusim.config

        echo "f3fs_cap_${cap}_slowdown_${max_pim_slowdown}"

    else
        echo "Invalid policy ${policy}" >&2
        exit 1

    fi
}
