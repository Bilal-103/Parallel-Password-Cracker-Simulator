#include "gpu_kernel.h"

#ifndef USE_CUDA

#include <chrono>

SimulationResult runCUDASimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword
) {
    SimulationResult result;
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
    return result;
}

#endif