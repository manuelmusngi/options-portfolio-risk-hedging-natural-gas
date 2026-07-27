#pragma once

#include "models/Option.hpp"

namespace hedging {

class LongPut final : public Option {
public:
    LongPut(double strike, double premium);

    [[nodiscard]] double payoff(double spot) const override;
};

} // namespace hedging
