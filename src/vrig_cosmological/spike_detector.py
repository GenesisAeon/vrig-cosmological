"""Detect v_RIG spikes in UTAC parameter time series.

A spike occurs when the Fisher-Rao geodesic speed in UTAC parameter space
exceeds the normalised v_RIG threshold. Spike events are interpreted as
precursors to phase-transition / regime-shift events.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from vrig_cosmological.constants import V_RIG_KM_S
from vrig_cosmological.information_geometry import (
    FisherRaoMetric,
    FisherRaoVelocityTimeSeries,
    UTACState,
)


@dataclass(frozen=True)
class SpikeEvent:
    """A detected v_RIG spike."""

    time: float
    speed: float  # Fisher-Rao speed at spike
    threshold: float
    excess: float  # speed - threshold


class VRIGSpikeDetector:
    """Detect v_RIG spikes in UTAC parameter time series.

    The Fisher-Rao speed is computed for a sequence of (r, K, σ) snapshots.
    Any moment where speed > threshold is flagged as a spike.

    Threshold is normalised: the physical v_RIG ≈ 1352 km/s is mapped to
    parameter-space units via a user-supplied normalisation factor.

    Prediction: spike precedes UTAC phase-transition event (H* crossing)
    by a time τ ≈ T₁ / v_RIG_normalised.
    """

    def __init__(
        self,
        threshold_normalised: float = 1.0,
        metric: FisherRaoMetric | None = None,
        min_gap: float = 0.5,
    ) -> None:
        """
        Parameters
        ----------
        threshold_normalised:
            Threshold in normalised Fisher-Rao units. Default 1.0 means the
            threshold equals the normalised v_RIG value. Scale from physical
            km/s using your dataset's normalisation.
        metric:
            Fisher-Rao metric instance (default: unit metric).
        min_gap:
            Minimum time between two consecutive spike events (avoids
            double-counting a broad peak).
        """
        self._threshold = threshold_normalised
        self._ts = FisherRaoVelocityTimeSeries(metric)
        self._min_gap = min_gap

    # ------------------------------------------------------------------

    def detect(self, states: list[UTACState]) -> list[SpikeEvent]:
        """Run spike detection on a UTAC state sequence."""
        if len(states) < 2:
            return []

        speeds = self._ts.compute(states)
        times = self._ts.times(states)

        spikes: list[SpikeEvent] = []
        last_t = -np.inf

        for t, sp in zip(times, speeds, strict=False):
            if sp > self._threshold and (t - last_t) >= self._min_gap:
                spikes.append(
                    SpikeEvent(
                        time=float(t),
                        speed=float(sp),
                        threshold=self._threshold,
                        excess=float(sp - self._threshold),
                    )
                )
                last_t = t

        return spikes

    # ------------------------------------------------------------------
    # Synthetic ERA5 analogue for testing

    @staticmethod
    def synthetic_era5_states(
        n_years: int = 83,
        start_year: float = 1940.0,
        regime_shift_year: float = 1998.0,
        base_r: float = 0.3,
        base_K: float = 1.0,
        base_sigma: float = 2.2,
        noise_scale: float = 0.02,
        spike_scale: float = 5.0,
        rng_seed: int = 42,
    ) -> list[UTACState]:
        """Generate synthetic ERA5-like UTAC parameter trajectory.

        Produces a smooth logistic trajectory with a sharp parameter change
        at `regime_shift_year` that creates a v_RIG spike — simulating the
        observed ~1998 AMOC/Arctic regime shift.
        """
        rng = np.random.default_rng(rng_seed)
        dt = 1.0
        times = np.arange(n_years, dtype=float) * dt

        r_series = base_r + noise_scale * rng.standard_normal(n_years)
        K_series = base_K + noise_scale * rng.standard_normal(n_years)
        s_series = base_sigma + noise_scale * rng.standard_normal(n_years)

        # Inject spike at regime-shift year
        shift_idx = int(regime_shift_year - start_year)
        if 0 <= shift_idx < n_years:
            r_series[shift_idx] += spike_scale * base_r
            K_series[shift_idx] += spike_scale * 0.1 * base_K
            s_series[shift_idx] += spike_scale * 0.5 * base_sigma

        return [
            UTACState(t=start_year + float(times[i]), r=float(r_series[i]),
                      K=float(K_series[i]), sigma=float(s_series[i]))
            for i in range(n_years)
        ]

    # ------------------------------------------------------------------

    @property
    def threshold(self) -> float:
        return self._threshold

    def __repr__(self) -> str:
        return f"VRIGSpikeDetector(threshold={self._threshold}, v_RIG_ref={V_RIG_KM_S:.2f} km/s)"
