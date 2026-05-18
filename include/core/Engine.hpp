#pragma once
#include <vector>
#include "models/Portfolio.hpp"
#include "core/StorageController.hpp"

namespace hedging {

class Engine {
public:
    Engine(Portfolio portfolio,
           std::unique_ptr<StorageBase> storage,
           double generator_marginal_cost);

    double run(const std::vector<double>& spot_path,
               double low_threshold,
               double high_threshold,
               double dt_hours = 1.0);

private:
    Portfolio         m_portfolio;
    StorageController m_storage_ctrl;
    double            m_gen_mc;
};

}
