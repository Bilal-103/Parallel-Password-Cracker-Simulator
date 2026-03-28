#include <iostream>
#include <iomanip>
#include <limits>
#include <tuple>
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

    std::cout << "\nExecution modes:\n";
    std::cout << "1) Run all (Sequential + OpenMP + MPI + CUDA)\n";
    std::cout << "2) Sequential only\n";
    std::cout << "3) OpenMP only\n";
    std::cout << "4) MPI only\n";
    std::cout << "5) CUDA only\n";
    std::cout << "Select mode: ";

    int choice = 1;
    std::cin >> choice;
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    const bool runSequential = (choice == 1 || choice == 2);
    const bool runOpenMP = (choice == 1 || choice == 3);
    const bool runMPI = (choice == 1 || choice == 4);
    const bool runCUDA = (choice == 1 || choice == 5);

    std::vector<std::tuple<std::string, SimulationResult, bool>> comparisonRows;

    SimulationResult sequentialResult;
    if (runSequential || choice == 1) {
        sequentialResult = runSequentialSimulation(candidates, config.targetPassword);
        printSimulationReport("Sequential Baseline", sequentialResult, sequentialResult.elapsedSeconds);
        comparisonRows.push_back(std::make_tuple("Sequential", sequentialResult, true));
    }

    const double baselineSeconds = (sequentialResult.elapsedSeconds > 0.0)
        ? sequentialResult.elapsedSeconds
        : runSequentialSimulation(candidates, config.targetPassword).elapsedSeconds;

    if (runOpenMP) {
        SimulationResult openmpResult = runOpenMPSimulation(candidates, config.targetPassword);
        printSimulationReport("OpenMP Parallel Simulation", openmpResult, baselineSeconds);
        comparisonRows.push_back(std::make_tuple("OpenMP", openmpResult, true));
#ifndef _OPENMP
        std::cout << "[Info] OpenMP not enabled at compile time; fallback path executed.\n";
#endif
    }

    if (runMPI) {
        SimulationResult mpiResult = runMPISimulation(candidates, config.targetPassword, argc, argv);
        printSimulationReport("MPI Distributed Simulation", mpiResult, baselineSeconds);
        comparisonRows.push_back(std::make_tuple("MPI", mpiResult, true));
#ifndef USE_MPI
        std::cout << "[Info] MPI not enabled at compile time; fallback path executed.\n";
#endif
    }

    if (runCUDA) {
        SimulationResult cudaResult = runCUDASimulation(candidates, config.targetPassword);
        printSimulationReport("CUDA GPU Simulation", cudaResult, baselineSeconds);
        comparisonRows.push_back(std::make_tuple("CUDA", cudaResult, true));
#ifndef USE_CUDA
        std::cout << "[Info] CUDA not enabled at compile time; fallback path executed.\n";
#endif
    }

    if (!comparisonRows.empty()) {
        std::cout << "\n==================== Comparison Dashboard ====================\n";
        std::cout << std::left << std::setw(12) << "Mode"
                  << std::setw(12) << "Found"
                  << std::setw(16) << "Guesses"
                  << std::setw(14) << "Time(s)"
                  << std::setw(14) << "Speedup"
                  << "\n";
        std::cout << "--------------------------------------------------------------\n";

        for (const auto& row : comparisonRows) {
            const std::string& mode = std::get<0>(row);
            const SimulationResult& result = std::get<1>(row);

            const double elapsed = (result.elapsedSeconds > 0.0) ? result.elapsedSeconds : 1e-9;
            const double speedup = (baselineSeconds > 0.0) ? baselineSeconds / elapsed : 1.0;

            std::cout << std::left << std::setw(12) << mode
                      << std::setw(12) << (result.found ? "Yes" : "No")
                      << std::setw(16) << result.guessesTried
                      << std::setw(14) << std::fixed << std::setprecision(6) << elapsed
                      << std::setw(14) << std::fixed << std::setprecision(2) << speedup
                      << "\n";
        }

        std::cout << "==============================================================\n";
    }

    std::cout << "\nSimulation complete.\n";
    return 0;
}