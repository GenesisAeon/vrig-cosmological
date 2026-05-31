"""Fisher-Rao metric on the UTAC parameter manifold → v_RIG velocity.

The UTAC ODE has parameters θ = (r, K, σ). The Fisher-Rao metric g_ij
is the information-geometric metric on the statistical manifold of UTAC
distributions. The geodesic speed in this metric gives v_RIG(t).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray


@dataclass
class UTACState:
    """Snapshot of UTAC parameters at a single time point."""

    t: float
    r: float  # logistic growth rate
    K: float  # carrying capacity
    sigma: float  # UTAC coupling / sharpness


class FisherRaoMetric:
    """Fisher-Rao information metric on the UTAC parameter space {r, K, σ}.

    The metric tensor is approximated by the Hessian of the log-likelihood
    of the logistic UTAC model:

        g_ij(θ) ≈ -E[∂² log p(H|θ) / ∂θᵢ ∂θⱼ]

    For the logistic model this reduces to diagonal entries:
        g_rr  ∝ 1/r²
        g_KK  ∝ 1/K²
        g_σσ  ∝ 1

    Geodesic speed:
        v(t) = √(g_ij · θ̇ⁱ · θ̇ʲ)
    """

    def __init__(self, scale_r: float = 1.0, scale_K: float = 1.0, scale_sigma: float = 1.0) -> None:
        self._sr = scale_r
        self._sK = scale_K
        self._ss = scale_sigma

    def metric_diagonal(self, state: UTACState) -> tuple[float, float, float]:
        """Return (g_rr, g_KK, g_σσ) at the given state."""
        g_rr = self._sr / (state.r ** 2 + 1e-12)
        g_KK = self._sK / (state.K ** 2 + 1e-12)
        g_ss = self._ss
        return g_rr, g_KK, g_ss

    def geodesic_speed(
        self,
        state: UTACState,
        dtheta_dt: tuple[float, float, float],
    ) -> float:
        """Compute Fisher-Rao geodesic speed ||θ̇||_g."""
        g_rr, g_KK, g_ss = self.metric_diagonal(state)
        dr, dK, ds = dtheta_dt
        return math.sqrt(g_rr * dr**2 + g_KK * dK**2 + g_ss * ds**2)


class FisherRaoVelocityTimeSeries:
    """Compute Fisher-Rao velocity from a sequence of UTAC states."""

    def __init__(self, metric: FisherRaoMetric | None = None) -> None:
        self._metric = metric or FisherRaoMetric()

    def compute(self, states: list[UTACState]) -> NDArray[np.float64]:
        """Return an array of Fisher-Rao speeds for each consecutive pair.

        Output length = len(states) - 1.
        """
        if len(states) < 2:
            return np.array([], dtype=np.float64)

        velocities: list[float] = []
        for i in range(len(states) - 1):
            s0, s1 = states[i], states[i + 1]
            dt = s1.t - s0.t
            if abs(dt) < 1e-15:
                velocities.append(0.0)
                continue
            dtheta = (
                (s1.r - s0.r) / dt,
                (s1.K - s0.K) / dt,
                (s1.sigma - s0.sigma) / dt,
            )
            v = self._metric.geodesic_speed(s0, dtheta)
            velocities.append(v)

        return np.array(velocities, dtype=np.float64)

    def times(self, states: list[UTACState]) -> NDArray[np.float64]:
        """Midpoint timestamps for each velocity estimate."""
        return np.array(
            [(states[i].t + states[i + 1].t) / 2.0 for i in range(len(states) - 1)],
            dtype=np.float64,
        )
