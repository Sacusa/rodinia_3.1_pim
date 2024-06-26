include ../common/make.config

CC=nvcc
CCFLAGS=-ccbin g++ -m64 -lcudart --std=c++11 -O3 -lm \
		-gencode arch=compute_70,code=compute_70 -Xcompiler -fopenmp

PIM_DIR = /home/sgupta45/PIM/PIM_apps

PIM_DEPS = $(PIM_DIR)/common.o \
		   $(PIM_DIR)/STREAM/pim_stream.o \
		   $(PIM_DIR)/STREAM/pim_real.o

BTREE_DEPS = b+tree/main.o \
			 b+tree/kernel/kernel_gpu_cuda_wrapper.o \
			 b+tree/kernel/kernel_gpu_cuda_wrapper_2.o \
			 b+tree/util/timer/timer.o \
			 b+tree/util/num/num.o \
			 b+tree/util/cuda/cuda.o

BACKPROP_DEPS = backprop/backprop.o \
				backprop/facetrain.o \
				backprop/imagenet.o \
				backprop/backprop_cuda.o

BFS_DEPS = bfs/bfs.o

CFD_DEPS = cfd/euler3d.o

DWT2D_DEPS = dwt2d/main.cu.o \
			 dwt2d/dwt.cu.o \
			 dwt2d/components.cu.o \
			 dwt2d/dwt_cuda/fdwt53.cu.o \
			 dwt2d/dwt_cuda/fdwt97.cu.o \
			 dwt2d/dwt_cuda/common.cu.o \
			 dwt2d/dwt_cuda/rdwt97.cu.o \
			 dwt2d/dwt_cuda/rdwt53.cu.o

GAUSSIAN_DEPS = gaussian/gaussian.o

HEARTWALL_DEPS = heartwall/main.o \
				 heartwall/AVI/avilib.o \
				 heartwall/AVI/avimod.o

HOTSPOT_DEPS = hotspot/hotspot.o

HOTSPOT3D_DEPS = hotspot3D/3D.o

HUFFMAN_DEPS = huffman/main_test_cu.o \
			   huffman/stats_logger.o \
			   huffman/vlc_kernel_sm64huff.o \
			   huffman/scan.o \
			   huffman/pack_kernels.o \
			   huffman/cpuencode.o

KMEANS_DEPS = kmeans/cluster.o \
			  kmeans/getopt.o \
			  kmeans/kmeans.o \
			  kmeans/kmeans_clustering.o \
			  kmeans/kmeans_cuda.o \
			  kmeans/rmse.o

LAVAMD_DEPS = lavaMD/main.o \
			  lavaMD/kernel/kernel_gpu_cuda_wrapper.o \
			  lavaMD/util/num/num.o \
			  lavaMD/util/timer/timer.o \
			  lavaMD/util/device/device.o

LEUKOCYTE_DEPS = leukocyte/CUDA/detect_main.o \
				 leukocyte/CUDA/find_ellipse.o \
				 leukocyte/CUDA/find_ellipse_kernel.o \
				 leukocyte/CUDA/track_ellipse.o \
				 leukocyte/CUDA/track_ellipse_kernel.o \
				 leukocyte/CUDA/misc_math.o \
				 leukocyte/meschach_lib/meschach.a

LUD_DEPS = lud/common/common.o \
		   lud/cuda/lud.o \
		   lud/cuda/lud_kernel.o

MUMMERGPU_DEPS = mummergpu/src/obj/release/mummergpu_main.o
MUMMERGPU_FLAGS = -lmummergpu -L mummergpu/lib -lGL -lGLU

NN_DEPS = nn/nn.o

NW_DEPS = nw/needle.o

PATHFINDER_DEPS = pathfinder/pathfinder.o

SRAD_DEPS = srad/srad_v1/main.o srad/srad_v2/srad.o

STREAMCLUSTER_DEPS = streamcluster/streamcluster_cuda_cpu.o \
					 streamcluster/streamcluster_cuda.o \
					 streamcluster/streamcluster_header.o

LLM_DEPS = gemm.o

ALL_DEPS = $(PIM_DEPS) $(BTREE_DEPS) $(BACKPROP_DEPS) $(BFS_DEPS) $(CFD_DEPS) \
		   $(DWT2D_DEPS) $(GAUSSIAN_DEPS) $(HEARTWALL_DEPS) $(HOTSPOT_DEPS) \
		   $(HOTSPOT3D_DEPS) $(HUFFMAN_DEPS) $(KMEANS_DEPS) $(LAVAMD_DEPS) \
		   $(LEUKOCYTE_DEPS) $(LUD_DEPS) $(MUMMERGPU_DEPS) $(NN_DEPS) \
		   $(NW_DEPS) $(PATHFINDER_DEPS) $(SRAD_DEPS) $(STREAMCLUSTER_DEPS) \
		   $(LLM_DEPS)

main: $(ALL_DEPS) main.cu
	$(CC) $(CCFLAGS) $(MUMMERGPU_FLAGS) $(ALL_DEPS) main.cu -o main

gemm.o: gemm.cu
	$(CC) $(CCFLAGS) gemm.cu -c -o gemm.o

clean:
	rm main
