#include "storage/P2G.hpp"

namespace hedging {

P2G::P2G(double capacity_mwh, double efficiency, double conversion_cost_per_mwh)
    : StorageBase{capacity_mwh, efficiency},
      m_conversion_cost_per_mwh{conversion_cost_per_mwh} {}

double P2G::conversion_cost_per_mwh() const noexcept {
    return m_conversion_cost_per_mwh;
}

} // namespace hedging
