# Option-Based Portfolio Risk Hedging for Gas Generators

This project is an exercise in implementing a research-grade Options Strategies in Henry Hub Natural Gas that may be used in hedging. Two implementations are considered, one using Python-based while the other in C++ based structures.

> **Paper:** Lai, S., Qiu, J., & Tao, Y. (2022). Option-based portfolio risk hedging strategy for gas generator based on mean-variance utility model. *Energy Conversion and Economics*, 3(1), 20–30. DOI: [10.1049/enc2.12036](https://doi.org/10.1049/enc2.12036)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-green.svg)](https://www.python.org/)
[![DOI](https://img.shields.io/badge/DOI-10.1049%2Fenc2.12036-orange.svg)](https://doi.org/10.1049/enc2.12036)
[![Status: Research](https://img.shields.io/badge/Status-Research-purple.svg)]()

---

## Abstract

Natural gas generators face significant operational risks in electricity markets due to price volatility and uncertain demand. This repository implements the **option-based portfolio risk-hedging framework** proposed by Lai et al. (2022), which combines three financial option instruments — **short put**, **long put**, and **short call** — with two energy storage technologies — **Power-to-Gas (P2G)** and **battery** — to maximise the risk-adjusted utility of a gas generator. Optimal portfolio weights are determined via a **mean-variance utility model** (`Max U = E[r] − ½·A·Var[r]`), enabling the generator to tailor its hedging posture to its individual risk-aversion index *A*. Simulation results show the portfolio approach consistently outperforms both the unhedged baseline and any single-option strategy in terms of profit and risk reduction.

---

## Highlights

| # | Highlight |
|---|-----------|
| ✅ | Novel three-option hedging portfolio (short put + long put + short call) tailored for gas generators |
| ✅ | Dual energy storage integration: P2G and battery act as physical hedging buffers |
| ✅ | Mean-variance utility optimisation with configurable risk-aversion index *A* |
| ✅ | Estimation-invariant design — robust to demand and price forecast errors |
| ✅ | Outperforms traditional bilateral-contract hedging and single-option strategies |
| ✅ | Risk-preference sensitivity analysis: risk-averse → long put; risk-tolerant → short call |

---

## Project Architecture

```
gas-generator-option-hedging/
│
├── README.md
├── LICENSE
├── requirements.txt
├── setup.py
│
├── data/
│   ├── market_prices.csv
│   ├── gas_costs.csv
│   └── scenario_params.json
│
├── src/
│   ├── options/
│   │   ├── short_put.py         # Short put payoff, premium, constraint models
│   │   ├── long_put.py          # Long put payoff, transfer mechanism models
│   │   └── short_call.py        # Short call payoff and exercise logic
│   ├── storage/
│   │   ├── p2g.py               # Power-to-Gas charging/discharging model
│   │   └── battery.py           # Battery SOC dynamics and constraints
│   ├── portfolio/
│   │   ├── mean_variance.py     # Mean-variance utility: E[r] - 0.5·A·Var[r]
│   │   ├── optimiser.py         # QP weight optimisation
│   │   └── risk_metrics.py      # CVaR, Sharpe ratio, return distribution
│   └── utils/
│       ├── scenario_gen.py      # Scenario generation (price + demand)
│       └── plotting.py          # Efficient frontier and payoff profile plots
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_option_payoffs.ipynb
│   ├── 03_storage_simulation.ipynb
│   └── 04_portfolio_optimisation.ipynb
│
├── tests/
│   ├── test_options.py
│   ├── test_storage.py
│   └── test_portfolio.py
│
└── diagrams/
    ├── risk_flow_diagram.svg        # Research-grade risk-flow flowchart
    ├── portfolio_infographic.svg    # Stakeholder-facing portfolio infographic
    ├── risk_flow_diagram.png
    └── portfolio_infographic.png
```

---

## Installation

```bash
git clone https://github.com/your-org/gas-generator-option-hedging.git
cd gas-generator-option-hedging
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Key dependencies:**
```
numpy>=1.23 · scipy>=1.9 · pandas>=1.5 · cvxpy>=1.3 · matplotlib>=3.6 · seaborn>=0.12 · jupyter>=1.0 · pytest>=7.2
```

---

## Usage

```python
from src.options.short_put import ShortPut
from src.options.long_put import LongPut
from src.options.short_call import ShortCall
from src.storage.p2g import PowerToGas
from src.storage.battery import Battery
from src.portfolio.mean_variance import MeanVarianceOptimiser

short_put  = ShortPut(strike=80.0,  premium=5.0)
long_put   = LongPut(strike=80.0,   premium=4.5)
short_call = ShortCall(strike=80.0, premium=6.0)
p2g        = PowerToGas(capacity_mwh=50, efficiency=0.60)
battery    = Battery(capacity_mwh=30, charge_rate=10, efficiency=0.92)

optimiser = MeanVarianceOptimiser(
    instruments=[short_put, long_put, short_call, p2g, battery],
    risk_aversion=3, n_scenarios=1000, random_seed=42
)
result = optimiser.solve()
print(result.weights)
```

---

## Model Overview

```
Maximise:   U = E[r_portfolio(T)] − (1/2) · A · Var[r_portfolio(T)]

Subject to: Σ wᵢ = 1          (weights sum to 1)
            0 ≤ wᵢ ≤ 1        (no short-selling of instruments)
            SOC constraints     (battery state-of-charge bounds)
            P2G energy balance  (gas input = electrical output / η_P2G)
            Option exercise conditions (price vs. strike price)
```

---

## Assumptions

1. **Time resolution:** 30-minute slots (48/day)
2. **Strike price:** Uniform across options for baseline — extend if paper specifies instrument-level strikes
3. **Scenario generation:** 1,000 Monte Carlo scenarios unless paper specifies otherwise
4. **P2G efficiency:** 60%; battery round-trip: 92% — adjust from paper Table 1
5. **No transaction costs** beyond explicit premiums are modelled
6. **Risk-free rate:** Assumed zero

---

## Project Architecture in C++

```

OptionHedgingSystem/
├── CMakeLists.txt
├── cmake/
│   └── modules/
├── include/
│   ├── core/
│   ├── models/
│   ├── storage/
│   ├── optimization/
│   ├── simulation/
│   └── utils/
├── src/
│   ├── core/
│   ├── models/
│   ├── storage/
│   ├── optimization/
│   ├── simulation/
│   └── utils/
├── configs/
├── data/
├── tests/
└── examples/

```

## Citation

```bibtex
@article{lai2022option,
  title   = {Option-based portfolio risk hedging strategy for gas generator
             based on mean-variance utility model},
  author  = {Lai, Shuying and Qiu, Jing and Tao, Yuechuan},
  journal = {Energy Conversion and Economics},
  volume  = {3}, number = {1}, pages = {20--30}, year = {2022},
  doi     = {10.1049/enc2.12036}
}
```

## License

MIT — see [LICENSE](LICENSE). Not affiliated with or endorsed by the original authors.




---

### Project Structure Mapping

#### Mapping table

| **Module** | **File path** | **Paper section** | **Responsibility** |
|---|---:|---|---|
| **Data ingestion** | `src/data/load_data.py` | Data and price series | Load and validate historical spot price data |
| **Preprocessing** | `src/data/preprocess.py` | Data and price series | Clean, resample, and compute hourly statistics |
| **Option payoff models** | `src/models/options.py` | Option design and payoffs | Implement short put, long put, short call payoff functions |
| **Storage models** | `src/models/storage.py` | Energy storage integration | P2G and battery operational model and constraints |
| **Generator dispatch** | `src/models/generator.py` | Generator operation and bidding | Simulate generator dispatch and market clearing behavior |
| **Portfolio optimization** | `src/optimization/mean_variance.py` | Mean‑variance utility model | Compute expected return, variance, and optimal weights |
| **Scenario manager** | `src/scenarios/runner.py` | Scenario analysis | Run parameter sweeps for risk aversion and storage mix |
| **Simulation orchestrator** | `src/run_simulation.py` | Simulation experiments | End‑to‑end experiment runner and result exporter |
| **Plotting and figures** | `src/plotting/generate_all.py` | Results and figures | Create research and showcase diagrams |
| **Utilities** | `src/utils/*.py` | Methods and supplementary | Helper functions, constants, and IO |
| **Configs** | `configs/default.yaml` | Methods and reproducibility | Default parameters, seeds, and paths |
| **Notebooks** | `notebooks/analysis.ipynb` | Supplementary analysis | Interactive exploration and figure reproduction |

#### Brief file descriptions
- **`src/models/options.py`**  
  Implements payoff calculators for each option type and a portfolio payoff aggregator.
- **`src/models/storage.py`**  
  Encodes capacity, efficiency, fixed and variable costs, and charge/discharge scheduling heuristics.
- **`src/optimization/mean_variance.py`**  
  Computes expected portfolio payoff vector, covariance matrix, and solves for weights under a mean‑variance utility objective with risk aversion parameter gamma.
- **`src/scenarios/runner.py`**  
  Automates sweeps across gamma, storage mix ratios, and strike price sets and writes summary CSVs.

---

### Diagram Assets and Captions

#### General export recommendations
- **Primary format**: SVG for source diagrams.  
- **Secondary format**: PNG at 300 DPI for presentations.  
- **Layering**: keep logical layers for axes, annotations, and data traces to allow easy edits.  
- **Suggested export sizes**: research diagrams 1600×1200 px; showcase infographics 1200×800 px.

---

#### Research Grade Diagrams

1. **Risk Flow and System Interaction Diagram**  
   - **Filename**: `figures/research_risk_flow.svg`  
   - **Description**: Detailed flowchart showing generator dispatch, market clearing, option cashflows, storage charge/discharge loops, and net P&L aggregation.  
   - **Export**: SVG source; PNG export `research_risk_flow.png` 1600×1200 px.  
   - **Alt text**: Flowchart of generator, market, options, and storage interactions showing cashflow directions.  
   - **Caption**: Comprehensive system diagram linking operational decisions to option payoffs and storage actions.

2. **Option Payoff Interaction Matrix**  
   - **Filename**: `figures/research_option_payoffs.svg`  
   - **Description**: Multi‑panel plot with payoff curves for short put, long put, short call and combined portfolio payoff under sample weightings.  
   - **Export**: SVG and PNG `research_option_payoffs.png` 1600×900 px.  
   - **Alt text**: Payoff curves for short put long put and short call with combined portfolio overlay.  
   - **Caption**: Visual comparison of individual option payoffs and their combined effect on generator revenue.

3. **Mean Variance Frontier with Scenario Points**  
   - **Filename**: `figures/research_mean_variance_frontier.svg`  
   - **Description**: Efficient frontier plot with markers for no‑hedge, single‑option hedges, and optimal portfolio points for multiple gamma values and storage mixes.  
   - **Export**: SVG and PNG `research_mean_variance_frontier.png` 1600×900 px.  
   - **Alt text**: Mean variance frontier with labeled strategy points and storage mix annotations.  
   - **Caption**: Frontier showing tradeoffs and how storage and risk aversion shift optimal portfolios.

---

#### Portfolio Showcase Diagrams

1. **Payoff Snapshot Infographic**  
   - **Filename**: `figures/showcase_payoff_snapshot.svg`  
   - **Description**: Clean infographic showing simplified payoff bars for each option and a recommended portfolio mix for a medium risk profile.  
   - **Export**: SVG and PNG `showcase_payoff_snapshot.png` 1200×800 px.  
   - **Alt text**: Infographic with three payoff bars and recommended portfolio pie chart.  
   - **Caption**: Executive summary of option payoffs and recommended allocation for balanced risk appetite.

2. **Storage Role Visual**  
   - **Filename**: `figures/showcase_storage_role.svg`  
   - **Description**: Two‑panel visual comparing P2G and battery impacts on hedging outcomes with simple icons and one‑line takeaways.  
   - **Export**: SVG and PNG `showcase_storage_role.png` 1200×800 px.  
   - **Alt text**: Side by side comparison of P2G and battery showing capacity and cost tradeoffs.  
   - **Caption**: How storage type changes operational flexibility and hedging effectiveness.

3. **Recommended Portfolio Mix Card**  
   - **Filename**: `figures/showcase_portfolio_card.svg`  
   - **Description**: Single slide style card with pie chart of recommended weights, bullet takeaways, and a one‑line risk note.  
   - **Export**: SVG and PNG `showcase_portfolio_card.png` 1200×800 px.  
   - **Alt text**: Card showing pie chart of recommended option weights and three bullet points.  
   - **Caption**: Stakeholder friendly summary of the recommended option portfolio.

---

### Diagram design notes
- **Research diagrams** should include axis labels, units, legend, and small font annotations for reproducibility.  
- **Showcase diagrams** should prioritize clarity, large fonts, and minimal technical detail.  
- **Suggested layers for each SVG**: background, data traces, annotations, labels, export guides.

---

### Assumptions Made
- Historical price data is available and cleaned in `data/`.  
- Option premiums are either observed or computed via a simple pricing approximation consistent across scenarios.  
- Storage cost models are reduced to fixed capital cost plus per MWh variable cost and roundtrip efficiency.  
- Market clearing is modeled hourly with generator bidding behavior simplified to a price threshold rule.

---

### Reviewer Checklist
- **Data**: Confirm `data/aemo_prices_2016_2018.csv` is present and documented.  
- **Reproducibility**: Run `python -m src.run_simulation` and verify `results/` outputs.  
- **Figures**: Open `figures/*.svg` in an editor and confirm layers and labels.  
- **Configs**: Validate `configs/default.yaml` contains seeds and parameter ranges.  
- **Documentation**: Ensure `PROJECT_STRUCTURE.md` and `DIAGRAMS.md` match actual file names.

---
 
