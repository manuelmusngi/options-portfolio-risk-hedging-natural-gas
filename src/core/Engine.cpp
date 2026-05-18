#include "core/Engine.hpp"

namespace hedging {

Engine::Engine(Portfolio p,
               std::unique_ptr<StorageBase> s,
               double mc)
    : m_portfolio{std::move(p)},
      m_storage_ctrl{std::move(s)},
      m_gen_mc{mc} {}

double Engine::run(const std::vector<double>& spot,
                   double low, double high, double dt) {
    double pnl = 0.0;

    for (double price : spot) {
        double gen = (price > m_gen_mc) ? 1.0 : 0.0;
        pnl += gen * (price - m_gen_mc);

        double power = m_storage_ctrl.decide_power(price, low, high);
        m_storage_ctrl.step(power, dt);
    }

    if (!spot.empty())
        pnl += m_portfolio.payoff(spot.back());

    return pnl;
}

}
