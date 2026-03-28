#ifndef PARALLEL_MPI_H
#define PARALLEL_MPI_H

#include <string>
#include <vector>

#include "simulation.h"

SimulationResult runMPISimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword,
    int argc,
    char** argv
);

#endif