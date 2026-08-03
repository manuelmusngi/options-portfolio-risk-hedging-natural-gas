#include "simulation/ScenarioRunner.hpp"
#include <iostream>

namespace hedging {

ScenarioRunner::ScenarioRunner(std::vector<double> expected_returns,
                               std::vector<double> cov_matrix)
    : m_mu{std::move(expected_returns)},
      m_cov{std::move(cov_matrix)} {}

void ScenarioRunner::sweep_gamma(const std::vector<double>& gammas) const {
    for (double g : gammas) {
        auto w = m_opt.solve(m_mu, m_cov, g);

        std::cout << "gamma = " << g << " → weights: ";
        for (double wi : w) std::cout << wi << " ";
        std::cout << "\n";
    }
}

} // namespace hedging
