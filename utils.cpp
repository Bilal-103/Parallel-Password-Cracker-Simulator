#include "utils.h"

#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>

InputConfig readInputConfig() {
    InputConfig config;

    std::cout << "=== Password Security Analysis and Guessing Simulation Tool ===\n";
    std::cout << "Educational and authorized testing use only.\n\n";

    std::cout << "Enter target password (plaintext simulation input): ";
    std::getline(std::cin, config.targetPassword);

    std::cout << "Enter wordlist file path (or leave empty to use built-in list): ";
    std::getline(std::cin, config.wordlistPath);

    std::cout << "Enter max password length (recommended <= 10, brute-force capped at 5): ";
    std::string maxLenText;
    std::getline(std::cin, maxLenText);
    if (!maxLenText.empty()) {
        config.maxPasswordLength = std::max(1, std::stoi(maxLenText));
    }

    std::cout << "Enter character set for brute-force simulation (default a-z0-9): ";
    std::string charset;
    std::getline(std::cin, charset);
    if (!charset.empty()) {
        config.charset = charset;
    }

    std::cout << "Enter brute-force candidate limit (default 200000): ";
    std::string limitText;
    std::getline(std::cin, limitText);
    if (!limitText.empty()) {
        config.bruteForceCandidateLimit = static_cast<std::size_t>(std::stoull(limitText));
    }

    std::cout << "Use proposal mode (pure brute-force search space for stage-wise comparison)? [Y/n]: ";
    std::string modeText;
    std::getline(std::cin, modeText);
    if (!modeText.empty()) {
        const char c = static_cast<char>(std::tolower(static_cast<unsigned char>(modeText[0])));
        config.proposalBruteForceMode = (c != 'n');
    }

    return config;
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
