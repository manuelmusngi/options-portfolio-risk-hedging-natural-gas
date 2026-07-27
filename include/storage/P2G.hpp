#pragma once

#include "storage/StorageBase.hpp"

namespace hedging {

class P2G final : public StorageBase {
public:
    P2G(double capacity_mwh, double efficiency, double conversion_cost_per_mwh);

    [[nodiscard]] double conversion_cost_per_mwh() const noexcept;

private:
    double m_conversion_cost_per_mwh;
};

} // namespace hedging
