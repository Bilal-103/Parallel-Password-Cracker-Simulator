#ifndef PASSWORD_SIMULATION_H
#define PASSWORD_SIMULATION_H

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

struct SimulationResult {
    bool found = false;
    std::uint64_t guessesTried = 0;
    std::string matchedGuess;
    std::size_t matchedIndex = static_cast<std::size_t>(-1);
    double elapsedSeconds = 0.0;
};

std::vector<std::string> buildOrderedCandidateList(
    const std::vector<std::string>& wordlist,
    int maxPasswordLength,
    const std::string& charset,
    std::size_t bruteForceCandidateLimit = 200000
);

std::vector<std::string> buildBruteForceOnlyCandidateList(
    int maxPasswordLength,
    const std::string& charset,
    std::size_t bruteForceCandidateLimit = 200000
);

SimulationResult runSequentialSimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword
);

#endif