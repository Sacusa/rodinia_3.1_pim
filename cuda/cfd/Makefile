include ../../common/make.config

CUDA_SDK_PATH := $(SDK_DIR)

# Determine the correct version of the cutil library
CUTIL_LIB = # -lcutil
ifeq ($(shell uname -m), x86_64)
     ifeq ($(shell if test -e $(SDK_DIR)/lib/libcutil_x86_64.a; then echo T; else echo F; fi), T)
        CUTIL_LIB = #-lcutil_x86_64
     endif
endif

NVCC_FLAGS=--gpu-architecture=compute_70 --gpu-code=compute_70 -I$(CUDA_SDK_PATH)/common/inc -L$(CUDA_SDK_PATH)/common/lib $(CUTIL_LIB) --cudart shared -c

all: euler3d.o euler3d_double.o pre_euler3d.o pre_euler3d_double.o

%.o: %.cu
	nvcc -O3 $(NVCC_FLAGS) $^ -o $@

clean:
	rm -f *.o *.linkinfo
