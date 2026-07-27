#pragma once

#include "models/Option.hpp"

namespace hedging {

class ShortPut final : public Option {
public:
    ShortPut(double strike, double premium);

    [[nodiscard]] double payoff(double spot) const override;
};

} // namespace hedging
