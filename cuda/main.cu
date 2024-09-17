#include <cassert>
#include <chrono>
#include <cuda_runtime.h>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <thread>
#include <vector>
#include "../../common.h"

/**
 * std::barrier and std::semaphore support was added in C++20 and requires
 * CUDA 12+. We provide comparable implementations for older versions of CUDA,
 * such as used the one we use. This requires C++11 support.
 */

#if __cplusplus >= 202002L

#include <barrier>
#include <semaphore>
using Barrier = std::barrier;
using Semaphore = std::counting_semaphore;

#else

#include <condition_variable>
#include <mutex>

class Barrier {
    public:
        Barrier (unsigned expected_ = 0) : expected(expected_) {}

        inline void arrive_and_wait() {
            std::unique_lock<std::mutex> lock(mtx);
            --expected;
            if (expected == 0) {
                lock.unlock();
                cv.notify_all();
            } else {
                cv.wait(lock, [&] { return expected == 0; });
            }
        }

    private:
        std::mutex mtx;
        std::condition_variable cv;
        unsigned expected;
};

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
#define PIM_SMS   8  // maximum number of SMs apportioned for PIM kernels
#define LLM_NUM_MEM_KERNELS 3

enum ExecMode {
    MEM_ONLY = 0,
    PIM_ONLY,
    MEM_AND_MEM,
    PIM_AND_MEM,
    LLM,
    LLM_MEM_ONLY,
    LLM_PIM_ONLY,
    NUM_EXEC_MODES
};

std::vector<std::string> exec_mode_str {
    "MEM only",
    "PIM only",
    "MEM and MEM",
    "PIM and MEM",
    "LLM",
    "LLM (MEM only)",
    "LLM (PIM only)"
};

// Global state variables
int (*mem_app[2]) (int, char**);
cudaStream_t mem1_stream;

pim_state_t *pim_state;
cudaStream_t pim_stream;

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
int main_kmeans(int argc, char** argv, cudaStream_t stream);
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
char **parse_arguments(char *args, int &argc);
void setup_mem(char*, int);
void setup_pim(char *kernel);
void run_mem(int, char*, int, char**, bool, bool, bool, Barrier*, Semaphore*,
        Semaphore*, Semaphore*, Semaphore*);
void run_gemm(cudaStream_t, bool, Barrier*, Semaphore*, Semaphore*,
        Semaphore*);
void run_pim(bool, Barrier*, Semaphore*, Semaphore*, Semaphore*);
void run_pim_llm(pim_state_t*, pim_state_t*, pim_state_t*, Barrier*,
        Semaphore*, Semaphore*, Semaphore*);
void exec_mem_only(int, char**);
void exec_pim_only(int, char**);
void exec_mem_and_mem(int, char**, int, char**);
void exec_pim_and_mem(int, char**, int, char**);
void exec_llm(bool, bool);

void print_usage(char *argv0)
{
    std::cout << "Usage: " << argv0 << \
        " <mode> \"[pim/mem1 [args]]\" \"[mem/mem2 [args]]\"" << std::endl;
    std::cout << std::endl;

    std::cout << "Modes:" << std::endl;

    for (int exec_mode_iter = 0; exec_mode_iter != NUM_EXEC_MODES;
            exec_mode_iter++) {
        std::cout << exec_mode_iter << "\t" << \
            exec_mode_str[exec_mode_iter] << std::endl;
    }
}

int main(int argc, char **argv)
{
    enum args_positions {
        BIN = 0,
        MODE,
        APP1,
        APP2,
        NUM_ARGS
    };

    int error_code = EXIT_SUCCESS;

    if (argc <= MODE) {
        print_usage(argv[BIN]);
        error_code = EXIT_FAILURE;
    }

    else {
        int exec_mode_int = std::atoi(argv[MODE]);

        if (exec_mode_int >= NUM_EXEC_MODES) {
            print_usage(argv[BIN]);
            error_code = EXIT_FAILURE;
        }

        ExecMode exec_mode = static_cast<ExecMode>(exec_mode_int);

        if (exec_mode == MEM_ONLY) {
            if (argc != (APP1 + 1)) {
                print_usage(argv[BIN]);
                error_code = EXIT_FAILURE;
            } else {
                int mem_argc = 0;
                char **mem_argv = parse_arguments(argv[APP1], mem_argc);

                exec_mem_only(mem_argc, mem_argv);
            }
        }

        else if (exec_mode == PIM_ONLY) {
            if (argc != (APP1 + 1)) {
                print_usage(argv[BIN]);
                error_code = EXIT_FAILURE;
            } else {
                int pim_argc = 0;
                char **pim_argv = parse_arguments(argv[APP1], pim_argc);

                exec_pim_only(pim_argc, pim_argv);
            }
        }

        else if (exec_mode == MEM_AND_MEM) {
            if (argc != (APP2 + 1)) {
                print_usage(argv[BIN]);
                error_code = EXIT_FAILURE;
            } else {
                int mem1_argc = 0;
                char **mem1_argv = parse_arguments(argv[APP1], mem1_argc);

                int mem2_argc = 0;
                char **mem2_argv = parse_arguments(argv[APP2], mem2_argc);

                exec_mem_and_mem(mem1_argc, mem1_argv, mem2_argc, mem2_argv);
            }
        }

        else if (exec_mode == PIM_AND_MEM) {
            if (argc != (APP2 + 1)) {
                print_usage(argv[BIN]);
                error_code = EXIT_FAILURE;
            } else {
                int pim_argc = 0;
                char **pim_argv = parse_arguments(argv[APP1], pim_argc);

                int mem_argc = 0;
                char **mem_argv = parse_arguments(argv[APP2], mem_argc);

                exec_pim_and_mem(pim_argc, pim_argv, mem_argc, mem_argv);
            }
        }

        else if (exec_mode == LLM) {
            if (argc != (MODE + 1)) {
                print_usage(argv[BIN]);
                error_code = EXIT_FAILURE;
            } else {
                exec_llm(true, true);
            }
        }

        else if (exec_mode == LLM_MEM_ONLY) {
            if (argc != (MODE + 1)) {
                print_usage(argv[BIN]);
                error_code = EXIT_FAILURE;
            } else {
                exec_llm(true, false);
            }
        }

        else if (exec_mode == LLM_PIM_ONLY) {
            if (argc != (MODE + 1)) {
                print_usage(argv[BIN]);
                error_code = EXIT_FAILURE;
            } else {
                exec_llm(false, true);
            }
        }

        else {
            // Should not reach here
            std::cout << "Unknown mode " << exec_mode << std::endl;
            error_code = EXIT_FAILURE;
        }
    }

    return error_code;
}

/**
 * This function converts a string with an application name and associated
 * arguments into a C-style argv array. It also returns argc using the second
 * argument.
 */
char **parse_arguments(char *args, int &argc)
{
    std::string args_str(args);
    std::istringstream args_tokens(args_str);
    std::vector<char*> args_vector;

    argc = 0;

    // Stream the argument tokens into a char* vector
    std::string token;
    while (getline(args_tokens, token, ' ')) {
        size_t token_size = token.size();

        char *arg = (char*) malloc(sizeof(char) * (token_size + 1));
        token.copy(arg, token_size);
        arg[token_size] = '\0';

        args_vector.push_back(arg);
        argc++;
    }

    assert(argc > 0);  // at least the application name should be there

    char **argv = (char**) malloc(sizeof(char*) * (argc + 1));
    std::copy(args_vector.begin(), args_vector.end(), argv);
    argv[argc] = NULL;

    return argv;
}

void setup_mem(char *kernel, int index)
{
    if (!strcmp(kernel, "b+tree")) {
        mem_app[index] = main_btree;
    } else if (!strcmp(kernel, "backprop")) {
        mem_app[index] = main_backprop;
    } else if (!strcmp(kernel, "bfs")) {
        mem_app[index] = main_bfs;
    } else if (!strcmp(kernel, "cfd")) {
        mem_app[index] = main_euler3d;
    } else if (!strcmp(kernel, "dwt2d")) {
        mem_app[index] = main_dwt2d;
    } else if (!strcmp(kernel, "gaussian")) {
        mem_app[index] = main_gaussian;
    } else if (!strcmp(kernel, "heartwall")) {
        mem_app[index] = main_heartwall;
    } else if (!strcmp(kernel, "hotspot")) {
        mem_app[index] = main_hotspot;
    } else if (!strcmp(kernel, "hotspot3D")) {
        mem_app[index] = main_hotspot3D;
    } else if (!strcmp(kernel, "huffman")) {
        mem_app[index] = main_huffman;
    } else if (!strcmp(kernel, "kmeans")) {
        // do nothing; kmeans needs a stream argument
    } else if (!strcmp(kernel, "lavaMD")) {
        mem_app[index] = main_lavaMD;
    } else if (!strcmp(kernel, "leukocyte")) {
        mem_app[index] = main_leukocyte;
    } else if (!strcmp(kernel, "lud")) {
        mem_app[index] = main_lud;
    } else if (!strcmp(kernel, "mummergpu")) {
        mem_app[index] = main_mummergpu;
    } else if (!strcmp(kernel, "nn")) {
        // do nothing; nn needs special handling
    } else if (!strcmp(kernel, "nw")) {
        mem_app[index] = main_nw;
    } else if (!strcmp(kernel, "pathfinder")) {
        mem_app[index] = main_pathfinder;
    } else if (!strcmp(kernel, "srad_v1")) {
        mem_app[index] = main_srad_v1;
    } else if (!strcmp(kernel, "srad_v2")) {
        mem_app[index] = main_srad_v2;
    } else if (!strcmp(kernel, "streamcluster")) {
        mem_app[index] = main_streamcluster;
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

void run_mem(int mem_app_index, char *kernel, int argc, char **argv,
        bool is_first, bool do_wait_to_launch, bool do_signal_launch,
        Barrier *all_threads_ready_barrier, Semaphore *signal_mem_start,
        Semaphore *mem_running, Semaphore *thread_finished,
        Semaphore *signal_mem_finished)
{
    // create a copy of argv because some benchmarks destroy the arguments
    char **argv_copy = new char*[argc + 1];
    for (int i = 0; i < argc; i++) {
        argv_copy[i] = new char[strlen(argv[i]) + 1];
        strcpy(argv_copy[i], argv[i]);
    }
    argv_copy[argc] = NULL;

    // ensure all threads start at the same time
    if (is_first) { all_threads_ready_barrier->arrive_and_wait(); }

    if (do_wait_to_launch) { signal_mem_start->acquire(); }
    if (do_signal_launch)  { mem_running->release(); }

    cudaStream_t stream;
    switch (mem_app_index) {
        case 0:
            stream = 0;  // default stream
            break;
        case 1:
            stream = mem1_stream;
            break;
        default:
            std::cout << "Invalid mem app index" << std::endl;
            exit(EXIT_FAILURE);
    }

    // Only kmeans uses the passed stream object for now. This can be changed
    // but it will take time.
    if (!strcmp(kernel, "kmeans")) {
        main_kmeans(argc, argv_copy, stream);
    } else if (!strcmp(kernel, "nn")) {
        main_nn(argc, argv_copy, is_first);
    } else {
        mem_app[mem_app_index](argc, argv_copy);
    }

    cudaStreamSynchronize(stream);
    signal_mem_finished->release();
    thread_finished->release();

    // we don't need to destroy argv_copy because:
    // 1) if the benchmark modified the pointer, freeing it can cause a
    //    segfault
    // 2) the thread is being destroyed right now, so the memory will be freed
    //    anyway
}

void run_gemm(cudaStream_t stream, bool wait_for_pim,
        Barrier *all_threads_ready_barrier, Semaphore *pim_running,
        Semaphore *thread_finished, Semaphore *signal_mem_finished)
{
    all_threads_ready_barrier->arrive_and_wait();

    if (wait_for_pim) { pim_running->acquire(); }

    for (int i = 0; i < LLM_NUM_MEM_KERNELS; i++) {
        main_gemm(stream, 128, 4096, 4096);
        cudaStreamSynchronize(stream);
    }

    signal_mem_finished->release();
    thread_finished->release();
}

void run_pim(bool is_first, Barrier *all_threads_ready_barrier,
        Semaphore *pim_running, Semaphore *thread_finished,
        Semaphore *signal_pim_finished)
{
    if (is_first) { all_threads_ready_barrier->arrive_and_wait(); }

    launch_pim(pim_state, pim_stream);

    if (is_first) { pim_running->release(); }

    cudaStreamSynchronize(pim_stream);
    signal_pim_finished->release();
    thread_finished->release();
}

void run_pim_llm(pim_state_t *pim_qk, pim_state_t *pim_softmax,
        pim_state_t *pim_sv, Barrier *all_threads_ready_barrier,
        Semaphore *pim_running, Semaphore *thread_finished,
        Semaphore *signal_pim_finished)
{
    all_threads_ready_barrier->arrive_and_wait();

    launch_pim(pim_qk,      pim_stream);
    launch_pim(pim_softmax, pim_stream);
    launch_pim(pim_sv,      pim_stream);

    pim_running->release();

    cudaStreamSynchronize(pim_stream);
    signal_pim_finished->release();
    thread_finished->release();
}

void exec_mem_only(int argc, char **argv)
{
    char *mem_app_name = argv[0];
    setup_mem(mem_app_name, 0);

    unsigned mem_iters = 0;
    Semaphore thread_finished{0}, mem_finished{0};
    Barrier all_threads_ready_barrier(1);

    while (mem_iters < MIN_ITERS) {
        std::thread (run_mem, 0, mem_app_name, argc, argv, mem_iters == 0,
                false, false, &all_threads_ready_barrier, nullptr, nullptr,
                &thread_finished, &mem_finished).detach();

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

void exec_pim_only(int argc, char **argv)
{
    char *pim_app_name = argv[0];
    setup_pim(pim_app_name);

    unsigned pim_iters = 0;
    Semaphore pim_launched{0}, thread_finished{0}, pim_finished{0};
    Barrier all_threads_ready_barrier(1);

    while (pim_iters < MIN_ITERS) {
        std::thread (run_pim, false, &all_threads_ready_barrier,
                &pim_launched, &thread_finished, &pim_finished).detach();

        thread_finished.acquire();

        pim_finished.acquire();
        pim_iters++;
        std::cout << "<<< PIM FINISHED >>>" << std::endl;
        cudaGetErrorName(cudaSuccess);
    }

    // Kill all running kernels
    cudaDeviceReset();

    // Sleep for a second so that GPGPU-Sim can clean up
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
}

void exec_mem_and_mem(int mem1_argc, char **mem1_argv, int mem2_argc,
        char **mem2_argv)
{
    char *mem1_app_name = mem1_argv[0];
    char *mem2_app_name = mem2_argv[0];
    setup_mem(mem1_app_name, 0);
    setup_mem(mem2_app_name, 1);

    cudaStreamCreateWithPriority(&mem1_stream, PIM_SMS, -1);

    unsigned mem1_iters = 0, mem2_iters = 0;
    bool mem1_running = false, mem2_running = false;
    Semaphore mem1_launched{0}, thread_finished{0}, mem1_finished{0},
              mem2_finished{0};
    Barrier all_threads_ready_barrier(2);

    while ((mem1_iters < MIN_ITERS) || (mem2_iters < MIN_ITERS)) {
        if (!mem1_running && !mem2_running) {
            std::thread (run_mem, 0, mem1_app_name, mem1_argc, mem1_argv, true,
                    false, true, &all_threads_ready_barrier, nullptr,
                    &mem1_launched, &thread_finished, &mem1_finished).detach();
            std::thread (run_mem, 1, mem2_app_name, mem2_argc, mem2_argv, true,
                    true, false, &all_threads_ready_barrier, &mem1_launched,
                    nullptr, &thread_finished, &mem2_finished).detach();

            mem1_running = true;
            mem2_running = true;
        }

        else if (!mem1_running) {
            std::thread (run_mem, 0, mem1_app_name, mem1_argc, mem1_argv,
                    false, false, false, &all_threads_ready_barrier, nullptr,
                    &mem1_launched, &thread_finished, &mem1_finished).detach();
            mem1_running = true;
        }

        else if (!mem2_running) {
            std::thread (run_mem, 1, mem2_app_name, mem2_argc, mem2_argv,
                    false, false, false, &all_threads_ready_barrier,
                    &mem1_launched, nullptr, &thread_finished,
                    &mem2_finished).detach();
            mem2_running = true;
        }

        thread_finished.acquire();

        if (mem1_finished.try_acquire()) {
            mem1_iters++;
            mem1_running = false;
            std::cout << "<<< MEM1 FINISHED >>>" << std::endl;
            cudaGetErrorName(cudaSuccess);
        }

        else if (mem2_finished.try_acquire()) {
            mem2_iters++;
            mem2_running = false;
            std::cout << "<<< MEM2 FINISHED >>>" << std::endl;
            cudaGetErrorName(cudaSuccess);
        }
    }

    // Kill all running kernels
    cudaDeviceReset();

    // Sleep for a second so that GPGPU-Sim can clean up
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
}

void exec_pim_and_mem(int pim_argc, char **pim_argv, int mem_argc,
        char **mem_argv)
{
    char *pim_app_name = pim_argv[0];
    char *mem_app_name = mem_argv[0];
    setup_mem(mem_app_name, 0);
    setup_pim(pim_app_name);

    cudaStreamCreateWithPriority(&pim_stream, 0, -1);

    unsigned mem_iters = 0, pim_iters = 0;
    bool mem_running = false, pim_running = false;
    Semaphore pim_launched{0}, thread_finished{0}, mem_finished{0},
              pim_finished{0};
    Barrier all_threads_ready_barrier(2);

    while ((mem_iters < MIN_ITERS) || (pim_iters < MIN_ITERS)) {
        if (!mem_running && !pim_running) {
            std::thread (run_pim, true, &all_threads_ready_barrier,
                    &pim_launched, &thread_finished, &pim_finished).detach();
            std::thread (run_mem, 0, mem_app_name, mem_argc, mem_argv, true,
                    true, false, &all_threads_ready_barrier, &pim_launched,
                    nullptr, &thread_finished, &mem_finished).detach();

            mem_running = true;
            pim_running = true;
        }

        else if (!mem_running) {
            std::thread (run_mem, 0, mem_app_name, mem_argc, mem_argv, false,
                    false, false, &all_threads_ready_barrier, &pim_launched,
                    nullptr, &thread_finished, &mem_finished).detach();
            mem_running = true;
        }

        else if (!pim_running) {
            std::thread (run_pim, false, &all_threads_ready_barrier,
                    &pim_launched, &thread_finished, &pim_finished).detach();
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

    Semaphore pim_launched{0}, thread_finished{0}, mem_finished{0},
              pim_finished{0};
    Barrier all_threads_ready_barrier(((do_run_pim && do_run_mem) ? 2 : 1));

    if (do_run_pim) {
        std::thread (run_pim_llm, pim_qk, pim_softmax, pim_sv,
                &all_threads_ready_barrier, &pim_launched, &thread_finished,
                &pim_finished).detach();
    }

    if (do_run_mem) {
        std::thread (run_gemm, mem_stream, do_run_pim,
                &all_threads_ready_barrier, &pim_launched, &thread_finished,
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
