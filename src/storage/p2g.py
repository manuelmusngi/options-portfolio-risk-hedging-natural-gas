"""
Power-to-Gas (P2G) Storage Model
=================================
Physical model (paper §6):
  level(t+1) = level(t) + η_P2G * P_charge(t)*Δt − P_discharge(t)*Δt

Constraints:
  0 ≤ level(t) ≤ capacity_mwh
  0 ≤ P_charge(t) ≤ max_charge_rate
  0 ≤ P_discharge(t) ≤ max_discharge_rate
  No simultaneous charge and discharge
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class P2GSimResult:
    n_slots: int
    time_hours: np.ndarray
    level_mwh: np.ndarray        # shape (N+1,)
    charge_mw: np.ndarray        # shape (N,)
    discharge_mw: np.ndarray     # shape (N,)
    elec_absorbed_mwh: np.ndarray
    total_elec_absorbed: float
    total_gas_discharged: float
    avg_level: float
    final_level: float

    def summary(self) -> dict:
        return {
            "n_slots": self.n_slots,
            "total_elec_absorbed_mwh": self.total_elec_absorbed,
            "total_gas_discharged_mwh": self.total_gas_discharged,
            "avg_level_mwh": self.avg_level,
            "final_level_mwh": self.final_level,
            "max_level_mwh": float(self.level_mwh.max()),
        }


class PowerToGas:
    """
    Power-to-Gas energy storage device.

    Parameters
    ----------
    capacity_mwh : float        Max gas energy capacity [MWh]. Default 50.
    efficiency : float          Electrolysis efficiency η ∈ (0,1]. Default 0.60.
    max_charge_rate_mw : float  Max electrical input [MW]. Default 10.
    max_discharge_rate_mw : float Max gas output [MW]. Default 8.
    initial_level_mwh : float   Initial gas stored [MWh]. Default 0.
    slot_hours : float          Slot duration [h]. Default 0.5.
    """

    instrument_type: str = "p2g"

    def __init__(
        self,
        capacity_mwh: float = 50.0,
        efficiency: float = 0.60,
        max_charge_rate_mw: float = 10.0,
        max_discharge_rate_mw: float = 8.0,
        initial_level_mwh: float = 0.0,
        slot_hours: float = 0.5,
        name: str = "P2G",
    ) -> None:
        if capacity_mwh <= 0:
            raise ValueError(f"Capacity must be positive, got {capacity_mwh}")
        if not 0 < efficiency <= 1:
            raise ValueError(f"Efficiency must be in (0,1], got {efficiency}")
        if not 0 <= initial_level_mwh <= capacity_mwh:
            raise ValueError(f"Initial level {initial_level_mwh} must be in [0, {capacity_mwh}]")

        self.capacity_mwh = float(capacity_mwh)
        self.efficiency = float(efficiency)
        self.max_charge_rate_mw = float(max_charge_rate_mw)
        self.max_discharge_rate_mw = float(max_discharge_rate_mw)
        self.initial_level_mwh = float(initial_level_mwh)
        self.slot_hours = float(slot_hours)
        self.name = name
        self._level = self.initial_level_mwh

    def reset(self) -> None:
        self._level = self.initial_level_mwh

    def step(self, charge_mw: float = 0.0, discharge_mw: float = 0.0) -> dict:
        act_charge = float(np.clip(charge_mw, 0.0, self.max_charge_rate_mw))
        act_discharge = float(np.clip(discharge_mw, 0.0, self.max_discharge_rate_mw))
        if act_charge > 0 and act_discharge > 0:
            act_discharge = 0.0

        gas_in = self.efficiency * act_charge * self.slot_hours
        gas_out = act_discharge * self.slot_hours
        new_level = float(np.clip(self._level + gas_in - gas_out, 0.0, self.capacity_mwh))
        actual_gas_out = self._level + gas_in - new_level
        actual_discharge = actual_gas_out / self.slot_hours if self.slot_hours > 0 else 0.0
        self._level = new_level

        return {
            "level": self._level,
            "actual_charge_mw": act_charge,
            "actual_discharge_mw": actual_discharge,
            "elec_absorbed_mwh": act_charge * self.slot_hours,
            "gas_stored_mwh": gas_in,
        }

    def simulate(
        self,
        charge_schedule_mw: np.ndarray,
        discharge_schedule_mw: Optional[np.ndarray] = None,
    ) -> P2GSimResult:
        n = len(charge_schedule_mw)
        if discharge_schedule_mw is None:
            discharge_schedule_mw = np.zeros(n)

        self.reset()
        levels = np.zeros(n + 1)
        charges = np.zeros(n)
        discharges = np.zeros(n)
        elec_abs = np.zeros(n)
        levels[0] = self._level

        for t in range(n):
            info = self.step(
                charge_mw=float(charge_schedule_mw[t]),
                discharge_mw=float(discharge_schedule_mw[t]),
            )
            levels[t + 1] = info["level"]
            charges[t] = info["actual_charge_mw"]
            discharges[t] = info["actual_discharge_mw"]
            elec_abs[t] = info["elec_absorbed_mwh"]

        time_h = np.arange(n) * self.slot_hours
        return P2GSimResult(
            n_slots=n, time_hours=time_h, level_mwh=levels,
            charge_mw=charges, discharge_mw=discharges,
            elec_absorbed_mwh=elec_abs,
            total_elec_absorbed=float(elec_abs.sum()),
            total_gas_discharged=float(discharges.sum() * self.slot_hours),
            avg_level=float(levels[1:].mean()),
            final_level=float(levels[-1]),
        )

    def greedy_absorption_schedule(self, excess_power_mw: np.ndarray) -> np.ndarray:
        """Build greedy charging schedule to absorb excess electricity (short-put support)."""
        self.reset()
        schedule = np.zeros(len(excess_power_mw))
        for t, avail in enumerate(excess_power_mw):
            remaining_cap = self.capacity_mwh - self._level
            max_elec_in = remaining_cap / max(self.efficiency, 1e-9) / self.slot_hours
            charge = float(np.clip(avail, 0.0, min(self.max_charge_rate_mw, max_elec_in)))
            info = self.step(charge_mw=charge, discharge_mw=0.0)
            schedule[t] = info["actual_charge_mw"]
        return schedule

    @property
    def level(self) -> float:
        return self._level

    def __repr__(self) -> str:
        return (
            f"PowerToGas(capacity={self.capacity_mwh} MWh, "
            f"η={self.efficiency:.0%}, "
            f"max_charge={self.max_charge_rate_mw} MW)"
        )
