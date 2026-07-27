#include "storage/StorageBase.hpp"
#include <algorithm>

namespace hedging {

StorageBase::StorageBase(double capacity_mwh, double efficiency)
    : m_capacity_mwh{capacity_mwh},
      m_efficiency{efficiency},
      m_soc_mwh{0.0} {}

double StorageBase::capacity() const noexcept { return m_capacity_mwh; }
double StorageBase::state_of_charge() const noexcept { return m_soc_mwh; }

void StorageBase::step(double power_mw, double dt_hours) {
    double energy = power_mw * dt_hours;

    if (energy > 0.0) { // charging
        energy *= m_efficiency;
        m_soc_mwh = std::clamp(m_soc_mwh + energy, 0.0, m_capacity_mwh);
    } else { // discharging
        energy /= m_efficiency;
        m_soc_mwh = std::clamp(m_soc_mwh + energy, 0.0, m_capacity_mwh);
    }
}

} // namespace hedging
