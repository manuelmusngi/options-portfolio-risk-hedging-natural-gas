#include "optimization/MeanVarianceOptimizer.hpp"
#include <vector>

namespace hedging {

std::vector<double> MeanVarianceOptimizer::solve(
    const std::vector<double>& expected_returns,
    const std::vector<double>& /*cov_matrix*/,
    double /*gamma*/) const
{
    // Stub: equal weights as placeholder
    const std::size_t n = expected_returns.size();
    if (n == 0) return {};

    std::vector<double> w(n, 1.0 / static_cast<double>(n));
    return w;
}

} // namespace hedging
