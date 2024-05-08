include ../../common/make.config

CC := $(CUDA_DIR)/bin/nvcc

CC_FLAGS=-O3 -I$(INCLUDE) -L$(CUDA_LIB_DIR) -arch=sm_70 --cudart shared -c

INCLUDE := $(CUDA_DIR)/include

SRC = 3D.cu

EXE = 3D.o

$(EXE): $(SRC)
	$(CC) $(KERNEL_DIM) $(SRC) -o $(EXE) $(CC_FLAGS)

clean: $(SRC)
	rm -f $(EXE) $(EXE).linkinfo result.txt
