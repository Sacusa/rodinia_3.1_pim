#!/bin/bash
source batch_common.sh

frfcfs_cap=0
bliss_threshold=4
rr_batches=1
paws_cap=0

sed -i '/-gpgpu_shader_to_mem_vcs/s/.*/-gpgpu_shader_to_mem_vcs '"${num_vcs}"'/' ${config_file}
sed -i '/-bliss_blacklisting_threshold/s/.*/-bliss_blacklisting_threshold '"${bliss_threshold}"'/' ${config_file}
sed -i '/-dram_min_pim_batches/s/.*/-dram_min_pim_batches '"${rr_batches}"'/' ${config_file}
sed -i '/-frfcfs_cap/s/.*/-frfcfs_cap '"${frfcfs_cap}"'/' ${config_file}

for p in ${!policy_ids[@]}; do
    policy_id="${policy_ids[$p]}"
    policy_name=""

    if [ "${policy_id}" = "1" ]; then
        policy_name="frfcfs_${frfcfs_cap}"
    elif [ "${policy_id}" = "6" ]; then
        policy_name="bliss_${bliss_threshold}"
    elif [ "${policy_id}" = "7" ]; then
        policy_name="rr_${rr_batches}_${pim_slowdown_rr}"
    elif [ "${policy_id}" = "8" ]; then
        policy_name="paws_${paws_cap}_${pim_slowdown_paws}"
    else
        policy_name="${outdirs[$p]}"
    fi

    # Create output and run directories
    outdir="/scratch/sgupta45/pim/${outdirs[$p]}"
    mkdir -p ${outdir}

    tmp_dir="tmp/tmp_${policy_name}_llm"
    mkdir -p ${tmp_dir}
    cd ${tmp_dir}

    # Clean the directory
    cp ${root_dir}/clean.sh .
    ./clean.sh

    # Create GPGPU-Sim config
    cp ${root_dir}/gpgpusim.config .

    sed -i '/-gpgpu_dram_scheduler/s/.*/-gpgpu_dram_scheduler '"${policy_id}"'/' gpgpusim.config

    if [ "${policy_id}" = "1" ]; then
        sed -i '/-frfcfs_cap/s/.*/-frfcfs_cap '"${frfcfs_cap}"'/' gpgpusim.config
    elif [ "${policy_id}" = "6" ]; then
        sed -i '/-bliss_blacklisting_threshold/s/.*/-bliss_blacklisting_threshold '"${bliss_threshold}"'/' ${config_file}
    elif [ "${policy_id}" = "7" ]; then
        sed -i '/-dram_min_pim_batches/s/.*/-dram_min_pim_batches '"${rr_batches}"'/' gpgpusim.config
        sed -i '/-dram_max_pim_slowdown/s/.*/-dram_max_pim_slowdown '"${pim_slowdown_rr}"'/' gpgpusim.config
    elif [ "${policy_id}" = "8" ]; then
        sed -i '/-frfcfs_cap/s/.*/-frfcfs_cap '"${paws_cap}"'/' gpgpusim.config
        sed -i '/-dram_max_pim_slowdown/s/.*/-dram_max_pim_slowdown '"${pim_slowdown_paws}"'/' gpgpusim.config
    fi

    echo "${policy_name} / llm"
    cp ${root_dir}/batch_app.sh .
    sed -i '/SBATCH_NAME/s/.*/#SBATCH -J '"${policy_name}"'_llm/' batch_app.sh
    sed -i '\|LAUNCH_CMD|s|.*|'"${bin}"' llm \&> '"${outdir}/llm"'|' batch_app.sh

    sbatch batch_app.sh
    cd ${root_dir}
done

if [ "${policy_id}" = "1" ]; then
    if [ "${frfcfs_cap}" = "0" ]; then
        frfcfs_cap="8"
    else
        frfcfs_cap=$((frfcfs_cap * 2))
    fi
    frfcfs_cap=$(min "${frfcfs_cap}" "${max_frfcfs_cap}")
elif [ "${policy_id}" = "6" ]; then
    bliss_threshold=$((bliss_threshold * 2))
    bliss_threshold=$(min "${bliss_threshold}" "${max_bliss_threshold}")
elif [ "${policy_id}" = "7" ]; then
    rr_batches=$((rr_batches * 2))
    rr_batches=$(min "${rr_batches}" "${max_rr_batches}")
elif [ "${policy_id}" = "8" ]; then
    if [ "${paws_cap}" = "0" ]; then
        paws_cap="8"
    else
        paws_cap=$((paws_cap * 2))
    fi
    paws_cap=$(min "${paws_cap}" "${max_paws_cap}")
fi
