include ../../common/make.config

CC := $(CUDA_DIR)/bin/nvcc

CC_FLAGS := -O3 -arch=sm_70 --cudart shared

all : nn.o

clean :
	rm -rf *.o nn

nn.o : nn_cuda.cu
	$(CC) $(CC_FLAGS) -c -o nn.o nn_cuda.cu
