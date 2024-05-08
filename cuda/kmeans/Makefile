include ../../common/make.config

# C compiler
CC = gcc
CC_FLAGS = -I$(CUDA_DIR)/include -g -fopenmp -O2 -lstdc++

# CUDA compiler
NVCC = $(CUDA_DIR)/bin/nvcc
NVCC_FLAGS = -I$(CUDA_DIR)/include -arch=sm_70 --cudart shared

# 'make dbg=1' enables NVCC debugging
ifeq ($(dbg),1)
	NVCC_FLAGS += -g -O0
else
	NVCC_FLAGS += -O2
endif

# 'make emu=1' compiles the CUDA kernels for emulation
ifeq ($(emu),1)
	NVCC_FLAGS += -deviceemu
endif

all: cluster.o getopt.o kmeans.o kmeans_clustering.o kmeans_cuda.o rmse.o

%.o: %.c
	$(CC) $(CC_FLAGS) $< -c

kmeans_cuda.o: kmeans_cuda.cu
	$(NVCC) $(NVCC_FLAGS) -c kmeans_cuda.cu

clean:
	rm -f *.o *~ kmeans_cuda.linkinfo
