#include "core/Engine.hpp"

namespace hedging {

Engine::Engine(Portfolio portfolio,
               std::unique_ptr<StorageBase> storage,
               double generator_marginal_cost)
    : m_portfolio{std::move(portfolio)},
      m_storage_ctrl{std::move(storage)},
      m_gen_mc{generator_marginal_cost} {}

double Engine::run(const std::vector<double>& spot_path,
                   double low_threshold,
                   double high_threshold,
                   double dt_hours) {
    double total_pnl = 0.0;

    // Simple assumption: generator produces 1 MWh each hour if price > mc
    for (double price : spot_path) {
        // Generator revenue
        double gen_output_mwh = (price > m_gen_mc) ? 1.0 : 0.0;
        double gen_pnl = gen_output_mwh * (price - m_gen_mc);

        // Storage decision
        double power_mw = m_storage_ctrl.decide_power(price, low_threshold, high_threshold);
        m_storage_ctrl.step(power_mw, dt_hours);
        // You can subtract storage variable cost here if you track it

        total_pnl += gen_pnl;
    }

    // Option portfolio payoff at final spot (expiry)
    if (!spot_path.empty()) {
        double final_spot = spot_path.back();
        total_pnl += m_portfolio.payoff(final_spot);
    }

    return total_pnl;
}

} // namespace hedging
