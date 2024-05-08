include ../../common/make.config

NVCC = $(CUDA_DIR)/bin/nvcc

NVCC_FLAGS = -I$(CUDA_DIR)/include -arch=sm_70 --cudart shared

TARGET_G = sc_gpu.o

# make dbg=1 tells nvcc to add debugging symbols to the binary
ifeq ($(dbg),1)
	NVCC_FLAGS += -g -O0
else
	NVCC_FLAGS += -O3
endif

# make emu=1 compiles the CUDA kernels for emulation
ifeq ($(emu),1)
	NVCC_FLAGS += -deviceemu
endif

DEPS = streamcluster_cuda_cpu.cpp streamcluster_cuda.cu streamcluster_header.cu

all: streamcluster_cuda_cpu.o streamcluster_cuda.o streamcluster_header.o

#$(TARGET_G): $(DEPS)
#	$(NVCC) $(NVCC_FLAGS) $(DEPS) -c -o $(TARGET_G) -lcuda
%.o: %.c*
	$(NVCC) $(NVCC_FLAGS) $^ -c -o $@ -lcuda

clean:
	rm -f *.o *~ *.txt $(TARGET_G) *.linkinfo
