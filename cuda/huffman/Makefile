include ../../common/make.config

NVCC=$(CUDA_DIR)/bin/nvcc
CC = g++

CUDA_INCLUDEPATH=$(CUDA_DIR)/include

NVCC_OPTS=-O3 -arch=sm_70 --cudart shared -Xcompiler -m64 -w

GCC_OPTS=-O3 -m64 -w

OBJ = main_test_cu.o stats_logger.o vlc_kernel_sm64huff.o scan.o pack_kernels.o cpuencode.o
SRC = main_test_cu.cu
EXE = pavle

ifdef TESTING
override TESTING = -DTESTING
endif

ifdef CACHECWLUT
override TESTING = -DCACHECWLUT
endif

all: $(OBJ)

vlc_kernel_sm64huff.o: vlc_kernel_sm64huff.cu
	$(NVCC) $(TESTING) -c vlc_kernel_sm64huff.cu $(NVCC_OPTS)

scan.o: scan.cu
	$(NVCC) -c scan.cu $(NVCC_OPTS)

#cpuencode.o: cpuencode.cu
#	$(NVCC) -c $(NVCC_OPTS) cpuencode.cu

pack_kernels.o: pack_kernels.cu
	$(NVCC) -c pack_kernels.cu $(NVCC_OPTS)

main_test_cu.o: main_test_cu.cu cutil.h
	$(NVCC) $(TESTING) -c main_test_cu.cu $(NVCC_OPTS) -I $(CUDA_INCLUDEPATH)

.o:.cpp
	$(CC) ++ $(GCC_OPTS) -c $@ -o $<

clean:
	rm -f *.o $(EXE)
