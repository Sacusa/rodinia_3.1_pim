#!/bin/bash
source common.sh

launch_competitive () {
    # ./launch_all_pim_mem.sh bliss 10000 4
    ./launch_all_pim_mem.sh fifo
    # ./launch_all_pim_mem.sh frfcfs 0
    # ./launch_all_pim_mem.sh frfcfs 32
    ./launch_all_pim_mem.sh fr_rr_fcfs
    ./launch_all_pim_mem.sh f3fs 256 1
    # ./launch_all_pim_mem.sh gi 64 56 32
    # ./launch_all_pim_mem.sh mem_first
    # ./launch_all_pim_mem.sh pim_first
}

launch_collaborative () {
    # ./launch_llm.sh bliss 10000 4
    ./launch_llm.sh fifo
    # ./launch_llm.sh frfcfs 0
    # ./launch_llm.sh frfcfs 32
    ./launch_llm.sh fr_rr_fcfs
    # ./launch_llm.sh gi 64 56 32
    # ./launch_llm.sh mem_first
    # ./launch_llm.sh pim_first
}

# VC 1 baseline
sed -i '/gpgpu_shader_to_mem_vcs/c\-gpgpu_shader_to_mem_vcs 1' gpgpusim.config
./launch_all_1_mem.sh frfcfs 0
mv output output_baseline

# VC 1 experiments
sed -i '/gpgpu_shader_to_mem_vcs/c\-gpgpu_shader_to_mem_vcs 1' gpgpusim.config
launch_competitive
launch_collaborative
./launch_llm.sh f3fs 256 0.5
mv output output_vc1

# VC 2 experiments
sed -i '/gpgpu_shader_to_mem_vcs/c\-gpgpu_shader_to_mem_vcs 2' gpgpusim.config
launch_competitive
launch_collaborative
./launch_llm.sh f3fs 64 1
mv output output_vc2
