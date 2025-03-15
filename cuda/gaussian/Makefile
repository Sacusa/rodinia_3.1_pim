include ../../common/make.config

INCLUDE := $(CUDA_DIR)/include

CC := $(CUDA_DIR)/bin/nvcc
CC_FLAGS=-I$(INCLUDE) -L$(CUDA_LIB_DIR) -arch=sm_75 --cudart shared -O3

SRC = gaussian.cu
OBJ = gaussian.o
EXE = gaussian

objects: $(SRC)
	$(CC) $(KERNEL_DIM) $(SRC) -c -w -o $(OBJ) $(CC_FLAGS)

release: $(SRC)
	$(CC) $(KERNEL_DIM) $(SRC) -w -o $(EXE) -I$(INCLUDE) -L$(CUDA_LIB_DIR)

clean:
	rm -f gaussian gaussian.o
