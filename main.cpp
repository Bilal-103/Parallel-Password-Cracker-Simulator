#include <iostream>
#include <vector>

#include "gpu_kernel.h"
#include "parallel_mpi.h"
#include "parallel_openmp.h"
#include "simulation.h"
#include "utils.h"

int main(int argc, char** argv) {
    InputConfig config = readInputConfig();

    std::vector<std::string> wordlist = loadWordlist(config.wordlistPath);
    if (wordlist.empty()) {
        std::cout << "Using built-in fallback wordlist for simulation.\n";
        wordlist = defaultCommonPasswords();
    }

    std::vector<std::string> candidates;
    if (config.proposalBruteForceMode) {
        candidates = buildBruteForceOnlyCandidateList(
            config.maxPasswordLength,
            config.charset,
            config.bruteForceCandidateLimit
        );
    } else {
        candidates = buildOrderedCandidateList(
            wordlist,
            config.maxPasswordLength,
            config.charset,
            config.bruteForceCandidateLimit
        );
    }

    std::cout << "\n================ Password Cracker Benchmark UI ================\n";
    std::cout << "Candidate mode: "
              << (config.proposalBruteForceMode
                     ? "Proposal Mode (pure brute-force search space)"
                     : "Smart Mode (dictionary + pattern + brute-force)")
              << "\n";
    std::cout << "Total candidates: " << candidates.size() << "\n";

    const int choice = readExecutionModeChoice();

    const bool runSequential = (choice == 1 || choice == 2);
    const bool runOpenMP = (choice == 1 || choice == 3);
    const bool runMPI = (choice == 1 || choice == 4);
    const bool runCUDA = (choice == 1 || choice == 5);

    std::vector<std::pair<std::string, SimulationResult>> comparisonRows;

    SimulationResult sequentialResult;
    if (runSequential || choice == 1) {
        sequentialResult = runSequentialSimulation(candidates, config.targetPassword);
        printSimulationReport("Sequential Baseline", sequentialResult, sequentialResult.elapsedSeconds);
        comparisonRows.push_back(std::make_pair("Sequential", sequentialResult));
    }

    const double baselineSeconds = (sequentialResult.elapsedSeconds > 0.0)
        ? sequentialResult.elapsedSeconds
        : runSequentialSimulation(candidates, config.targetPassword).elapsedSeconds;

    if (runOpenMP) {
        SimulationResult openmpResult = runOpenMPSimulation(candidates, config.targetPassword);
        printSimulationReport("OpenMP Parallel Simulation", openmpResult, baselineSeconds);
        comparisonRows.push_back(std::make_pair("OpenMP", openmpResult));
#ifndef _OPENMP
        std::cout << "[Info] OpenMP not enabled at compile time; fallback path executed.\n";
#endif
    }

    if (runMPI) {
        SimulationResult mpiResult = runMPISimulation(candidates, config.targetPassword, argc, argv);
        printSimulationReport("MPI Distributed Simulation", mpiResult, baselineSeconds);
        comparisonRows.push_back(std::make_pair("MPI", mpiResult));
#ifndef USE_MPI
        std::cout << "[Info] MPI not enabled at compile time; fallback path executed.\n";
#endif
    }

    if (runCUDA) {
        SimulationResult cudaResult = runCUDASimulation(candidates, config.targetPassword);
        printSimulationReport("CUDA GPU Simulation", cudaResult, baselineSeconds);
        comparisonRows.push_back(std::make_pair("CUDA", cudaResult));
#ifndef USE_CUDA
        std::cout << "[Info] CUDA not enabled at compile time; fallback path executed.\n";
#endif
    }

    printComparisonDashboard(comparisonRows, baselineSeconds);

    std::cout << "\nSimulation complete.\n";
    return 0;
}