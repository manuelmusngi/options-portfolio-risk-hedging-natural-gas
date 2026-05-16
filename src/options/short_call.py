"""
Short Call Option Model
=======================
The gas generator acts as **option seller** (writer) of a call option.

Mechanics (paper §5)
--------------------
- Generator receives premium P_sc upfront.
- If S > K at exercise: generator must sell electricity at K (below market).
- Net payoff per MWh per slot:

      payoff(S) = premium  -  max(S - K, 0)

Risk profile
------------
- Downside: theoretically unlimited as S → ∞.
- Upside:   capped at premium (retained when S ≤ K).
- Battery can partially offset the sell-obligation via discharge at peak prices.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class ShortCallResult:
    spot_prices: np.ndarray
    payoffs: np.ndarray
    premiums: np.ndarray
    obligation_costs: np.ndarray
    exercised_mask: np.ndarray
    expected_payoff: float
    payoff_variance: float
    exercise_probability: float

    def summary(self) -> dict:
        return {
            "expected_payoff": self.expected_payoff,
            "payoff_variance": self.payoff_variance,
            "payoff_std": np.sqrt(self.payoff_variance),
            "exercise_probability": self.exercise_probability,
            "min_payoff": float(self.payoffs.min()),
            "max_payoff": float(self.payoffs.max()),
            "premium": float(self.premiums[0] if self.premiums.ndim == 1 else self.premiums[0, 0]),
        }


class ShortCall:
    """
    Short Call option instrument for gas generator hedging.

    Parameters
    ----------
    strike : float      Strike K [$/MWh]. Exercised when S > K.
    premium : float     Premium received [$/MWh].
    volume_mwh : float  Contracted volume [MWh]. Default 1.
    """

    instrument_type: str = "short_call"

    def __init__(
        self,
        strike: float,
        premium: float,
        volume_mwh: float = 1.0,
        name: str = "ShortCall",
    ) -> None:
        if strike <= 0:
            raise ValueError(f"Strike must be positive, got {strike}")
        if premium < 0:
            raise ValueError(f"Premium must be non-negative, got {premium}")
        if volume_mwh <= 0:
            raise ValueError(f"Volume must be positive, got {volume_mwh}")
        self.strike = float(strike)
        self.premium = float(premium)
        self.volume_mwh = float(volume_mwh)
        self.name = name

    def payoff(self, spot_prices: np.ndarray) -> np.ndarray:
        """payoff(S) = (premium - max(S - K, 0)) * volume_mwh"""
        S = np.asarray(spot_prices, dtype=float)
        obligation = np.maximum(S - self.strike, 0.0)
        return (self.premium - obligation) * self.volume_mwh

    def premium_income(self, spot_prices: np.ndarray) -> np.ndarray:
        S = np.asarray(spot_prices, dtype=float)
        return np.full_like(S, self.premium * self.volume_mwh)

    def obligation_cost(self, spot_prices: np.ndarray) -> np.ndarray:
        S = np.asarray(spot_prices, dtype=float)
        return np.maximum(S - self.strike, 0.0) * self.volume_mwh

    def is_exercised(self, spot_prices: np.ndarray) -> np.ndarray:
        S = np.asarray(spot_prices, dtype=float)
        return S > self.strike

    def evaluate(
        self,
        spot_prices: np.ndarray,
        scenario_probs: Optional[np.ndarray] = None,
    ) -> ShortCallResult:
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

        return ShortCallResult(
            spot_prices=S, payoffs=payoffs_raw, premiums=premium_arr,
            obligation_costs=obligation_arr, exercised_mask=exercised,
            expected_payoff=exp_payoff, payoff_variance=var_payoff,
            exercise_probability=exercise_prob,
        )

    def revenue_cost_breakdown(self, spot_prices: np.ndarray) -> dict:
        S = np.asarray(spot_prices, dtype=float)
        return {
            "premium_income": float(self.premium_income(S).mean()),
            "obligation_cost": float(self.obligation_cost(S).mean()),
            "net_payoff": float(self.payoff(S).mean()),
            "exercise_probability": float((S > self.strike).mean()),
        }

    def __repr__(self) -> str:
        return (
            f"ShortCall(strike={self.strike}, premium={self.premium}, "
            f"volume={self.volume_mwh} MWh)"
        )
