#ifndef PARALLEL_OPENMP_H
#define PARALLEL_OPENMP_H

#include <string>
#include <vector>

#include "simulation.h"

SimulationResult runOpenMPSimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword
);

#endif