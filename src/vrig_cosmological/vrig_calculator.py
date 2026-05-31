"""Compute v_RIG = c / (α⁻¹ · Φ) with full uncertainty propagation."""

from __future__ import annotations

from dataclasses import dataclass

from vrig_cosmological.constants import (
    ALPHA,
    ALPHA_UNCERTAINTY,
    C_KM_S,
    PHI,
    V_CMB_DIPOLE_KM_S,
    V_RIG_KM_S,
)


@dataclass(frozen=True)
class VRIGResult:
    """Full result of a v_RIG computation."""

    v_rig_km_s: float
    uncertainty_km_s: float
    ratio_cmb_dipole: float
    ratio_c: float  # = α/Φ, dimensionless
    alpha_used: float
    phi_used: float
    c_km_s: float


class VRIGCalculator:
    """Compute v_RIG = c / (α⁻¹ · Φ) = c · α / Φ.

    Components:
        c   = 299 792.458 km/s (exact)
        α   = 1/137.035 999 084  ±1.5×10⁻¹⁰  (CODATA 2018)
        Φ   = (1+√5)/2 = 1.618 033 988 7…      (exact)

    v_RIG ≈ 1352.12 ± 0.01 km/s
    """

    def __init__(
        self,
        alpha: float = ALPHA,
        phi: float = PHI,
        c_km_s: float = C_KM_S,
        alpha_rel_uncertainty: float = ALPHA_UNCERTAINTY,
    ) -> None:
        self._alpha = alpha
        self._phi = phi
        self._c = c_km_s
        self._alpha_unc = alpha_rel_uncertainty

    # ------------------------------------------------------------------
    def compute(self) -> VRIGResult:
        """Return the full v_RIG result with uncertainty."""
        v = self._c * self._alpha / self._phi
        # Uncertainty: only α has a meaningful uncertainty here.
        # δv/v = δα/α  (c exact, Φ exact)
        dv = v * self._alpha_unc
        return VRIGResult(
            v_rig_km_s=v,
            uncertainty_km_s=dv,
            ratio_cmb_dipole=v / V_CMB_DIPOLE_KM_S,
            ratio_c=self._alpha / self._phi,
            alpha_used=self._alpha,
            phi_used=self._phi,
            c_km_s=self._c,
        )

    # ------------------------------------------------------------------
    # Convenience forms
    # ------------------------------------------------------------------

    def v_rig_natural(self) -> float:
        """v_RIG in natural units: α / Φ  (dimensionless fraction of c)."""
        return self._alpha / self._phi

    def alpha_phi_denominator(self) -> float:
        """α⁻¹ · Φ  — the denominator in the original formula."""
        return self._phi / self._alpha

    def summary(self) -> str:
        r = self.compute()
        lines = [
            "v_RIG = c / (α⁻¹ · Φ)",
            f"  c        = {r.c_km_s:.3f} km/s  (exact)",
            f"  α⁻¹      = {1/r.alpha_used:.6f}",
            f"  Φ        = {r.phi_used:.10f}",
            f"  α⁻¹ · Φ  = {self.alpha_phi_denominator():.6f}",
            f"  v_RIG    = {r.v_rig_km_s:.4f} ± {r.uncertainty_km_s:.4f} km/s",
            f"  v/v_CMB  = {r.ratio_cmb_dipole:.4f}",
            f"  v/c      = {r.ratio_c:.6f}  (= α/Φ)",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"VRIGCalculator(v_RIG={V_RIG_KM_S:.4f} km/s)"


def compute_vrig() -> VRIGResult:
    """Module-level convenience function."""
    return VRIGCalculator().compute()


def analytical_uncertainty(delta_alpha_abs: float | None = None) -> float:
    """Return the absolute uncertainty in km/s given δα.

    If delta_alpha_abs is None, uses the CODATA 2018 relative uncertainty.
    """
    if delta_alpha_abs is None:
        delta_alpha_abs = ALPHA * ALPHA_UNCERTAINTY
    return C_KM_S * delta_alpha_abs / PHI


def v_rig_from_params(alpha: float, phi: float = PHI, c: float = C_KM_S) -> float:
    """Compute v_RIG for arbitrary α and Φ values (sensitivity analysis)."""
    return c * alpha / phi
