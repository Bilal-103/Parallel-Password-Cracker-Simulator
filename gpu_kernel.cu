#include "gpu_kernel.h"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <vector>

#ifdef USE_CUDA
#include <cuda_runtime.h>

__global__ void compareKernel(
    const char* candidates,
    const int* lengths,
    int candidateCount,
    const char* target,
    int targetLen,
    int stride,
    int* foundIndex
) {
    const int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= candidateCount) {
        return;
    }

    if (lengths[idx] != targetLen) {
        return;
    }

    const char* candidate = candidates + (idx * stride);
    for (int i = 0; i < targetLen; ++i) {
        if (candidate[i] != target[i]) {
            return;
        }
    }

    atomicMin(foundIndex, idx);
}
#endif

#ifdef USE_CUDA
SimulationResult runCUDASimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword
) {
    SimulationResult result;
    const auto start = std::chrono::high_resolution_clock::now();

    if (candidates.empty()) {
        const auto end = std::chrono::high_resolution_clock::now();
        result.elapsedSeconds = std::chrono::duration<double>(end - start).count();
        return result;
    }

    int maxLen = static_cast<int>(targetPassword.size());
    for (const std::string& c : candidates) {
        maxLen = std::max(maxLen, static_cast<int>(c.size()));
    }
    const int stride = maxLen + 1;

    std::vector<char> hostCandidates(candidates.size() * static_cast<std::size_t>(stride), '\0');
    std::vector<int> hostLengths(candidates.size(), 0);

    for (std::size_t i = 0; i < candidates.size(); ++i) {
        hostLengths[i] = static_cast<int>(candidates[i].size());
        for (int j = 0; j < hostLengths[i] && j < stride - 1; ++j) {
            hostCandidates[i * static_cast<std::size_t>(stride) + static_cast<std::size_t>(j)] = candidates[i][static_cast<std::size_t>(j)];
        }
    }

    char* dCandidates = nullptr;
    int* dLengths = nullptr;
    char* dTarget = nullptr;
    int* dFoundIndex = nullptr;

    const int notFound = INT32_MAX;
    int hostFound = notFound;

    cudaMalloc(&dCandidates, hostCandidates.size() * sizeof(char));
    cudaMalloc(&dLengths, hostLengths.size() * sizeof(int));
    cudaMalloc(&dTarget, targetPassword.size() * sizeof(char));
    cudaMalloc(&dFoundIndex, sizeof(int));

    cudaMemcpy(dCandidates, hostCandidates.data(), hostCandidates.size() * sizeof(char), cudaMemcpyHostToDevice);
    cudaMemcpy(dLengths, hostLengths.data(), hostLengths.size() * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(dTarget, targetPassword.data(), targetPassword.size() * sizeof(char), cudaMemcpyHostToDevice);
    cudaMemcpy(dFoundIndex, &notFound, sizeof(int), cudaMemcpyHostToDevice);

    const int blockSize = 256;
    const int gridSize = (static_cast<int>(candidates.size()) + blockSize - 1) / blockSize;

    compareKernel<<<gridSize, blockSize>>>(
        dCandidates,
        dLengths,
        static_cast<int>(candidates.size()),
        dTarget,
        static_cast<int>(targetPassword.size()),
        stride,
        dFoundIndex
    );
    cudaDeviceSynchronize();

    cudaMemcpy(&hostFound, dFoundIndex, sizeof(int), cudaMemcpyDeviceToHost);

    cudaFree(dCandidates);
    cudaFree(dLengths);
    cudaFree(dTarget);
    cudaFree(dFoundIndex);

    if (hostFound != notFound && hostFound >= 0 && hostFound < static_cast<int>(candidates.size())) {
        result.found = true;
        result.matchedIndex = static_cast<std::size_t>(hostFound);
        result.matchedGuess = candidates[result.matchedIndex];
        result.guessesTried = static_cast<std::uint64_t>(hostFound + 1);
    } else {
        result.guessesTried = static_cast<std::uint64_t>(candidates.size());
    }

    const auto end = std::chrono::high_resolution_clock::now();
    result.elapsedSeconds = std::chrono::duration<double>(end - start).count();
    return result;
}
#endif