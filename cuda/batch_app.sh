#!/bin/bash
#SBATCH -p reserved --reservation=sgupta45_20241001 -t 14-00:00:00
#SBATCH -c 2 --mem=16G --mail-type=fail
SBATCH_NAME
module load cuda/10.1
export CUDA_INSTALL_PATH=/software/cuda/10.1/usr/local/cuda-10.1
source /home/sgupta45/GPGPU-Sim-4.0.1/setup_environment release
LAUNCH_CMD
echo "DONE"
