#ifndef GPU_KERNEL_H
#define GPU_KERNEL_H

#include <string>
#include <vector>

#include "simulation.h"

SimulationResult runCUDASimulation(
    const std::vector<std::string>& candidates,
    const std::string& targetPassword
);

#endif