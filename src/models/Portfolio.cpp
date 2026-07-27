#include "models/Portfolio.hpp"

namespace hedging {

void Portfolio::add_position(std::unique_ptr<Option> opt, double quantity) {
    m_positions.push_back(Position{std::move(opt), quantity});
}

double Portfolio::payoff(double spot) const {
    double total = 0.0;
    for (const auto& pos : m_positions) {
        total += pos.quantity * pos.instrument->payoff(spot);
    }
    return total;
}

} // namespace hedging
