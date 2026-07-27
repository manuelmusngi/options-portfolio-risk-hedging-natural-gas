#pragma once

#include "models/Option.hpp"

namespace hedging {

class ShortCall final : public Option {
public:
    ShortCall(double strike, double premium);

    [[nodiscard]] double payoff(double spot) const override;
};

} // namespace hedging
