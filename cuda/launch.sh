#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <pim> <mem>"
    exit -1
fi

pim_app="$1"
mem_app="$2"

ROOT_DIR=/home/sgupta45/PIM/PIM_apps/rodinia_3.1_pim/cuda
DATA_DIR=/scratch/sgupta45/rodinia_3.1_data

BIN="${ROOT_DIR}/main ${pim_app} ${mem_app}"

if [ "$mem_app" == "b+tree" ]; then
    ${BIN} file ${DATA_DIR}/b+tree/mil.txt \
        command ${DATA_DIR}/b+tree/command.txt  # ANL
    #${BIN} file ${DATA_DIR}/b+tree/mil.txt \
    #    command ${DATA_DIR}/b+tree/command3.txt  # CGO
elif [ "$mem_app" == "backprop" ]; then
    #${BIN} 65536  # ANL
    #${BIN} 112097152  # CGO
    ${BIN} 655360
elif [ "$mem_app" == "bfs" ]; then
    ${BIN} ${DATA_DIR}/bfs/graph1MW_6.txt  # ANL and CGO
elif [ "$mem_app" == "cfd" ]; then
    ${BIN} ${DATA_DIR}/cfd/fvcorr.domn.097K  # ANL
    #${BIN} ${DATA_DIR}/cfd/fvcorr.domn.193K  # CGO
elif [ "$mem_app" == "dwt2d" ]; then
    ${BIN} ${DATA_DIR}/dwt2d/rgb.bmp -d 1024x1024 -f -5 -l 3  # ANL
    #${BIN} ${DATA_DIR}/dwt2d/rgb.bmp -d 20480x20480 -f -5 -l 1  # CGO
elif [ "$mem_app" == "gaussian" ]; then
    #${BIN} -f ${DATA_DIR}/gaussian/matrix1024.txt -q  # ANL
    #${BIN} -f ${DATA_DIR}/gaussian/matrix2048.txt -q  # CGO
    ${BIN} -s 2048 -q
elif [ "$mem_app" == "heartwall" ]; then
    #${BIN} ${DATA_DIR}/heartwall/test.avi 20  # ANL and CGO
    ${BIN} ${DATA_DIR}/heartwall/test.avi 2
elif [ "$mem_app" == "hotspot" ]; then
    #${BIN} 512 2 2 ${DATA_DIR}/hotspot/temp_512 \
    #    ${DATA_DIR}/hotspot/power_512 output.out  # ANL
    #${BIN} 2048 2 2048 ${DATA_DIR}/hotspot/temp_4096 \
    #    ${DATA_DIR}/hotspot/power_4096 /dev/null  # CGO
    ${BIN} 2048 4 2 ${DATA_DIR}/hotspot/temp_2048 \
        ${DATA_DIR}/hotspot/power_2048 /dev/null
elif [ "$mem_app" == "hotspot3D" ]; then
    #${BIN} 512 8 100 ${DATA_DIR}/hotspot3D/power_512x8 \
    #    ${DATA_DIR}/hotspot3D/temp_512x8 /dev/null  # ANL
    #${BIN} 512 8 10000 \
    #    ${DATA_DIR}/hotspot3D/power_512x8 \
    #    ${DATA_DIR}/hotspot3D/temp_512x8 /dev/null  # CGO
    ${BIN} 512 8 10 ${DATA_DIR}/hotspot3D/power_512x8 \
        ${DATA_DIR}/hotspot3D/temp_512x8 /dev/null
elif [ "$mem_app" == "huffman" ]; then
    ${BIN} ${DATA_DIR}/huffman/test1024_H2.206587175259.in
elif [ "$mem_app" == "kmeans" ]; then
    ${BIN} -o -i ${DATA_DIR}/kmeans/kdd_cup  # ANL
    #${BIN} -o -i ${DATA_DIR}/kmeans/92800.txt
elif [ "$mem_app" == "lavaMD" ]; then
    ${BIN} -boxes1d 10  # ANL
    #${BIN} -boxes1d 30  # CGO
elif [ "$mem_app" == "leukocyte" ]; then
    #${BIN} ${DATA_DIR}/leukocyte/testfile.avi 10  # ANL
    ${BIN} ${DATA_DIR}/leukocyte/testfile.avi 2
elif [ "$mem_app" == "lud" ]; then
    #${BIN} -i ${DATA_DIR}/lud/2048.dat  # ANL
    #${BIN} -s 8192  # CGO
    ${BIN} -s 2048
elif [ "$mem_app" == "mummergpu" ]; then
    ${BIN} ${DATA_DIR}/mummergpu/NC_003997.20k.fna \
        ${DATA_DIR}/mummergpu/NC_003997_q25bp.50k.fna
elif [ "$mem_app" == "nn" ]; then
    #${BIN} ../nn/filelist_4 -r 5 -lat 30 -lng 90  # ANL and CGO
    ${BIN} ${ROOT_DIR}/nn/filelist_10 -r 10 -lat 30 -lng 90
elif [ "$mem_app" == "nw" ]; then
    ${BIN} 2048 10  # ANL
    #${BIN} 10240 10  # CGO
elif [ "$mem_app" == "pathfinder" ]; then
    #${BIN} 100000 100 20  # ANL
    ${BIN} 100000 100 2  # CGO
elif [ "$mem_app" == "srad_v1" ]; then
    ${BIN} 100 0.5 512 512  # ANL
    #${BIN} 1 0.5 20480 20480  # CGO
elif [ "$mem_app" == "srad_v2" ]; then
    #${BIN} 512 512 0 127 0 127 0.5 2  # ANL
    #${BIN} 2048 2048 0 127 0 127 0.5 20  # CGO
    ${BIN} 2048 2048 0 127 0 127 0.5 2
elif [ "$mem_app" == "streamcluster" ]; then
    ${BIN} 10 20 256 65536 65536 1000 none /dev/null 1  # ANL
    #${BIN} 2 3 256 1165536 1165536 1000 none /dev/null 1  # CGO
else
    echo "Invalid MEM app: ${mem_app}"
    exit -1
fi
