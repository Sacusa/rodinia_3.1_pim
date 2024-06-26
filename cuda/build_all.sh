#!/bin/bash

declare -a mem_apps=("b+tree" "backprop" "bfs" "cfd" "dwt2d" "gaussian"
    "heartwall" "hotspot" "hotspot3D" "huffman" "kmeans" "lavaMD" "leukocyte"
    "lud" "mummergpu" "nn" "nw" "pathfinder" "streamcluster")

for mem_app in "${mem_apps[@]}"; do
    echo $mem_app
    cd $mem_app
    make clean ; make
    cd ..
done

cd srad/srad_v1
echo "srad_v1"
make clean ; make

cd ../srad_v2
echo "srad_v2"
make clean ; make

cd ../..
make
