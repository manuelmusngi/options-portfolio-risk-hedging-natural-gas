#include <iostream>
#include <vector>
#include <memory>

#include "models/ShortPut.hpp"
#include "models/LongPut.hpp"
#include "models/ShortCall.hpp"
#include "models/Portfolio.hpp"
#include "storage/Battery.hpp"
#include "core/Engine.hpp"
#include "simulation/ScenarioRunner.hpp"

using namespace hedging;

int main() {
    Portfolio portfolio;
    portfolio.add_position(std::make_unique<ShortPut>(100.0, 5.0), -1.0);
    portfolio.add_position(std::make_unique<LongPut>(95.0, 3.0), 1.0);
    portfolio.add_position(std::make_unique<ShortCall>(110.0, 4.0), -1.0);

    auto battery = std::make_unique<Battery>(50.0, 0.9, 2.0);

    Engine engine(std::move(portfolio), std::move(battery), /*gen_mc=*/60.0);

    std::vector<double> spot = {40, 55, 65, 80, 120, 90, 70};

    double pnl = engine.run(spot, /*low_threshold=*/50.0, /*high_threshold=*/90.0);
    std::cout << "Total P&L: " << pnl << "\n";

    // Mean-variance scenario sweep
    std::vector<double> mu  = {0.02, 0.01, 0.03};
    std::vector<double> cov = {
        0.10, 0.02, 0.01,
        0.02, 0.08, 0.03,
        0.01, 0.03, 0.12
    };

    ScenarioRunner runner(mu, cov);
    runner.sweep_gamma({0.1, 0.5, 1.0, 2.0});

    return 0;
}
