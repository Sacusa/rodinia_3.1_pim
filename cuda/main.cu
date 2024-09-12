#include <cassert>
#include <chrono>
#include <cuda_runtime.h>
#include <cstdlib>
#include <iostream>
#include <thread>
#include "../../common.h"

/**
 * std::semaphore support was added in C++20 and requires CUDA 12+. We provide
 * a comparable implementation for older versions of CUDA, such as used the one
 * we use. This requires C++11 support.
 */

#if __cplusplus >= 202002L

#include <semaphore>
using Semaphore std::counting_semaphore;

#else

#include <condition_variable>
#include <mutex>

class Semaphore {
    public:
        Semaphore (unsigned count_ = 0) : count(count_) {}

        inline void acquire() {
            std::unique_lock<std::mutex> lock(mtx);
            if (count == 0) {
                cv.wait(lock, [&] { return count > 0; });
            }
            --count;
        }

        inline bool try_acquire() {
            std::unique_lock<std::mutex> lock(mtx);
            if (count == 0) {
                return false;
            } else {
                --count;
                return true;
            }
        }

        inline void release() {
            std::unique_lock<std::mutex> lock(mtx);
            ++count;
            lock.unlock();
            cv.notify_all();
        }

private:
        std::mutex mtx;
        std::condition_variable cv;
        unsigned count;
};

#endif

#define MIN_ITERS 1
#define PIM_ROWS  256
#define LLM_NUM_MEM_KERNELS 3

// Global state variables
int (*mem_app) (int, char**);
pim_state_t *pim_state;
cudaStream_t pim_stream;
Semaphore thread_finished{0};

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
void main_gemm(cudaStream_t stream, size_t M, size_t K, size_t N);

// Helper functions
void setup_mem(char*);
void setup_pim(char *kernel);
void run_mem(char*, int, char**, bool, bool, Semaphore*, Semaphore*);
void run_gemm(cudaStream_t, bool, Semaphore*, Semaphore*);
void run_pim(bool, Semaphore*, Semaphore*);
void run_pim_llm(pim_state_t*, pim_state_t*, pim_state_t*, Semaphore*,
        Semaphore*);
void exec_mem_and_pim(char*, char*, int, char**);
void exec_mem_only(char*, int, char**);
void exec_llm(bool, bool);

void print_usage(char *argv0)
{
    std::cout << "Usage: " << argv0 << "<pim> <mem>" << std::endl;
    std::cout << "       " << argv0 << " llm" << std::endl;
}

int main(int argc, char **argv)
{
    int error_code = 0;

    if (argc >= 3) {
        char *mem_app_name = argv[2];
        char *pim_app_name = argv[1];

        if (!strcmp(pim_app_name, "nop")) {
            exec_mem_only(mem_app_name, argc, argv);
        } else {
            exec_mem_and_pim(mem_app_name, pim_app_name, argc, argv);
        }
    }
    else if (argc == 2) {
        char *app_name = argv[1];

        if (!strcmp(app_name, "llm")) {
            exec_llm(true, true);
        } else if (!strcmp(app_name, "llm_mem_only")) {
            exec_llm(true, false);
        } else if (!strcmp(app_name, "llm_pim_only")) {
            exec_llm(false, true);
        } else {
            print_usage(argv[0]);
            error_code = -2;
        }
    }
    else {
        print_usage(argv[0]);
        error_code = -1;
    }

    return error_code;
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
        pim_state = init_pim(FULLY_CONNECTED, 1048576, 256);
    } else if (!strcmp(kernel, "grim")) {
        pim_state = init_pim(GRIM, 1048576, 32);
    } else {
        std::cout << "Invalid PIM application: " << kernel << std::endl;
        std::exit(EXIT_FAILURE);
    }
}

void run_mem(char *kernel, int argc, char **argv, bool wait_for_pim,
        bool is_first, Semaphore *pim_running, Semaphore *signal_mem_finished)
{
    // create a copy of argv because some benchmarks destroy the arguments
    char **argv_copy = new char*[(argc - 2) + 1];
    for (int i = 2; i < argc; i++) {
        argv_copy[i - 2] = new char[strlen(argv[i]) + 1];
        strcpy(argv_copy[i - 2], argv[i]);
    }
    argv_copy[argc - 2] = NULL;

    if (wait_for_pim) { pim_running->acquire(); }

    if (!strcmp(kernel, "nn")) {
        main_nn(argc - 2, argv_copy, is_first);
    } else {
        mem_app(argc - 2, argv_copy);
    }

    cudaStreamSynchronize(0);
    signal_mem_finished->release();
    thread_finished.release();

    // we don't need to destroy argv_copy because:
    // 1) if the benchmark modified the pointer, freeing it can cause a
    //    segfault
    // 2) the thread is being destroyed right now, so the memory will be freed
    //    anyway
}

void run_gemm(cudaStream_t stream, bool wait_for_pim,
        Semaphore *pim_running, Semaphore *signal_mem_finished)
{
    if (wait_for_pim) { pim_running->acquire(); }

    for (int i = 0; i < LLM_NUM_MEM_KERNELS; i++) {
        main_gemm(stream, 128, 4096, 4096);
        cudaStreamSynchronize(stream);
    }

    signal_mem_finished->release();
    thread_finished.release();
}

void run_pim(bool do_signal_launch, Semaphore *pim_running,
        Semaphore *signal_pim_finished)
{
    launch_pim(pim_state, pim_stream);

    if (do_signal_launch) { pim_running->release(); }

    cudaStreamSynchronize(pim_stream);
    signal_pim_finished->release();
    thread_finished.release();
}

void run_pim_llm(pim_state_t *pim_qk, pim_state_t *pim_softmax,
        pim_state_t *pim_sv, Semaphore *pim_running,
        Semaphore *signal_pim_finished)
{
    launch_pim(pim_qk,      pim_stream);
    launch_pim(pim_softmax, pim_stream);
    launch_pim(pim_sv,      pim_stream);

    pim_running->release();

    cudaStreamSynchronize(pim_stream);
    signal_pim_finished->release();
    thread_finished.release();
}

void exec_mem_and_pim(char *mem_app_name, char *pim_app_name, int argc,
        char **argv)
{
    setup_mem(mem_app_name);
    setup_pim(pim_app_name);

    cudaStreamCreateWithPriority(&pim_stream, 0, -1);

    unsigned mem_iters = 0, pim_iters = 0;
    bool mem_running = false, pim_running = false;
    Semaphore pim_launched{0}, mem_finished{0}, pim_finished{0};

    while ((mem_iters < MIN_ITERS) || (pim_iters < MIN_ITERS)) {
        if (!mem_running && !pim_running) {
            std::thread (run_pim, true, &pim_launched,
                    &pim_finished).detach();
            std::thread (run_mem, mem_app_name, argc, argv, true, true,
                    &pim_launched, &mem_finished).detach();

            mem_running = true;
            pim_running = true;
        }

        else if (!mem_running) {
            std::thread (run_mem, mem_app_name, argc, argv, false, false,
                    &pim_launched, &mem_finished).detach();
            mem_running = true;
        }

        else if (!pim_running) {
            std::thread (run_pim, false, &pim_launched,
                    &pim_finished).detach();
            pim_running = true;
        }

        thread_finished.acquire();

        if (mem_finished.try_acquire()) {
            mem_iters++;
            mem_running = false;
            std::cout << "<<< MEM FINISHED >>>" << std::endl;
            cudaGetErrorName(cudaSuccess);
        }

        else if (pim_finished.try_acquire()) {
            pim_iters++;
            pim_running = false;
            std::cout << "<<< PIM FINISHED >>>" << std::endl;
            cudaGetErrorName(cudaSuccess);
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
    Semaphore mem_finished{0};

    while (mem_iters < MIN_ITERS) {
        std::thread (run_mem, mem_app_name, argc, argv, false, mem_iters == 0,
                nullptr, &mem_finished).detach();

        thread_finished.acquire();

        mem_finished.acquire();
        mem_iters++;
        std::cout << "<<< MEM FINISHED >>>" << std::endl;
        cudaGetErrorName(cudaSuccess);
    }

    // Kill all running kernels
    cudaDeviceReset();

    // Sleep for a second so that GPGPU-Sim can clean up
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
}

void exec_llm(bool do_run_mem, bool do_run_pim)
{
    assert(do_run_mem || do_run_pim);

    pim_state_t *pim_qk, *pim_softmax, *pim_sv;
    cudaStream_t mem_stream;

    if (do_run_pim) {
        pim_qk = init_pim(FULLY_CONNECTED, 1048576, 1024);
        pim_softmax = init_pim(SOFTMAX, 1048576, 128);
        pim_sv = init_pim(FULLY_CONNECTED_128_ELEM, 1048576, 1024);

        // Higher priority stream for PIM
        cudaStreamCreateWithPriority(&pim_stream, 0, -1);
    }

    if (do_run_mem) {
        // Regular priority stream for MEM
        cudaStreamCreate(&mem_stream);
    }

    Semaphore pim_launched{0}, mem_finished{0}, pim_finished{0};

    if (do_run_pim) {
        std::thread (run_pim_llm, pim_qk, pim_softmax, pim_sv, &pim_launched,
                &pim_finished).detach();
    }

    if (do_run_mem) {
        std::thread (run_gemm, mem_stream, do_run_pim, &pim_launched,
                &mem_finished).detach();
    }

    bool pim_running = do_run_pim;
    bool mem_running = do_run_mem;

    while (pim_running || mem_running) {
        thread_finished.acquire();

        if (pim_running && pim_finished.try_acquire()) {
            pim_running = false;
            std::cout << "<<< PIM FINISHED >>>" << std::endl;
        }

        if (mem_running && mem_finished.try_acquire()) {
            mem_running = false;
            std::cout << "<<< MEM FINISHED >>>" << std::endl;
        }
    }

    // Kill all running kernels
    cudaDeviceReset();

    // Sleep for a second so that GPGPU-Sim can clean up
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));

    if (do_run_pim) {
        free_pim(pim_qk);
        free_pim(pim_softmax);
        free_pim(pim_sv);
    }
}
