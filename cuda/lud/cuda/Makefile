CC = gcc
NVCC = nvcc

DEFS += \
		-DGPU_TIMER

NVCCFLAGS += -I../common \
			 -O3 \
			 -use_fast_math \
			 -arch=sm_70 \
			 -lm \
			 --cudart shared \
			 -w

# Add source files here
EXECUTABLE  := lud_cuda
# Cuda source files (compiled with cudacc)
CUFILES     := lud_kernel.cu
# C/C++ source files (compiled with gcc / c++)
CCFILES     := lud.c lud_cuda.c ../common/common.c

OBJS = ../common/common.o lud.o lud_kernel.o

.PHONY: all clean
all : $(OBJS)

.c.o :
	$(NVCC) $(KERNEL_DIM) $(NVCCFLAGS) $(DEFS) -o $@ -c $<

%.o:	%.cu
	$(NVCC) $(KERNEL_DIM) $(NVCCFLAGS) $(DEFS) -o $@ -c $<

clean:
	rm -f $(EXECUTABLE) $(OBJS) *.linkinfo
