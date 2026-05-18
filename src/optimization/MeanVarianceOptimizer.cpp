#include "optimization/MeanVarianceOptimizer.hpp"
#include <Eigen/Dense>

namespace hedging {

std::vector<double> MeanVarianceOptimizer::solve(
    const std::vector<double>& mu,
    const std::vector<double>& cov,
    double gamma) const
{
    using Eigen::VectorXd;
    using Eigen::MatrixXd;

    const std::size_t n = mu.size();
    if (n == 0) return {};

    VectorXd mu_v(n);
    for (std::size_t i = 0; i < n; ++i) mu_v(i) = mu[i];

    MatrixXd Sigma(n, n);
    for (std::size_t i = 0; i < n; ++i)
        for (std::size_t j = 0; j < n; ++j)
            Sigma(i, j) = cov[i * n + j];

    // Simple unconstrained solution: maximize μᵀw − γ wᵀΣw
    // → derivative = 0 → μ − 2γ Σ w = 0 → w* = (1/(2γ)) Σ⁻¹ μ
    MatrixXd Sigma_inv = Sigma.inverse();
    VectorXd w = (1.0 / (2.0 * gamma)) * Sigma_inv * mu_v;

    // Normalize to sum to 1
    double sum = w.sum();
    if (sum != 0.0) w /= sum;

    std::vector<double> out(n);
    for (std::size_t i = 0; i < n; ++i) out[i] = w(i);
    return out;
}

} // namespace hedging
