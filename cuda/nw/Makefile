include ../../common/make.config

CC := $(CUDA_DIR)/bin/nvcc

CC_FLAGS := -O3 -I$(INCLUDE) -L$(CUDA_LIB_DIR) -arch=sm_70 --cudart shared -c -w

INCLUDE := $(CUDA_DIR)/include

SRC = needle.cu

OBJ = needle.o

$(OBJ): $(SRC)
	$(CC) $(SRC) -o $(OBJ) $(CC_FLAGS)

clean: $(SRC)
	rm -f $(OBJ) $(OBJ).linkinfo result.txt
