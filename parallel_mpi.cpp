#include "parallel_mpi.h"

#include <algorithm>
#include <chrono>
#include <cstdint>

#ifdef USE_MPI
#include <mpi.h>
#endif

SimulationResult runMPISimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword,
    int argc,
    char** argv
) {
    SimulationResult result;

#ifdef USE_MPI
    MPI_Init(&argc, &argv);

    int rank = 0;
    int worldSize = 1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &worldSize);

    const std::size_t total = candidates.size();
    const std::size_t chunk = (total + static_cast<std::size_t>(worldSize) - 1) / static_cast<std::size_t>(worldSize);
    const std::size_t startIdx = static_cast<std::size_t>(rank) * chunk;
    const std::size_t endIdx = std::min(total, startIdx + chunk);

    const auto start = std::chrono::high_resolution_clock::now();

    std::uint64_t localFound = UINT64_MAX;
    for (std::size_t i = startIdx; i < endIdx; ++i) {
        if (candidates[i] == targetPassword) {
            localFound = static_cast<std::uint64_t>(i);
            break;
        }
    }

    std::uint64_t globalFound = UINT64_MAX;
    MPI_Allreduce(&localFound, &globalFound, 1, MPI_UINT64_T, MPI_MIN, MPI_COMM_WORLD);

    const auto end = std::chrono::high_resolution_clock::now();
    const double localElapsed = std::chrono::duration<double>(end - start).count();

    double maxElapsed = 0.0;
    MPI_Reduce(&localElapsed, &maxElapsed, 1, MPI_DOUBLE, MPI_MAX, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        result.elapsedSeconds = maxElapsed;
        if (globalFound != UINT64_MAX) {
            result.found = true;
            result.matchedIndex = static_cast<std::size_t>(globalFound);
            result.matchedGuess = candidates[result.matchedIndex];
            result.guessesTried = globalFound + 1;
        } else {
            result.guessesTried = static_cast<std::uint64_t>(total);
        }
    }

    MPI_Bcast(&result.found, 1, MPI_C_BOOL, 0, MPI_COMM_WORLD);
    MPI_Bcast(&result.guessesTried, 1, MPI_UINT64_T, 0, MPI_COMM_WORLD);
    MPI_Bcast(&result.elapsedSeconds, 1, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    if (result.found) {
        std::uint64_t idx64 = 0;
        if (rank == 0) {
            idx64 = static_cast<std::uint64_t>(result.matchedIndex);
        }
        MPI_Bcast(&idx64, 1, MPI_UINT64_T, 0, MPI_COMM_WORLD);
        result.matchedIndex = static_cast<std::size_t>(idx64);
        if (result.matchedIndex < candidates.size()) {
            result.matchedGuess = candidates[result.matchedIndex];
        }
    }

    MPI_Finalize();
#else
    (void)argc;
    (void)argv;

    const auto start = std::chrono::high_resolution_clock::now();
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        ++result.guessesTried;
        if (candidates[i] == targetPassword) {
            result.found = true;
            result.matchedIndex = i;
            result.matchedGuess = candidates[i];
            break;
        }
    }
    const auto end = std::chrono::high_resolution_clock::now();
    result.elapsedSeconds = std::chrono::duration<double>(end - start).count();
#endif

    return result;
}