#### Options-Based Portfolio Risk Hedging for Natural Gas

This project is an exercise on a research-grade options strategies hedging implementation in Henry Hub Natural Gas (NG) portfolio. 

---

🌊 Abstract

Natural gas generators face significant operational risks in electricity markets due to price volatility and uncertain demand. This repository implements the **option-based portfolio risk-hedging framework** proposed by Lai et al. (2022), which combines three financial option instruments — **short put**, **long put**, and **short call** — with two energy storage technologies — **Power-to-Gas (P2G)** and **battery** — to maximize the risk-adjusted utility of a gas generator. 

Optimal portfolio weights are determined via a **mean-variance utility model** - $$Max U = E[r] − ½·A·Var[r]$$, enabling the generator to tailor its hedging posture to its individual risk-aversion. 

Simulation results show the portfolio approach consistently outperforms both the unhedged baseline and any single-option strategy in terms of profit and risk reduction.

---

✨ Highlights

| # | Highlight |
|---|-----------|
| ✅ | Novel three-option hedging portfolio (short put + long put + short call) tailored for gas generators |
| ✅ | Dual energy storage integration: P2G and battery act as physical hedging buffers |
| ✅ | Mean-variance utility optimisation with configurable risk-aversion |
| ✅ | Estimation-invariant design — robust to demand and price forecast errors |
| ✅ | Outperforms traditional bilateral-contract hedging and single-option strategies |
| ✅ | Risk-preference sensitivity analysis: risk-averse → long put; risk-tolerant → short call |

---
🏗️ Project Architecture - C++

OptionHedgingSystem/\
├── CMakeLists.txt\
├── cmake/\
│   └── modules/\
├── include/\
│   ├── core/\
│   ├── models/\
│   ├── storage/\
│   ├── optimization/\
│   ├── simulation/\
│   └── utils/\
├── src/\
│   ├── core/\
│   ├── models/\
│   ├── storage/\
│   ├── optimization/\
│   ├── simulation/\
│   └── utils/\
├── configs/\
├── data/\
├── tests/\
└── examples/

---
>📄 **Research Paper Reference:** Lai, S., Qiu, J., & Tao, Y. (2022). Options-based portfolio risk hedging strategy for gas generator based on mean-variance utility model. > *Energy Conversion and Economics*, 3(1), 20–30.
-  DOI: [10.1049/enc2.12036](https://doi.org/10.1049/enc2.12036)


---
📄 License

MIT — see [LICENSE](LICENSE). Not affiliated with or endorsed by the original authors.
