"""
Short Put Option Model
======================
The gas generator acts as **option seller** (writer) of a put option.

Mechanics (paper §3)
--------------------
- The generator receives a premium P_sp upfront from the option buyer.
- If the market spot price S falls below the strike price K at exercise time,
  the option buyer exercises: the generator is obligated to purchase a
  contracted volume of electricity at price K (above market value).
- The purchased electricity is absorbed by P2G storage or resold.
- Net payoff per MWh per slot:

      payoff(S) = premium  -  max(K - S, 0)

  i.e., premium income minus the forced-purchase loss when S < K.

Risk profile
------------
- Downside: unlimited loss as S → 0 (bounded in practice by price floor).
- Upside:   capped at premium (retained when S ≥ K, option not exercised).
- Preferred by generators with moderate-to-low risk aversion who seek
  consistent premium income.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ShortPutResult:
    """Container for ShortPut payoff computation results."""

    spot_prices: np.ndarray          # Shape (n,) – spot prices evaluated
    payoffs: np.ndarray              # Shape (n,) – net payoff per MWh
    premiums: np.ndarray             # Shape (n,) – premium component (constant)
    obligation_costs: np.ndarray     # Shape (n,) – max(K-S,0) component
    exercised_mask: np.ndarray       # Shape (n,) – bool: True where option exercised
    expected_payoff: float           # E[payoff]
    payoff_variance: float           # Var[payoff]
    exercise_probability: float      # Pr(S < K)

    def summary(self) -> dict:
        return {
            "expected_payoff": self.expected_payoff,
            "payoff_variance": self.payoff_variance,
            "payoff_std": np.sqrt(self.payoff_variance),
            "exercise_probability": self.exercise_probability,
            "min_payoff": float(self.payoffs.min()),
            "max_payoff": float(self.payoffs.max()),
            "premium": float(self.premiums[0]),
        }


class ShortPut:
    """
    Short Put option instrument for gas generator hedging.

    Parameters
    ----------
    strike : float
        Strike price K in $/MWh. Option is exercised when spot price S < K.
    premium : float
        Premium P_sp received by the generator (option seller) at inception,
        in $/MWh. Must be non-negative.
    volume_mwh : float
        Contracted electricity volume in MWh per time slot.
    name : str
        Instrument identifier.

    Examples
    --------
    >>> sp = ShortPut(strike=80.0, premium=5.0)
    >>> sp.payoff(np.array([60.0, 80.0, 100.0]))
    array([-15.,   5.,   5.])
    """

    instrument_type: str = "short_put"

    def __init__(
        self,
        strike: float,
        premium: float,
        volume_mwh: float = 1.0,
        name: str = "ShortPut",
    ) -> None:
        if strike <= 0:
            raise ValueError(f"Strike price must be positive, got {strike}")
        if premium < 0:
            raise ValueError(f"Premium must be non-negative, got {premium}")
        if volume_mwh <= 0:
            raise ValueError(f"Volume must be positive, got {volume_mwh}")

        self.strike = float(strike)
        self.premium = float(premium)
        self.volume_mwh = float(volume_mwh)
        self.name = name

    def payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        """payoff(S) = (premium - max(K - S, 0)) * volume_mwh"""
        S = np.asarray(spot_prices, dtype=float)
        obligation = np.maximum(self.strike - S, 0.0)
        return (self.premium - obligation) * self.volume_mwh

    def premium_income(self, spot_prices: np.ndarray) -> np.ndarray:
        S = np.asarray(spot_prices, dtype=float)
        return np.full_like(S, self.premium * self.volume_mwh)

    def obligation_cost(self, spot_prices: np.ndarray) -> np.ndarray:
        S = np.asarray(spot_prices, dtype=float)
        return np.maximum(self.strike - S, 0.0) * self.volume_mwh

    def is_exercised(self, spot_prices: np.ndarray) -> np.ndarray:
        S = np.asarray(spot_prices, dtype=float)
        return S < self.strike

    def evaluate(
        self,
        spot_prices: np.ndarray,
        scenario_probs: Optional[np.ndarray] = None,
    ) -> ShortPutResult:
        S = np.asarray(spot_prices, dtype=float)
        flat = S.ndim == 1
        if not flat:
            payoffs_raw = self.payoff(S).sum(axis=1)
            premium_arr = self.premium_income(S).sum(axis=1)
            obligation_arr = self.obligation_cost(S).sum(axis=1)
            exercised = self.is_exercised(S).any(axis=1)
        else:
            payoffs_raw = self.payoff(S)
            premium_arr = self.premium_income(S)
            obligation_arr = self.obligation_cost(S)
            exercised = self.is_exercised(S)

        n = len(payoffs_raw)
        probs = (
            np.asarray(scenario_probs, dtype=float)
            if scenario_probs is not None
            else np.full(n, 1.0 / n)
        )
        probs = probs / probs.sum()
        exp_payoff = float(np.dot(probs, payoffs_raw))
        var_payoff = float(np.dot(probs, (payoffs_raw - exp_payoff) ** 2))
        exercise_prob = float(np.dot(probs, exercised.astype(float)))

        return ShortPutResult(
            spot_prices=S,
            payoffs=payoffs_raw,
            premiums=premium_arr,
            obligation_costs=obligation_arr,
            exercised_mask=exercised,
            expected_payoff=exp_payoff,
            payoff_variance=var_payoff,
            exercise_probability=exercise_prob,
        )

    def revenue_cost_breakdown(self, spot_prices: np.ndarray) -> dict:
        S = np.asarray(spot_prices, dtype=float)
        return {
            "premium_income": float(self.premium_income(S).mean()),
            "obligation_cost": float(self.obligation_cost(S).mean()),
            "net_payoff": float(self.payoff(S).mean()),
            "exercise_probability": float((S < self.strike).mean()),
        }

    def __repr__(self) -> str:
        return (
            f"ShortPut(strike={self.strike}, premium={self.premium}, "
            f"volume={self.volume_mwh} MWh)"
        )
