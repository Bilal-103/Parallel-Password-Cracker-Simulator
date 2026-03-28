#include "parallel_openmp.h"

#include <chrono>
#include <cstddef>

#ifdef _OPENMP
#include <omp.h>
#endif

SimulationResult runOpenMPSimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword
) {
    SimulationResult result;
    const auto start = std::chrono::high_resolution_clock::now();

#ifdef _OPENMP
    std::size_t foundIndex = static_cast<std::size_t>(-1);

#pragma omp parallel for schedule(static)
    for (int i = 0; i < static_cast<int>(candidates.size()); ++i) {
        if (candidates[static_cast<std::size_t>(i)] == targetPassword) {
#pragma omp critical
            {
                if (foundIndex == static_cast<std::size_t>(-1)
                    || static_cast<std::size_t>(i) < foundIndex) {
                    foundIndex = static_cast<std::size_t>(i);
                }
            }
        }
    }

    if (foundIndex != static_cast<std::size_t>(-1)) {
        result.found = true;
        result.matchedIndex = foundIndex;
        result.matchedGuess = candidates[foundIndex];
        result.guessesTried = foundIndex + 1;
    } else {
        result.guessesTried = static_cast<std::uint64_t>(candidates.size());
    }
#else
    for (std::size_t i = 0; i < candidates.size(); ++i) {
        ++result.guessesTried;
        if (candidates[i] == targetPassword) {
            result.found = true;
            result.matchedIndex = i;
            result.matchedGuess = candidates[i];
            break;
        }
    }
#endif

    const auto end = std::chrono::high_resolution_clock::now();
    result.elapsedSeconds = std::chrono::duration<double>(end - start).count();
    return result;
}