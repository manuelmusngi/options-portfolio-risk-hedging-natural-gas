#include "models/ShortPut.hpp"
#include <algorithm>

namespace hedging {

ShortPut::ShortPut(double strike, double premium)
    : Option{strike, premium, Type::ShortPut} {}

double ShortPut::payoff(double spot) const {
    // Writer of put: receives premium, loses if spot < strike
    const double intrinsic = std::max(0.0, m_strike - spot);
    return m_premium - intrinsic;
}

} // namespace hedging
