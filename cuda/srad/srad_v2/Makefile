include ../../../common/make.config

CC := $(CUDA_DIR)/bin/nvcc

CC_FLAGS := -O3 -I$(INCLUDE) -L$(CUDA_LIB_DIR) -arch=sm_70 --cudart shared

INCLUDE := $(CUDA_DIR)/include

SRC = srad.cu

OBJ = srad.o

$(OBJ): $(SRC)
	$(CC) $(SRC) -c -o $(OBJ) $(CC_FLAGS)

clean: $(SRC)
	rm -f $(OBJ) $(OBJ).linkinfo result.txt
