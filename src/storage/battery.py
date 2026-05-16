"""
Battery Energy Storage Model
=============================
Physical model (paper §6):
  SOC(t+1) = SOC(t) + η_c*P_charge(t)*Δt/E_cap
                     − P_discharge(t)*Δt/(η_d*E_cap)

Constraints:
  SOC_min ≤ SOC(t) ≤ SOC_max
  0 ≤ P_charge(t) ≤ P_charge_max
  0 ≤ P_discharge(t) ≤ P_discharge_max
  No simultaneous charge and discharge
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class BatterySimResult:
    n_slots: int
    time_hours: np.ndarray
    soc: np.ndarray              # shape (N+1,)
    energy_mwh: np.ndarray       # shape (N+1,)
    charge_mw: np.ndarray        # shape (N,)
    discharge_mw: np.ndarray     # shape (N,)
    net_power_mw: np.ndarray
    total_energy_charged: float
    total_energy_discharged: float
    cycle_count: float
    avg_soc: float
    final_soc: float

    def summary(self) -> dict:
        return {
            "n_slots": self.n_slots,
            "total_charged_mwh": self.total_energy_charged,
            "total_discharged_mwh": self.total_energy_discharged,
            "cycle_count": self.cycle_count,
            "avg_soc": self.avg_soc,
            "final_soc": self.final_soc,
            "min_soc": float(self.soc.min()),
            "max_soc": float(self.soc.max()),
        }


class Battery:
    """
    Battery energy storage device with SOC dynamics.

    Parameters
    ----------
    capacity_mwh : float            Nominal capacity [MWh]. Default 30.
    max_charge_rate_mw : float      Max charging power [MW]. Default 10.
    max_discharge_rate_mw : float   Max discharging power [MW]. Default 10.
    efficiency_charge : float       η_c ∈ (0,1]. Default 0.96.
    efficiency_discharge : float    η_d ∈ (0,1]. Default 0.96.
    soc_min : float                 Min SOC [0,1). Default 0.10.
    soc_max : float                 Max SOC (soc_min,1]. Default 0.90.
    initial_soc : float             Initial SOC. Default 0.50.
    slot_hours : float              Slot duration [h]. Default 0.5.

    Notes
    -----
    Round-trip efficiency = η_c * η_d ≈ 0.92
    """

    instrument_type: str = "battery"

    def __init__(
        self,
        capacity_mwh: float = 30.0,
        max_charge_rate_mw: float = 10.0,
        max_discharge_rate_mw: float = 10.0,
        efficiency_charge: float = 0.96,
        efficiency_discharge: float = 0.96,
        soc_min: float = 0.10,
        soc_max: float = 0.90,
        initial_soc: float = 0.50,
        slot_hours: float = 0.5,
        name: str = "Battery",
    ) -> None:
        if capacity_mwh <= 0:
            raise ValueError("Capacity must be positive")
        if not 0 < efficiency_charge <= 1:
            raise ValueError(f"Charge efficiency must be in (0,1], got {efficiency_charge}")
        if not 0 < efficiency_discharge <= 1:
            raise ValueError(f"Discharge efficiency must be in (0,1], got {efficiency_discharge}")
        if not 0 <= soc_min < soc_max <= 1:
            raise ValueError(f"SOC bounds invalid: min={soc_min}, max={soc_max}")
        if not soc_min <= initial_soc <= soc_max:
            raise ValueError(f"Initial SOC {initial_soc} outside bounds [{soc_min}, {soc_max}]")

        self.capacity_mwh = float(capacity_mwh)
        self.max_charge_rate_mw = float(max_charge_rate_mw)
        self.max_discharge_rate_mw = float(max_discharge_rate_mw)
        self.efficiency_charge = float(efficiency_charge)
        self.efficiency_discharge = float(efficiency_discharge)
        self.soc_min = float(soc_min)
        self.soc_max = float(soc_max)
        self.initial_soc = float(initial_soc)
        self.slot_hours = float(slot_hours)
        self.name = name
        self._soc = self.initial_soc

    @property
    def soc(self) -> float:
        return self._soc

    @property
    def energy_mwh(self) -> float:
        return self._soc * self.capacity_mwh

    @property
    def available_charge_mwh(self) -> float:
        return (self.soc_max - self._soc) * self.capacity_mwh

    @property
    def available_discharge_mwh(self) -> float:
        return (self._soc - self.soc_min) * self.capacity_mwh

    @property
    def round_trip_efficiency(self) -> float:
        return self.efficiency_charge * self.efficiency_discharge

    def reset(self) -> None:
        self._soc = self.initial_soc

    def step(self, charge_mw: float = 0.0, discharge_mw: float = 0.0) -> dict:
        if charge_mw > 0 and discharge_mw > 0:
            discharge_mw = 0.0
        c = float(np.clip(charge_mw, 0.0, self.max_charge_rate_mw))
        d = float(np.clip(discharge_mw, 0.0, self.max_discharge_rate_mw))

        delta_charge = self.efficiency_charge * c * self.slot_hours
        delta_discharge = d * self.slot_hours / max(self.efficiency_discharge, 1e-9)

        new_energy = float(np.clip(
            self.energy_mwh + delta_charge - delta_discharge,
            self.soc_min * self.capacity_mwh,
            self.soc_max * self.capacity_mwh,
        ))
        new_soc = new_energy / self.capacity_mwh

        actual_charge_energy = max(new_energy - self.energy_mwh + delta_discharge, 0.0)
        actual_discharge_energy = max(self.energy_mwh + delta_charge - new_energy, 0.0)
        actual_c = actual_charge_energy / max(self.efficiency_charge * self.slot_hours, 1e-9)
        actual_d = actual_discharge_energy * self.efficiency_discharge / max(self.slot_hours, 1e-9)

        self._soc = new_soc
        return {
            "soc": self._soc, "energy_mwh": self.energy_mwh,
            "actual_charge_mw": actual_c, "actual_discharge_mw": actual_d,
            "net_power_mw": actual_d - actual_c,
        }

    def simulate(
        self,
        charge_schedule_mw: np.ndarray,
        discharge_schedule_mw: Optional[np.ndarray] = None,
    ) -> BatterySimResult:
        n = len(charge_schedule_mw)
        if discharge_schedule_mw is None:
            discharge_schedule_mw = np.zeros(n)

        self.reset()
        soc_arr = np.zeros(n + 1)
        energy_arr = np.zeros(n + 1)
        c_arr = np.zeros(n)
        d_arr = np.zeros(n)
        soc_arr[0] = self._soc
        energy_arr[0] = self.energy_mwh

        for t in range(n):
            info = self.step(
                charge_mw=float(charge_schedule_mw[t]),
                discharge_mw=float(discharge_schedule_mw[t]),
            )
            soc_arr[t + 1] = info["soc"]
            energy_arr[t + 1] = info["energy_mwh"]
            c_arr[t] = info["actual_charge_mw"]
            d_arr[t] = info["actual_discharge_mw"]

        time_h = np.arange(n) * self.slot_hours
        total_c = float((c_arr * self.slot_hours).sum())
        total_d = float((d_arr * self.slot_hours).sum())

        return BatterySimResult(
            n_slots=n, time_hours=time_h, soc=soc_arr, energy_mwh=energy_arr,
            charge_mw=c_arr, discharge_mw=d_arr, net_power_mw=d_arr - c_arr,
            total_energy_charged=total_c, total_energy_discharged=total_d,
            cycle_count=total_c / max(self.capacity_mwh, 1e-9),
            avg_soc=float(soc_arr[1:].mean()), final_soc=float(soc_arr[-1]),
        )

    def greedy_arbitrage_schedule(
        self,
        spot_prices: np.ndarray,
        threshold_buy: Optional[float] = None,
        threshold_sell: Optional[float] = None,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Greedy price-arbitrage schedule: charge at low prices, discharge at high prices."""
        S = np.asarray(spot_prices, dtype=float)
        if threshold_buy is None:
            threshold_buy = float(np.median(S))
        if threshold_sell is None:
            threshold_sell = float(np.percentile(S, 75))

        n = len(S)
        charge_sched = np.zeros(n)
        discharge_sched = np.zeros(n)
        self.reset()
        for t, price in enumerate(S):
            if price < threshold_buy and self.available_charge_mwh > 1e-6:
                charge_sched[t] = self.max_charge_rate_mw
                self.step(charge_mw=self.max_charge_rate_mw)
            elif price > threshold_sell and self.available_discharge_mwh > 1e-6:
                discharge_sched[t] = self.max_discharge_rate_mw
                self.step(discharge_mw=self.max_discharge_rate_mw)
            else:
                self.step()
        return charge_sched, discharge_sched

    def __repr__(self) -> str:
        return (
            f"Battery(capacity={self.capacity_mwh} MWh, "
            f"RTE={self.round_trip_efficiency:.0%}, "
            f"SOC=[{self.soc_min:.0%},{self.soc_max:.0%}], "
            f"current={self._soc:.1%})"
        )
