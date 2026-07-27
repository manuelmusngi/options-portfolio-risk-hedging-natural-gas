#include "models/LongPut.hpp"
#include <algorithm>

namespace hedging {

LongPut::LongPut(double strike, double premium)
    : Option{strike, premium, Type::LongPut} {}

double LongPut::payoff(double spot) const {
    // Holder of put: pays premium, gains if spot < strike
    const double intrinsic = std::max(0.0, m_strike - spot);
    return intrinsic - m_premium;
}

} // namespace hedging
