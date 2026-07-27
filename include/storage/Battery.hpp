#pragma once

#include "storage/StorageBase.hpp"

namespace hedging {

class Battery final : public StorageBase {
public:
    Battery(double capacity_mwh, double efficiency, double variable_cost_per_mwh);

    [[nodiscard]] double variable_cost_per_mwh() const noexcept;

private:
    double m_variable_cost_per_mwh;
};

} // namespace hedging
