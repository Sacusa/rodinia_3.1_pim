include ../../common/make.config

INCLUDE := $(CUDA_DIR)/include

CC := $(CUDA_DIR)/bin/nvcc
CC_FLAGS=-O3 -I$(INCLUDE) -L$(CUDA_LIB_DIR) -arch=sm_70 --cudart shared -w

SRC = bfs.cu

OBJ = bfs.o
EXE = bfs

object: $(SRC)
	$(CC) $(SRC) -c -o $(OBJ) $(CC_FLAGS)

release: $(SRC)
	$(CC) $(SRC) -o $(EXE) -I$(INCLUDE) -L$(CUDA_LIB_DIR)

enum: $(SRC)
	$(CC) -deviceemu $(SRC) -o $(EXE) -I$(INCLUDE) -L$(CUDA_LIB_DIR)

debug: $(SRC)
	$(CC) -g $(SRC) -o $(EXE) -I$(INCLUDE) -L$(CUDA_LIB_DIR)

debugenum: $(SRC)
	$(CC) -g -deviceemu $(SRC) -o $(EXE) -I$(INCLUDE) -L$(CUDA_LIB_DIR)

clean: $(SRC)
	rm -f $(EXE) $(OBJ) $(EXE).linkinfo result.txt
