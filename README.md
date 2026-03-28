<<<<<<< HEAD
# Password Security Analysis and Guessing Simulation Tool (Safe Educational Version)

This project simulates password-guessing behavior for **authorized security testing and education**.
It is not a real cracking tool and intentionally uses controlled limits.

## Files

- `main.cpp`
- `simulation.cpp`, `simulation.h`
- `parallel_openmp.cpp`, `parallel_openmp.h`
- `parallel_mpi.cpp`, `parallel_mpi.h`
- `gpu_kernel.cu`, `gpu_kernel.cpp`, `gpu_kernel.h`
- `utils.cpp`, `utils.h`

## Simulation Flow (Smart Ordering)

1. Common passwords first
2. Dictionary words
3. Pattern-based variants
4. Word combinations
5. Controlled brute force (max length capped to 5)

## Interactive Benchmark UI (Console)

The app provides an interactive console UI so you can test and compare all modes from one place:

1. Enter target password and search settings.
2. Choose candidate mode:
	- Proposal Mode: pure brute-force candidate space (for stage-wise baseline comparison)
	- Smart Mode: common + dictionary + patterns + combinations + brute-force
3. Select execution mode:
	- Sequential
	- OpenMP
	- MPI
	- CUDA
	- Run all
4. Review the built-in comparison dashboard table showing:
	- found/not found status
	- guesses tried
	- elapsed time
	- speedup vs sequential baseline

## Build on Windows

## 1) MinGW / g++ (Sequential + optional OpenMP)

```bash
g++ -std=c++17 -O2 main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cpp -o password_sim
```

Enable OpenMP:

```bash
g++ -std=c++17 -O2 -fopenmp main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cpp -o password_sim
```

## 2) MPI build (MS-MPI/OpenMPI toolchain)

Compile with your MPI compiler wrapper and define `USE_MPI`:

```bash
mpicxx -std=c++17 -O2 -DUSE_MPI main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cpp -o password_sim_mpi
```

Run (example with 4 processes):

```bash
mpiexec -n 4 password_sim_mpi
```

## 3) CUDA build

Compile with NVCC and define `USE_CUDA`.
Use `gpu_kernel.cu` (not `gpu_kernel.cpp`) in this mode.

```bash
nvcc -std=c++17 -O2 -DUSE_CUDA main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cu -o password_sim_cuda
```

## 4) Visual Studio

- Add `.cpp` files to project.
- For OpenMP: enable **C/C++ > Language > OpenMP Support**.
- For MPI: add MPI include/libs and set `USE_MPI` in preprocessor definitions.
- For CUDA: add CUDA build customization, include `gpu_kernel.cu`, and set `USE_CUDA`.

## Output Metrics

Each mode reports:

- Match status (simulation)
- Guesses tried
- Time (seconds)
- Guesses per second
- Speedup vs sequential baseline

## Safety Notes

- Educational and authorized usage only.
- Controlled brute-force limit is intentionally applied.
- No networking, no privilege bypass, no exploit logic.
=======
# Parallel-Password-Cracker-Simulator
>>>>>>> e21644c719718cf52926ecf816f283260f84a253
