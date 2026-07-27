 #include "storage/Battery.hpp"

namespace hedging {

Battery::Battery(double capacity_mwh, double efficiency, double variable_cost_per_mwh)
    : StorageBase{capacity_mwh, efficiency},
      m_variable_cost_per_mwh{variable_cost_per_mwh} {}

double Battery::variable_cost_per_mwh() const noexcept {
    return m_variable_cost_per_mwh;
}

} // namespace hedging
