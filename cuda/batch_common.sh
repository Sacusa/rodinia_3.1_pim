declare -a mem_apps=("b+tree" "backprop" "bfs" "cfd" "dwt2d" "gaussian"
    "heartwall" "hotspot" "hotspot3D" "huffman" "kmeans" "lavaMD"
    "lud" "mummergpu" "nn" "nw" "pathfinder" "srad_v1" "srad_v2"
    "streamcluster")

declare -a pim_apps=("stream_copy" "stream_daxpy" "stream_scale" "bn_fwd"
    "bn_bwd" "fully_connected" "kmeans" "histogram" "grim")

declare -a policy_ids=(
    0  # fifo
    1  # frfcfs/cap_0
    1  # frfcfs/cap_8
    1  # frfcfs/cap_16
    1  # frfcfs/cap_32
    1  # frfcfs/cap_64
    1  # frfcfs/cap_128
    4  # gi
    5  # gi_mem
    2  # mem_first
    3  # pim_first
    6  # bliss/interval_10000_threshold_4
    6  # bliss/interval_10000_threshold_8
    6  # bliss/interval_10000_threshold_16
    6  # bliss/interval_10000_threshold_32
    7  # rr/batch_1_slowdown_1
    7  # rr/batch_2_slowdown_1
    7  # rr/batch_4_slowdown_1
    7  # rr/batch_8_slowdown_1
    7  # rr/batch_16_slowdown_1
    8  # paws/cap_0_slowdown_3
    8  # paws/cap_8_slowdown_3
    8  # paws/cap_16_slowdown_3
    8  # paws/cap_32_slowdown_3
    8  # paws/cap_64_slowdown_3
    8  # paws/cap_128_slowdown_3
)
#declare -a outdirs=(
#    "fifo"
#    "frfcfs/cap_0"
#    "frfcfs/cap_8"
#    "frfcfs/cap_16"
#    "frfcfs/cap_32"
#    "frfcfs/cap_64"
#    "frfcfs/cap_128"
#    "gi"
#    "gi_mem"
#    "mem_first"
#    "pim_first"
#    "bliss/interval_10000_threshold_4"
#    "bliss/interval_10000_threshold_8"
#    "bliss/interval_10000_threshold_16"
#    "bliss/interval_10000_threshold_32"
#    "rr/batch_1_slowdown_1"
#    "rr/batch_2_slowdown_1"
#    "rr/batch_4_slowdown_1"
#    "rr/batch_8_slowdown_1"
#    "rr/batch_16_slowdown_1"
#    "paws/cap_0_slowdown_3"
#    "paws/cap_8_slowdown_3"
#    "paws/cap_16_slowdown_3"
#    "paws/cap_32_slowdown_3"
#    "paws/cap_64_slowdown_3"
#    "paws/cap_128_slowdown_3"
#)
declare -a outdirs=(
    "fifo_vc_2"
    "frfcfs_vc_2/cap_0"
    "frfcfs_vc_2/cap_8"
    "frfcfs_vc_2/cap_16"
    "frfcfs_vc_2/cap_32"
    "frfcfs_vc_2/cap_64"
    "frfcfs_vc_2/cap_128"
    "gi_vc_2"
    "gi_mem_vc_2"
    "mem_first_vc_2"
    "pim_first_vc_2"
    "bliss_vc_2/interval_10000_threshold_4"
    "bliss_vc_2/interval_10000_threshold_8"
    "bliss_vc_2/interval_10000_threshold_16"
    "bliss_vc_2/interval_10000_threshold_32"
    "rr_vc_2/batch_1_slowdown_1"
    "rr_vc_2/batch_2_slowdown_1"
    "rr_vc_2/batch_4_slowdown_1"
    "rr_vc_2/batch_8_slowdown_1"
    "rr_vc_2/batch_16_slowdown_1"
    "paws_vc_2/cap_0_slowdown_3"
    "paws_vc_2/cap_8_slowdown_3"
    "paws_vc_2/cap_16_slowdown_3"
    "paws_vc_2/cap_32_slowdown_3"
    "paws_vc_2/cap_64_slowdown_3"
    "paws_vc_2/cap_128_slowdown_3"
)

min () {
    a=$1
    b=$2
    c=$(( a < b ? a : b  ))
    echo "$c"
}

root_dir=/home/sgupta45/PIM/PIM_apps/rodinia_3.1_pim/cuda
config_file=${root_dir}/gpgpusim.config
bin=${root_dir}/main

num_vcs=2

max_frfcfs_cap=256
max_bliss_threshold=32
max_rr_batches=16
max_paws_cap=128

pim_slowdown_rr=1
pim_slowdown_paws=3
