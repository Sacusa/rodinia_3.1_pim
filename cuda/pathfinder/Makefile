include ../../common/make.config

CC := $(CUDA_DIR)/bin/nvcc
INCLUDE := $(CUDA_DIR)/include

CC_FLAGS := -O3 -I$(INCLUDE) -L$(CUDA_LIB_DIR) -arch=sm_70 --cudart shared -w

SRC = pathfinder.cu

OBJ = pathfinder.o

$(OBJ): $(SRC)
	$(CC) $(SRC) -c -o $(OBJ) $(CC_FLAGS)

clean:
	rm -f $(OBJ)
