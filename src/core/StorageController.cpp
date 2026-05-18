#include "core/StorageController.hpp"

namespace hedging {

StorageController::StorageController(std::unique_ptr<StorageBase> storage)
    : m_storage{std::move(storage)} {}

double StorageController::decide_power(double price,
                                       double low_threshold,
                                       double high_threshold) const {
    // Very simple: charge when cheap, discharge when expensive
    if (price < low_threshold) {
        return +10.0; // charge 10 MW
    }
    if (price > high_threshold) {
        return -10.0; // discharge 10 MW
    }
    return 0.0;
}

void StorageController::step(double power_mw, double dt_hours) {
    m_storage->step(power_mw, dt_hours);
}

double StorageController::soc() const noexcept {
    return m_storage->state_of_charge();
}

} // namespace hedging
