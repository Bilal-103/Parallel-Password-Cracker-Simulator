#include "utils.h"

#include <algorithm>
#include <cctype>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>

namespace {

void printSectionDivider(char ch = '=', int width = 72) {
    for (int i = 0; i < width; ++i) {
        std::cout << ch;
    }
    std::cout << "\n";
}

std::string trim(const std::string& value) {
    std::size_t start = 0;
    while (start < value.size() && std::isspace(static_cast<unsigned char>(value[start]))) {
        ++start;
    }

    std::size_t end = value.size();
    while (end > start && std::isspace(static_cast<unsigned char>(value[end - 1]))) {
        --end;
    }

    return value.substr(start, end - start);
}

int readBoundedInt(const std::string& prompt, int defaultValue, int minValue, int maxValue) {
    while (true) {
        std::cout << prompt << " [default: " << defaultValue << "]: ";
        std::string line;
        std::getline(std::cin, line);

        line = trim(line);
        if (line.empty()) {
            return defaultValue;
        }

        try {
            const int parsed = std::stoi(line);
            if (parsed < minValue || parsed > maxValue) {
                std::cout << "[Input Error] Enter a value between "
                          << minValue << " and " << maxValue << ".\n";
                continue;
            }
            return parsed;
        } catch (...) {
            std::cout << "[Input Error] Please enter a valid integer.\n";
        }
    }
}

std::size_t readBoundedSize(const std::string& prompt,
                           std::size_t defaultValue,
                           std::size_t minValue,
                           std::size_t maxValue) {
    while (true) {
        std::cout << prompt << " [default: " << defaultValue << "]: ";
        std::string line;
        std::getline(std::cin, line);

        line = trim(line);
        if (line.empty()) {
            return defaultValue;
        }

        try {
            const std::size_t parsed = static_cast<std::size_t>(std::stoull(line));
            if (parsed < minValue || parsed > maxValue) {
                std::cout << "[Input Error] Enter a value between "
                          << minValue << " and " << maxValue << ".\n";
                continue;
            }
            return parsed;
        } catch (...) {
            std::cout << "[Input Error] Please enter a valid positive number.\n";
        }
    }
}

bool readYesNo(const std::string& prompt, bool defaultYes) {
    while (true) {
        std::cout << prompt << (defaultYes ? " [Y/n]: " : " [y/N]: ");
        std::string line;
        std::getline(std::cin, line);

        line = trim(line);
        if (line.empty()) {
            return defaultYes;
        }

        const char c = static_cast<char>(std::tolower(static_cast<unsigned char>(line[0])));
        if (c == 'y') {
            return true;
        }
        if (c == 'n') {
            return false;
        }

        std::cout << "[Input Error] Enter y or n.\n";
    }
}

} // namespace

InputConfig readInputConfig() {
    InputConfig config;

    printSectionDivider();
    std::cout << " Password Security Analysis and Guessing Simulation Tool\n";
    std::cout << " Educational and authorized testing use only\n";
    printSectionDivider();

    while (config.targetPassword.empty()) {
        std::cout << "Target password (simulation input): ";
        std::getline(std::cin, config.targetPassword);
        config.targetPassword = trim(config.targetPassword);
        if (config.targetPassword.empty()) {
            std::cout << "[Input Error] Target password cannot be empty.\n";
        }
    }

    std::cout << "Wordlist file path (leave empty for built-in list): ";
    std::getline(std::cin, config.wordlistPath);
    config.wordlistPath = trim(config.wordlistPath);

    config.maxPasswordLength = readBoundedInt(
        "Maximum password length (brute-force stage internally capped to 5)",
        config.maxPasswordLength,
        1,
        128
    );

    std::cout << "Character set for brute-force stage [default: " << config.charset << "]: ";
    std::string charsetInput;
    std::getline(std::cin, charsetInput);
    charsetInput = trim(charsetInput);
    if (!charsetInput.empty()) {
        config.charset = charsetInput;
    }

    config.bruteForceCandidateLimit = readBoundedSize(
        "Brute-force candidate limit",
        config.bruteForceCandidateLimit,
        static_cast<std::size_t>(1),
        static_cast<std::size_t>(10000000)
    );

    config.proposalBruteForceMode = readYesNo(
        "Use Proposal Mode (pure brute-force candidate space)?",
        true
    );

    printSectionDivider('-');
    std::cout << "Configuration Summary\n";
    std::cout << "Target: [hidden for privacy in demo output]\n";
    std::cout << "Wordlist: "
              << (config.wordlistPath.empty() ? "built-in fallback" : config.wordlistPath)
              << "\n";
    std::cout << "Max length: " << config.maxPasswordLength << "\n";
    std::cout << "Charset size: " << config.charset.size() << "\n";
    std::cout << "Brute-force limit: " << config.bruteForceCandidateLimit << "\n";
    std::cout << "Candidate mode: "
              << (config.proposalBruteForceMode ? "Proposal" : "Smart")
              << "\n";
    printSectionDivider('-');

    return config;
}

int readExecutionModeChoice() {
    std::cout << "\nExecution modes\n";
    printSectionDivider('-');
    std::cout << "1) Run all (Sequential + OpenMP + MPI + CUDA)\n";
    std::cout << "2) Sequential only\n";
    std::cout << "3) OpenMP only\n";
    std::cout << "4) MPI only\n";
    std::cout << "5) CUDA only\n";
    printSectionDivider('-');

    return readBoundedInt("Select mode", 1, 1, 5);
}

std::vector<std::string> loadWordlist(const std::string& path) {
    std::vector<std::string> words;
    if (path.empty()) {
        return words;
    }

    std::ifstream in(path);
    if (!in.is_open()) {
        std::cerr << "[Warning] Could not open wordlist at: " << path << "\n";
        return words;
    }

    std::string line;
    while (std::getline(in, line)) {
        if (!line.empty()) {
            words.push_back(line);
        }
    }

    return words;
}

std::vector<std::string> defaultCommonPasswords() {
    return {
        "password", "admin", "welcome", "qwerty", "letmein", "football", "sunshine", "master",
        "hello", "world", "user", "test", "login", "guest", "secure", "system"
    };
}

void printSimulationReport(
    const std::string& title,
    const SimulationResult& result,
    double sequentialSeconds
) {
    const double elapsed = (result.elapsedSeconds > 0.0) ? result.elapsedSeconds : 1e-9;
    const double guessesPerSecond = static_cast<double>(result.guessesTried) / elapsed;
    const double speedup = (sequentialSeconds > 0.0) ? sequentialSeconds / elapsed : 1.0;

    std::cout << "\n--- " << title << " ---\n";
    if (result.found) {
        std::cout << "[+] Match Found (Simulation)\n";
        std::cout << "Matched Guess: " << result.matchedGuess << "\n";
    } else {
        std::cout << "[-] Match Not Found\n";
    }

    std::cout << "Guesses Tried: " << result.guessesTried << "\n";
    std::cout << std::fixed << std::setprecision(6)
              << "Time: " << elapsed << " sec\n"
              << "Guesses/sec: " << guessesPerSecond << "\n"
              << "Speedup vs Sequential: " << speedup << "x\n";
}

void printComparisonDashboard(
    const std::vector<std::pair<std::string, SimulationResult>>& rows,
    double baselineSeconds
) {
    if (rows.empty()) {
        return;
    }

    double bestTime = std::numeric_limits<double>::max();
    for (const auto& row : rows) {
        const double elapsed = row.second.elapsedSeconds;
        if (elapsed > 0.0 && elapsed < bestTime) {
            bestTime = elapsed;
        }
    }

    std::cout << "\n";
    printSectionDivider();
    std::cout << " Comparison Dashboard\n";
    printSectionDivider();
    std::cout << std::left << std::setw(12) << "Mode"
              << std::setw(12) << "Found"
              << std::setw(16) << "Guesses"
              << std::setw(14) << "Time(s)"
              << std::setw(14) << "Speedup"
              << std::setw(12) << "Best" << "\n";
    printSectionDivider('-');

    for (const auto& row : rows) {
        const std::string& mode = row.first;
        const SimulationResult& result = row.second;

        const double elapsed = (result.elapsedSeconds > 0.0) ? result.elapsedSeconds : 1e-9;
        const double speedup = (baselineSeconds > 0.0) ? baselineSeconds / elapsed : 1.0;
        const bool isBest = (result.elapsedSeconds > 0.0 && result.elapsedSeconds == bestTime);

        std::cout << std::left << std::setw(12) << mode
                  << std::setw(12) << (result.found ? "Yes" : "No")
                  << std::setw(16) << result.guessesTried
                  << std::setw(14) << std::fixed << std::setprecision(6) << elapsed
                  << std::setw(14) << std::fixed << std::setprecision(2) << speedup
                  << std::setw(12) << (isBest ? "*" : "")
                  << "\n";
    }

    printSectionDivider();
}
