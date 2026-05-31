"""Cosmological peculiar-velocity context for v_RIG.

Compares v_RIG ≈ 1352 km/s to observed peculiar velocity scales and
tests the prediction that v_RIG appears as a characteristic scale in
galaxy peculiar-velocity surveys.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from vrig_cosmological.constants import V_CMB_DIPOLE_KM_S, V_RIG_KM_S


# Reference peculiar velocity scales (km/s), literature values
REFERENCE_SCALES: dict[str, float] = {
    "CMB_dipole":            369.82,   # Planck 2018
    "Virgo_infall":          250.0,    # Local infall toward Virgo cluster
    "Great_Attractor":       600.0,    # Centaurus / Norma attractor
    "Shapley_infall":        800.0,    # Shapley supercluster
    "AMOC_analogue":         1000.0,   # Ocean current analogue scale
    "v_RIG":                 V_RIG_KM_S,  # This framework
    "Local_Group_wrt_CMB":   627.0,    # LG bulk flow
    "CF4_bulk_flow_100Mpc":  180.0,    # CosmicFlows-4 (Tully+ 2023)
}


@dataclass(frozen=True)
class PeculiarVelocityComparison:
    """Result of comparing v_RIG to a reference scale."""

    name: str
    v_reference_km_s: float
    v_rig_km_s: float
    ratio: float          # v_RIG / v_reference
    log_ratio: float      # log₂(v_RIG / v_reference)
    within_order: bool    # |log₁₀ ratio| < 1


class PeculiarVelocityAnalyzer:
    """Compare v_RIG to cosmological peculiar velocity scales.

    Tests Prediction 2 from the v_RIG framework:
    v_RIG should appear as a characteristic scale in peculiar-velocity surveys.

    Primary survey: 2MRS (Erdoğdu et al. 2006, MNRAS 368:1515).
    Extended: CosmicFlows-4 (Tully et al. 2023).
    """

    def __init__(self, v_rig: float = V_RIG_KM_S) -> None:
        self._v_rig = v_rig

    def compare_all(self) -> list[PeculiarVelocityComparison]:
        results: list[PeculiarVelocityComparison] = []
        for name, v_ref in REFERENCE_SCALES.items():
            if name == "v_RIG":
                continue
            ratio = self._v_rig / v_ref
            results.append(
                PeculiarVelocityComparison(
                    name=name,
                    v_reference_km_s=v_ref,
                    v_rig_km_s=self._v_rig,
                    ratio=ratio,
                    log_ratio=float(np.log2(ratio)),
                    within_order=abs(np.log10(ratio)) < 1.0,
                )
            )
        return results

    def compare_to(self, name: str) -> PeculiarVelocityComparison:
        v_ref = REFERENCE_SCALES[name]
        ratio = self._v_rig / v_ref
        return PeculiarVelocityComparison(
            name=name,
            v_reference_km_s=v_ref,
            v_rig_km_s=self._v_rig,
            ratio=ratio,
            log_ratio=float(np.log2(ratio)),
            within_order=abs(np.log10(ratio)) < 1.0,
        )

    # ------------------------------------------------------------------
    # Synthetic 2MRS-like data for testability

    @staticmethod
    def synthetic_2mrs_velocities(
        n: int = 1000,
        rng_seed: int = 0,
    ) -> NDArray[np.float64]:
        """Synthetic galaxy peculiar velocity distribution (2MRS-like).

        Models a mix of Gaussian bulk flow + log-normal scatter.
        Injected feature near v_RIG for testing the detection method.
        """
        rng = np.random.default_rng(rng_seed)
        bulk = rng.normal(loc=250.0, scale=150.0, size=n)
        scatter = rng.lognormal(mean=5.5, sigma=0.8, size=n)
        # Inject a weak excess near v_RIG (Prediction 2)
        n_excess = max(1, n // 40)
        excess = rng.normal(loc=V_RIG_KM_S, scale=50.0, size=n_excess)
        all_v = np.concatenate([np.abs(bulk), scatter, excess])
        return all_v

    def test_vrig_excess(
        self,
        velocities: NDArray[np.float64],
        window_km_s: float = 100.0,
        n_bootstrap: int = 1000,
        rng_seed: int = 7,
    ) -> dict[str, float]:
        """Test whether velocities show excess near v_RIG vs. neighbouring bins.

        Returns a dict with keys: n_in_window, n_control, excess_ratio, p_value_approx.
        """
        rng = np.random.default_rng(rng_seed)
        v = np.asarray(velocities, dtype=float)

        lo, hi = self._v_rig - window_km_s, self._v_rig + window_km_s
        n_window = int(np.sum((v >= lo) & (v <= hi)))

        # Control: same-width bin offset by +2 windows (avoids RIG region)
        c_lo, c_hi = hi + window_km_s, hi + 3 * window_km_s
        n_control = max(1, int(np.sum((v >= c_lo) & (v <= c_hi))))

        excess_ratio = n_window / n_control

        # Bootstrap p-value: probability excess_ratio ≥ observed under null
        null_ratios: list[float] = []
        for _ in range(n_bootstrap):
            shuffled = rng.permutation(v)
            n_w = int(np.sum((shuffled >= lo) & (shuffled <= hi)))
            n_c = max(1, int(np.sum((shuffled >= c_lo) & (shuffled <= c_hi))))
            null_ratios.append(n_w / n_c)
        p_value = float(np.mean(np.array(null_ratios) >= excess_ratio))

        return {
            "n_in_window": float(n_window),
            "n_control": float(n_control),
            "excess_ratio": excess_ratio,
            "p_value_approx": p_value,
        }
