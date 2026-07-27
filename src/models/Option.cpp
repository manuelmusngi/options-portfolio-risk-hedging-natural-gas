#include "models/Option.hpp"

namespace hedging {

Option::Option(double strike, double premium, Type type)
    : m_strike{strike}, m_premium{premium}, m_type{type} {}

double Option::strike() const noexcept { return m_strike; }
double Option::premium() const noexcept { return m_premium; }
Option::Type Option::type() const noexcept { return m_type; }

} // namespace hedging
