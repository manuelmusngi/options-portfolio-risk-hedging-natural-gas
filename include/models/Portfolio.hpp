#pragma once

#include <memory>
#include <vector>
#include "models/Option.hpp"

namespace hedging {

class Portfolio {
public:
    struct Position {
        std::unique_ptr<Option> instrument;
        double                  quantity; // positive = long, negative = short
    };

    Portfolio() = default;

    void add_position(std::unique_ptr<Option> opt, double quantity);

    // Spot price → total payoff across all positions
    [[nodiscard]] double payoff(double spot) const;

private:
    std::vector<Position> m_positions;
};

} // namespace hedging
