#include "models/ShortCall.hpp"
#include <algorithm>

namespace hedging {

ShortCall::ShortCall(double strike, double premium)
    : Option{strike, premium, Type::ShortCall} {}

double ShortCall::payoff(double spot) const {
    // Writer of call: receives premium, loses if spot > strike
    const double intrinsic = std::max(0.0, spot - m_strike);
    return m_premium - intrinsic;
}

} // namespace hedging
