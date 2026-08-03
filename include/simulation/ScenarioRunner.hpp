#pragma once

#include <vector>
#include "optimization/MeanVarianceOptimizer.hpp"

namespace hedging {

class ScenarioRunner {
public:
    ScenarioRunner(std::vector<double> expected_returns,
                   std::vector<double> cov_matrix);

    void sweep_gamma(const std::vector<double>& gammas) const;

private:
    std::vector<double> m_mu;
    std::vector<double> m_cov;
    MeanVarianceOptimizer m_opt;
};

} // namespace hedging
