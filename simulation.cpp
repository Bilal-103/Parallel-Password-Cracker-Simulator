#include "simulation.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cctype>
#include <functional>
#include <unordered_set>

namespace {

std::string toLower(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(),
        [](unsigned char ch) { return static_cast<char>(std::tolower(ch)); });
    return s;
}

std::string capitalizeFirst(std::string s) {
    if (!s.empty()) {
        s[0] = static_cast<char>(std::toupper(static_cast<unsigned char>(s[0])));
    }
    return s;
}

std::string toUpper(std::string s) {
    std::transform(s.begin(), s.end(), s.begin(),
        [](unsigned char ch) { return static_cast<char>(std::toupper(ch)); });
    return s;
}

std::string replaceAllCommonSubstitutions(const std::string& s) {
    std::string out = s;
    for (char& ch : out) {
        switch (static_cast<char>(std::tolower(static_cast<unsigned char>(ch)))) {
        case 'a':
            ch = '@';
            break;
        case 's':
            ch = '$';
            break;
        case 'o':
            ch = '0';
            break;
        default:
            break;
        }
    }
    return out;
}

void pushUniqueIfValid(
    const std::string& candidate,
    int maxLen,
    std::unordered_set<std::string>& seen,
    std::vector<std::string>& out
) {
    if (candidate.empty()) {
        return;
    }
    if (static_cast<int>(candidate.size()) > maxLen) {
        return;
    }
    if (seen.insert(candidate).second) {
        out.push_back(candidate);
    }
}

std::vector<std::string> buildPatternCandidates(
    const std::vector<std::string>& wordlist,
    int maxLen,
    std::unordered_set<std::string>& seen
) {
    static const std::array<std::string, 7> suffixes = {
        "1", "12", "123", "1234", "2024", "2025", "!"
    };

    std::vector<std::string> patterns;
    patterns.reserve(wordlist.size() * 8);

    for (const std::string& rawWord : wordlist) {
        const std::string base = toLower(rawWord);
        if (base.empty()) {
            continue;
        }

        pushUniqueIfValid(base, maxLen, seen, patterns);
        pushUniqueIfValid(capitalizeFirst(base), maxLen, seen, patterns);
        pushUniqueIfValid(toUpper(base), maxLen, seen, patterns);
        pushUniqueIfValid(replaceAllCommonSubstitutions(base), maxLen, seen, patterns);

        for (const std::string& suffix : suffixes) {
            pushUniqueIfValid(base + suffix, maxLen, seen, patterns);
            pushUniqueIfValid(capitalizeFirst(base) + suffix, maxLen, seen, patterns);
        }

        for (std::size_t i = 0; i < base.size(); ++i) {
            std::string single = base;
            char lower = static_cast<char>(std::tolower(static_cast<unsigned char>(single[i])));
            if (lower == 'a') {
                single[i] = '@';
            } else if (lower == 's') {
                single[i] = '$';
            } else if (lower == 'o') {
                single[i] = '0';
            } else {
                continue;
            }
            pushUniqueIfValid(single, maxLen, seen, patterns);
        }
    }

    return patterns;
}

std::vector<std::string> buildCombinationCandidates(
    const std::vector<std::string>& wordlist,
    int maxLen,
    std::unordered_set<std::string>& seen
) {
    std::vector<std::string> combos;

    const std::size_t cap = std::min<std::size_t>(wordlist.size(), 200);
    for (std::size_t i = 0; i < cap; ++i) {
        const std::string left = toLower(wordlist[i]);
        if (left.empty()) {
            continue;
        }
        for (std::size_t j = 0; j < cap; ++j) {
            if (i == j) {
                continue;
            }
            const std::string right = toLower(wordlist[j]);
            if (right.empty()) {
                continue;
            }
            pushUniqueIfValid(left + right, maxLen, seen, combos);
        }
    }

    return combos;
}

std::vector<std::string> buildBruteForceCandidates(
    const std::string& charset,
    int maxLen,
    std::size_t limit,
    std::unordered_set<std::string>& seen
) {
    std::vector<std::string> brute;
    if (charset.empty() || maxLen <= 0 || limit == 0) {
        return brute;
    }

    const int cappedLen = std::min(maxLen, 5);
    brute.reserve(std::min<std::size_t>(limit, 50000));

    std::string current;
    current.reserve(cappedLen);

    std::function<void(int)> generate = [&](int targetLen) {
        if (brute.size() >= limit) {
            return;
        }
        if (static_cast<int>(current.size()) == targetLen) {
            if (seen.insert(current).second) {
                brute.push_back(current);
            }
            return;
        }

        for (char ch : charset) {
            current.push_back(ch);
            generate(targetLen);
            current.pop_back();
            if (brute.size() >= limit) {
                return;
            }
        }
    };

    for (int len = 1; len <= cappedLen; ++len) {
        generate(len);
        if (brute.size() >= limit) {
            break;
        }
    }

    return brute;
}

} // namespace

std::vector<std::string> buildOrderedCandidateList(
    const std::vector<std::string>& wordlist,
    int maxPasswordLength,
    const std::string& charset,
    std::size_t bruteForceCandidateLimit
) {
    std::vector<std::string> ordered;
    std::unordered_set<std::string> seen;

    ordered.reserve(wordlist.size() * 3 + 5000);

    static const std::array<const char*, 16> commonFirst = {
        "123456", "password", "qwerty", "12345678", "111111", "abc123", "admin", "letmein",
        "welcome", "iloveyou", "monkey", "dragon", "sunshine", "football", "princess", "passw0rd"
    };

    for (const char* common : commonFirst) {
        pushUniqueIfValid(common, maxPasswordLength, seen, ordered);
    }

    for (const std::string& word : wordlist) {
        pushUniqueIfValid(toLower(word), maxPasswordLength, seen, ordered);
    }

    std::vector<std::string> patterns = buildPatternCandidates(wordlist, maxPasswordLength, seen);
    ordered.insert(ordered.end(), patterns.begin(), patterns.end());

    std::vector<std::string> combos = buildCombinationCandidates(wordlist, maxPasswordLength, seen);
    ordered.insert(ordered.end(), combos.begin(), combos.end());

    std::vector<std::string> brute = buildBruteForceCandidates(
        charset,
        maxPasswordLength,
        bruteForceCandidateLimit,
        seen
    );
    ordered.insert(ordered.end(), brute.begin(), brute.end());

    return ordered;
}

std::vector<std::string> buildBruteForceOnlyCandidateList(
    int maxPasswordLength,
    const std::string& charset,
    std::size_t bruteForceCandidateLimit
) {
    std::unordered_set<std::string> seen;
    return buildBruteForceCandidates(
        charset,
        maxPasswordLength,
        bruteForceCandidateLimit,
        seen
    );
}

SimulationResult runSequentialSimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword
) {
    SimulationResult result;
    const auto start = std::chrono::high_resolution_clock::now();

    for (std::size_t i = 0; i < candidates.size(); ++i) {
        ++result.guessesTried;
        if (candidates[i] == targetPassword) {
            result.found = true;
            result.matchedGuess = candidates[i];
            result.matchedIndex = i;
            break;
        }
    }

    const auto end = std::chrono::high_resolution_clock::now();
    result.elapsedSeconds = std::chrono::duration<double>(end - start).count();

    return result;
}