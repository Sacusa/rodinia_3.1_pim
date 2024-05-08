#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <pim> <mem>"
    exit -1
fi

pim_app="$1"
mem_app="$2"

if [ "$mem_app" == "b+tree" ]; then
    ./main ${pim_app} ${mem_app} file ../data/b+tree/mil.txt \
        command ../data/b+tree/command.txt  # ANL
    #./main ${pim_app} ${mem_app} file ../data/b+tree/mil.txt \
    #    command ../data/b+tree/command3.txt  # CGO
elif [ "$mem_app" == "backprop" ]; then
    #./main ${pim_app} ${mem_app} 65536  # ANL
    #./main ${pim_app} ${mem_app} 112097152  # CGO
    ./main ${pim_app} ${mem_app} 655360
elif [ "$mem_app" == "bfs" ]; then
    ./main ${pim_app} ${mem_app} ../data/bfs/graph1MW_6.txt  # ANL and CGO
elif [ "$mem_app" == "cfd" ]; then
    ./main ${pim_app} ${mem_app} ../data/cfd/fvcorr.domn.097K  # ANL
    #./main ${pim_app} ${mem_app} ../data/cfd/fvcorr.domn.193K  # CGO
elif [ "$mem_app" == "dwt2d" ]; then
    ./main ${pim_app} ${mem_app} ../data/dwt2d/rgb.bmp -d 1024x1024 \
        -f -5 -l 3  # ANL
    #./main ${pim_app} ${mem_app} ../data/dwt2d/rgb.bmp -d 20480x20480 \
    #    -f -5 -l 1  # CGO
elif [ "$mem_app" == "gaussian" ]; then
    #./main ${pim_app} ${mem_app} -f ../data/gaussian/matrix1024.txt  # ANL
    #./main ${pim_app} ${mem_app} -f ../data/gaussian/matrix2048.txt  # CGO
    ./main ${pim_app} ${mem_app} -s 2048
elif [ "$mem_app" == "heartwall" ]; then
    #./main ${pim_app} ${mem_app} ../data/heartwall/test.avi 20  # ANL and CGO
    ./main ${pim_app} ${mem_app} ../data/heartwall/test.avi 2
elif [ "$mem_app" == "hotspot" ]; then
    #./main ${pim_app} ${mem_app} 512 2 2 ../data/hotspot/temp_512 \
    #    ../data/hotspot/power_512 output.out  # ANL
    #./main ${pim_app} ${mem_app} 2048 2 2048 ../data/hotspot/temp_4096 \
    #    ../data/hotspot/power_4096 /dev/null  # CGO
    ./main ${pim_app} ${mem_app} 2048 4 2 ../data/hotspot/temp_2048 \
        ../data/hotspot/power_2048 /dev/null
elif [ "$mem_app" == "hotspot3D" ]; then
    #./main ${pim_app} ${mem_app} 512 8 100 ../data/hotspot3D/power_512x8 \
    #    ../data/hotspot3D/temp_512x8 /dev/null  # ANL
    #./main ${pim_app} ${mem_app} 512 8 10000 ../data/hotspot3D/power_512x8 \
    #    ../data/hotspot3D/temp_512x8 /dev/null  # CGO
    ./main ${pim_app} ${mem_app} 512 8 10 ../data/hotspot3D/power_512x8 \
        ../data/hotspot3D/temp_512x8 /dev/null
elif [ "$mem_app" == "huffman" ]; then
    ./main ${pim_app} ${mem_app} ../data/huffman/test1024_H2.206587175259.in
elif [ "$mem_app" == "kmeans" ]; then
    ./main ${pim_app} ${mem_app} -o -i ../data/kmeans/kdd_cup  # ANL
    #./main ${pim_app} ${mem_app} -o -i ../data/kmeans/92800.txt
elif [ "$mem_app" == "lavaMD" ]; then
    ./main ${pim_app} ${mem_app} -boxes1d 10  # ANL
    #./main ${pim_app} ${mem_app} -boxes1d 30  # CGO
elif [ "$mem_app" == "leukocyte" ]; then
    #./main ${pim_app} ${mem_app} ../data/leukocyte/testfile.avi 10  # ANL
    ./main ${pim_app} ${mem_app} ../data/leukocyte/testfile.avi 2
elif [ "$mem_app" == "lud" ]; then
    #./main ${pim_app} ${mem_app} -i ../data/lud/2048.dat  # ANL
    #./main ${pim_app} ${mem_app} -s 8192  # CGO
    ./main ${pim_app} ${mem_app} -s 2048
elif [ "$mem_app" == "mummergpu" ]; then
    ./main ${pim_app} ${mem_app} ../data/mummergpu/NC_003997.20k.fna \
        ../data/mummergpu/NC_003997_q25bp.50k.fna
elif [ "$mem_app" == "nn" ]; then
    #./main ${pim_app} ${mem_app} nn/filelist_4 -r 5 -lat 30 -lng 90
    # ANL and CGO
    ./main ${pim_app} ${mem_app} nn/filelist_10 -r 10 -lat 30 -lng 90
elif [ "$mem_app" == "nw" ]; then
    ./main ${pim_app} ${mem_app} 2048 10  # ANL
    #./main ${pim_app} ${mem_app} 10240 10  # CGO
elif [ "$mem_app" == "pathfinder" ]; then
    #./main ${pim_app} ${mem_app} 100000 100 20  # ANL
    ./main ${pim_app} ${mem_app} 100000 100 2  # CGO
elif [ "$mem_app" == "srad_v1" ]; then
    ./main ${pim_app} ${mem_app} 100 0.5 512 512  # ANL
    #./main ${pim_app} ${mem_app} 1 0.5 20480 20480  # CGO
elif [ "$mem_app" == "srad_v2" ]; then
    #./main ${pim_app} ${mem_app} 512 512 0 127 0 127 0.5 2  # ANL
    #./main ${pim_app} ${mem_app} 2048 2048 0 127 0 127 0.5 20  # CGO
    ./main ${pim_app} ${mem_app} 2048 2048 0 127 0 127 0.5 2
elif [ "$mem_app" == "streamcluster" ]; then
    ./main ${pim_app} ${mem_app} 10 20 256 65536 65536 1000 none \
        /dev/null 1  # ANL
    #./main ${pim_app} ${mem_app} 2 3 256 1165536 1165536 1000 none \
    #    /dev/null 1  # CGO
else
    echo "Invalid MEM app: ${mem_app}"
    exit -1
fi
