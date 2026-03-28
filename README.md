# Password Security Analysis and Guessing Simulation Tool

This project simulates password-guessing behavior for authorized security testing and education.
It is not a real cracking tool and intentionally uses controlled limits.

## Files

- main.cpp
- simulation.cpp, simulation.h
- parallel_openmp.cpp, parallel_openmp.h
- parallel_mpi.cpp, parallel_mpi.h
- gpu_kernel.cu, gpu_kernel.cpp, gpu_kernel.h
- utils.cpp, utils.h

## Simulation Flow (Smart Ordering)

1. Common passwords first
2. Dictionary words
3. Pattern-based variants
4. Word combinations
5. Controlled brute-force (max generation length capped to 5)

## Terminal UI

The simulator now includes a cleaner, menu-driven terminal UI:

1. Guided setup form with input validation for:
   - target password
   - optional wordlist path
   - max length
   - charset
   - brute-force candidate limit
   - candidate mode (proposal vs smart)
2. Execution menu:
   - Run all
   - Sequential only
   - OpenMP only
   - MPI only
   - CUDA only
3. Comparison dashboard showing:
   - found/not found status
   - guesses tried
   - elapsed time
   - speedup vs sequential
   - best-time marker

## Desktop GUI (Window App)

If you want a window-based GUI instead of terminal prompts, use `gui_app.py`.

### Run Steps

1. Build the simulator executable first:

```bash
C:\msys64\ucrt64\bin\g++.exe -std=c++17 -O2 main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cpp -o password_sim.exe
```

2. Launch the GUI:

```bash
python gui_app.py
```

### GUI Features

- Form-based input for all simulator settings
- Wordlist file picker
- Mode selection dropdown (all/sequential/OpenMP/MPI/CUDA)
- Run button that executes `password_sim.exe` in the background
- Scrollable output panel with full simulator report

## Build on Windows

### 1) MinGW / g++ (Sequential + optional OpenMP)

```bash
g++ -std=c++17 -O2 main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cpp -o password_sim
```

Enable OpenMP:

```bash
g++ -std=c++17 -O2 -fopenmp main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cpp -o password_sim
```

### 2) MPI build (MS-MPI/OpenMPI toolchain)

Compile with your MPI compiler wrapper and define USE_MPI:

```bash
mpicxx -std=c++17 -O2 -DUSE_MPI main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cpp -o password_sim_mpi
```

Run (example with 4 processes):

```bash
mpiexec -n 4 password_sim_mpi
```

### 3) CUDA build

Compile with NVCC and define USE_CUDA.
Use gpu_kernel.cu (not gpu_kernel.cpp) in this mode.

```bash
nvcc -std=c++17 -O2 -DUSE_CUDA main.cpp simulation.cpp utils.cpp parallel_openmp.cpp parallel_mpi.cpp gpu_kernel.cu -o password_sim_cuda
```

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
