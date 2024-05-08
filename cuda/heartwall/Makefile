
ifdef OUTPUT
override OUTPUT = -DOUTPUT
endif

# link objects(binaries) together
all: main.o ./AVI/avilib.o ./AVI/avimod.o

# compile main function file into object (binary)
main.o: main.cu kernel.cu define.c
	nvcc $(OUTPUT) $(KERNEL_DIM) main.cu -I./AVI -c -O3 -arch=sm_70

./AVI/avilib.o ./AVI/avimod.o:
	cd AVI; make;

# delete all object files
clean:
	rm -f *.o AVI/*.o *.linkinfo
