#ifndef PASSWORD_UTILS_H
#define PASSWORD_UTILS_H

#include <utility>
#include <string>
#include <vector>

#include "simulation.h"

struct InputConfig {
    std::string targetPassword;
    std::string wordlistPath;
    int maxPasswordLength = 5;
    std::string charset = "abcdefghijklmnopqrstuvwxyz0123456789";
    std::size_t bruteForceCandidateLimit = 200000;
    bool proposalBruteForceMode = true;
};

InputConfig readInputConfig();
int readExecutionModeChoice();
std::vector<std::string> loadWordlist(const std::string& path);
std::vector<std::string> defaultCommonPasswords();
void printSimulationReport(
    const std::string& title,
    const SimulationResult& result,
    double sequentialSeconds
);
void printComparisonDashboard(
    const std::vector<std::pair<std::string, SimulationResult>>& rows,
    double baselineSeconds
);

#endif