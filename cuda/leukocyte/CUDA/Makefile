include ../../../common/make.config

ifdef OUTPUT
override OUTPUT = -DOUTPUT
endif

# C compiler
CC = nvcc -ccbin gcc
CC_FLAGS = -O3 -I$(MATRIX_DIR) -I$(CUDA_DIR)/include -lstdc++

# CUDA compiler
NVCC = $(CUDA_DIR)/bin/nvcc
NVCC_FLAGS = -I$(CUDA_DIR)/include -I$(SDK_DIR)/common/inc -arch=sm_70 --cudart shared

# Matrix library path
MATRIX_DIR = ../meschach_lib

# 'make dbg=1' enables NVCC debugging
ifeq ($(dbg),1)
	NVCC_FLAGS += -g -O0
else
	NVCC_FLAGS += -O3
endif

# 'make emu=1' compiles the CUDA kernels for emulation
ifeq ($(emu),1)
	NVCC_FLAGS += -deviceemu
endif

all: detect_main.o avilib.o find_ellipse.o find_ellipse_kernel.o track_ellipse.o track_ellipse_kernel.o misc_math.o $(MATRIX_DIR)/meschach.a

%.o: %.c
	$(CC)  $(OUTPUT) $(CC_FLAGS) $< -c

detect_main.o: detect_main.c find_ellipse.h track_ellipse.h avilib.h
	$(CC) $(CC_FLAGS) detect_main.c -c

find_ellipse_kernel.o: find_ellipse_kernel.cu find_ellipse_kernel.h
	$(NVCC) $(NVCC_FLAGS) -c find_ellipse_kernel.cu

track_ellipse_kernel.o: track_ellipse_kernel.cu track_ellipse_kernel.h
	$(NVCC) $(NVCC_FLAGS) -I$(MATRIX_DIR) -c track_ellipse_kernel.cu

find_ellipse.o: avilib.h

track_ellipse.o: find_ellipse.h avilib.h

$(MATRIX_DIR)/meschach.a:
	cd $(MATRIX_DIR); ./configure --with-all; make all; make clean

clean:
	rm -f *.o *~ leukocyte *.linkinfo
