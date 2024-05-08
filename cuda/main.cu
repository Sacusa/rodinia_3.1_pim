#include <chrono>
#include <cuda_runtime.h>
#include <cstdlib>
#include <iostream>
#include <mutex>
#include <thread>
#include "../../common.h"

#define MIN_ITERS 1
#define PIM_ROWS  256

class Semaphore {
    public:
        Semaphore (int count_ = 0) : count(count_) {}

        inline void notify()
        {
            mtx.lock();
            count++;
            mtx.unlock();
        }

        inline bool done()
        {
            bool retval = true;

            mtx.lock();
            if (count == 0) {
                retval = false;
            } else {
                count--;
            }
            mtx.unlock();

            return retval;
        }

private:
        std::mutex mtx;
        int count;
};

// Global state variables
int (*mem_app) (int, char**);
pim_state_t *pim_state;
cudaStream_t pim_stream;
Semaphore pim_running;

// Rodinia benchmark declarations
extern "C" int main_btree(int argc, char** argv);
int main_backprop(int argc, char** argv);
int main_bfs(int argc, char** argv);
int main_euler3d(int argc, char** argv);  // CFD
int main_dwt2d(int argc, char** argv);
int main_gaussian(int argc, char** argv);
int main_heartwall(int argc, char** argv);
int main_hotspot(int argc, char** argv);
int main_hotspot3D(int argc, char** argv);
int main_huffman(int argc, char** argv);
int main_kmeans(int argc, char** argv);
int main_lavaMD(int argc, char** argv);
extern "C" int main_leukocyte(int argc, char** argv);
int main_lud(int argc, char** argv);
int main_mummergpu(int argc, char** argv);
int main_nn(int argc, char** argv, bool is_first);
int main_nw(int argc, char** argv);
int main_pathfinder(int argc, char** argv);
int main_srad_v1(int argc, char** argv);
int main_srad_v2(int argc, char** argv);
int main_streamcluster(int argc, char** argv);

// Helper functions
void setup_mem(char*);
void setup_pim(char *kernel);
void run_mem(char*, int, char**, Semaphore*, bool, bool);
void run_pim(Semaphore*, bool);
void exec_mem_and_pim(char*, char*, int, char**);
void exec_mem_only(char*, int, char**);

int main(int argc, char **argv)
{
    if (argc < 3) {
        std::cout << "Usage: " << argv[0] << "<pim> <mem>" << std::endl;
        return -1;
    }

    char *mem_app_name = argv[2];
    char *pim_app_name = argv[1];

    if (!strcmp(pim_app_name, "nop")) {
        exec_mem_only(mem_app_name, argc, argv);
    } else {
        exec_mem_and_pim(mem_app_name, pim_app_name, argc, argv);
    }

    return 0;
}

void setup_mem(char *kernel)
{
    if (!strcmp(kernel, "b+tree")) {
        mem_app = main_btree;
    } else if (!strcmp(kernel, "backprop")) {
        mem_app = main_backprop;
    } else if (!strcmp(kernel, "bfs")) {
        mem_app = main_bfs;
    } else if (!strcmp(kernel, "cfd")) {
        mem_app = main_euler3d;
    } else if (!strcmp(kernel, "dwt2d")) {
        mem_app = main_dwt2d;
    } else if (!strcmp(kernel, "gaussian")) {
        mem_app = main_gaussian;
    } else if (!strcmp(kernel, "heartwall")) {
        mem_app = main_heartwall;
    } else if (!strcmp(kernel, "hotspot")) {
        mem_app = main_hotspot;
    } else if (!strcmp(kernel, "hotspot3D")) {
        mem_app = main_hotspot3D;
    } else if (!strcmp(kernel, "huffman")) {
        mem_app = main_huffman;
    } else if (!strcmp(kernel, "kmeans")) {
        mem_app = main_kmeans;
    } else if (!strcmp(kernel, "lavaMD")) {
        mem_app = main_lavaMD;
    } else if (!strcmp(kernel, "leukocyte")) {
        mem_app = main_leukocyte;
    } else if (!strcmp(kernel, "lud")) {
        mem_app = main_lud;
    } else if (!strcmp(kernel, "mummergpu")) {
        mem_app = main_mummergpu;
    } else if (!strcmp(kernel, "nn")) {
        // do nothing; nn needs special handling
    } else if (!strcmp(kernel, "nw")) {
        mem_app = main_nw;
    } else if (!strcmp(kernel, "pathfinder")) {
        mem_app = main_pathfinder;
    } else if (!strcmp(kernel, "srad_v1")) {
        mem_app = main_srad_v1;
    } else if (!strcmp(kernel, "srad_v2")) {
        mem_app = main_srad_v2;
    } else if (!strcmp(kernel, "streamcluster")) {
        mem_app = main_streamcluster;
    } else {
        std::cout << "Invalid MEM application: " << kernel << std::endl;
        std::exit(EXIT_FAILURE);
    }
}

void setup_pim(char *kernel)
{
    if (!strcmp(kernel, "stream_add")) {
        pim_state = init_pim(STREAM_ADD, 1048576, PIM_ROWS);
    } else if (!strcmp(kernel, "stream_copy")) {
        pim_state = init_pim(STREAM_COPY, 1048576, PIM_ROWS);
    } else if (!strcmp(kernel, "stream_daxpy")) {
        pim_state = init_pim(STREAM_DAXPY, 1048576, PIM_ROWS);
    } else if (!strcmp(kernel, "stream_scale")) {
        pim_state = init_pim(STREAM_SCALE, 1048576, PIM_ROWS);
    } else if (!strcmp(kernel, "stream_triad")) {
        pim_state = init_pim(STREAM_TRIAD, 1048576, PIM_ROWS);
    } else if (!strcmp(kernel, "bn_fwd")) {
        pim_state = init_pim(BN_FWD, 1048576, PIM_ROWS);
    } else if (!strcmp(kernel, "bn_bwd")) {
        pim_state = init_pim(BN_BWD, 1048576, PIM_ROWS);
    } else if (!strcmp(kernel, "kmeans")) {
        pim_state = init_pim(KMEANS, 1048576, 1);
    } else if (!strcmp(kernel, "histogram")) {
        pim_state = init_pim(HISTOGRAM, 1048576, 1);
    } else if (!strcmp(kernel, "fully_connected")) {
        pim_state = init_pim(FULLY_CONNECTED, 1048576, 1);
    } else if (!strcmp(kernel, "grim")) {
        pim_state = init_pim(GRIM, 1048576, 32);
    } else {
        std::cout << "Invalid PIM application: " << kernel << std::endl;
        std::exit(EXIT_FAILURE);
    }
}

void run_mem(char *kernel, int argc, char **argv, Semaphore *semaphore,
        bool is_first, bool wait_for_pim)
{
    // create a copy of argv because some benchmarks destroy the arguments
    char **argv_copy = new char*[(argc - 2) + 1];
    for (int i = 2; i < argc; i++) {
        argv_copy[i - 2] = new char[strlen(argv[i])];
        strcpy(argv_copy[i - 2], argv[i]);
    }
    argv_copy[argc - 2] = NULL;

    if (wait_for_pim) { while(!pim_running.done()); }

    if (!strcmp(kernel, "nn")) {
        main_nn(argc - 2, argv_copy, is_first);
    } else {
        mem_app(argc - 2, argv_copy);
    }

    cudaStreamSynchronize(0);
    semaphore->notify();

    // we don't need to destroy argv_copy because:
    // 1) if the benchmark modified the pointer, freeing it can cause a
    //    segfault
    // 2) the thread is being destroyed right now, so the memory will be freed
    //    anyway
}

void run_pim(Semaphore *semaphore, bool is_first)
{
    launch_pim(pim_state, pim_stream);
    if (is_first) {
        // wait for PIM to start running
        cudaStreamGetPriority(pim_stream, NULL);
        pim_running.notify();
    }
    cudaStreamSynchronize(pim_stream);
    semaphore->notify();
}

void exec_mem_and_pim(char *mem_app_name, char *pim_app_name, int argc,
        char **argv)
{
    setup_mem(mem_app_name);
    setup_pim(pim_app_name);

    cudaStreamCreate(&pim_stream);

    unsigned mem_iters = 0, pim_iters = 0;
    bool mem_running = false, pim_running = false;
    Semaphore mem_semaphore, pim_semaphore;

    while ((mem_iters < MIN_ITERS) || (pim_iters < MIN_ITERS)) {
        if (!mem_running && !pim_running) {
            std::thread (run_pim, &pim_semaphore, true).detach();
            std::thread (run_mem, mem_app_name, argc, argv, &mem_semaphore,
                    true, true).detach();

            mem_running = true;
            pim_running = true;
        }

        else if (!mem_running) {
            std::thread (run_mem, mem_app_name, argc, argv, &mem_semaphore,
                    false, false).detach();
            mem_running = true;
        }

        else if (!pim_running) {
            std::thread (run_pim, &pim_semaphore, false).detach();
            pim_running = true;
        }

        while (true) {
            if (mem_semaphore.done()) {
                mem_iters++;
                mem_running = false;
                std::cout << "<<< MEM FINISHED >>>" << std::endl;
                cudaGetErrorName(cudaSuccess);
                break;
            }

            if (pim_semaphore.done()) {
                pim_iters++;
                pim_running = false;
                std::cout << "<<< PIM FINISHED >>>" << std::endl;
                cudaGetErrorName(cudaSuccess);
                break;
            }
        }
    }

    // Kill all running kernels
    cudaDeviceReset();

    // Sleep for a second so that GPGPU-Sim can clean up
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    free_pim(pim_state);
}

void exec_mem_only(char *mem_app_name, int argc, char **argv)
{
    setup_mem(mem_app_name);

    unsigned mem_iters = 0;
    Semaphore mem_semaphore;

    while (mem_iters < MIN_ITERS) {
        std::thread (run_mem, mem_app_name, argc, argv, &mem_semaphore,
                mem_iters == 0, false).detach();

        while (!mem_semaphore.done());
        mem_iters++;
        std::cout << "<<< MEM FINISHED >>>" << std::endl;
        cudaGetErrorName(cudaSuccess);
    }

    // Kill all running kernels
    cudaDeviceReset();

    // Sleep for a second so that GPGPU-Sim can clean up
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
}
