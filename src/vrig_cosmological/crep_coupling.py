"""v_RIG as a CREP-component velocity in the UTAC parameter manifold.

The CREP tensor Γ(C, R, E, P) = (C·R·E·P)^(1/4) gives a criticality
measure. When Γ is used to label a position in the CREP spectrum, the
Fisher-Rao speed of moving through the spectrum is v_RIG.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from vrig_cosmological.constants import ALPHA, PHI, V_RIG_KM_S


@dataclass(frozen=True)
class CREPState:
    """A point in the CREP parameter space."""

    C: float  # Complexity
    R: float  # Resonance
    E: float  # Entropy
    P: float  # Potential

    @property
    def gamma(self) -> float:
        """Γ = (C·R·E·P)^(1/4)"""
        return (self.C * self.R * self.E * self.P) ** 0.25

    def __post_init__(self) -> None:
        for name, val in [("C", self.C), ("R", self.R), ("E", self.E), ("P", self.P)]:
            if val < 0:
                raise ValueError(f"CREP component {name} must be non-negative, got {val}")


class CREPCoupling:
    """Compute v_RIG as the characteristic velocity in CREP parameter space.

    Interpretation:
        v_RIG = c · α / Φ
    is the geodesic speed at which a system traverses the CREP spectrum
    at the information-geometric scale set by α and Φ.

    The normalised CREP velocity is:
        v_CREP(t) = dΓ/dt / (α/Φ)

    When v_CREP > 1 (in these units), the system is moving through the
    CREP spectrum faster than v_RIG — a phase transition is imminent.
    """

    def __init__(self, v_rig_km_s: float = V_RIG_KM_S) -> None:
        self._v_rig = v_rig_km_s

    def gamma_velocity(self, gamma_prev: float, gamma_next: float, dt: float) -> float:
        """Return |dΓ/dt| between two consecutive CREP states."""
        if abs(dt) < 1e-15:
            return 0.0
        return abs(gamma_next - gamma_prev) / dt

    def normalised_velocity(self, gamma_prev: float, gamma_next: float, dt: float) -> float:
        """Return |dΓ/dt| normalised by α/Φ (dimensionless v_RIG units)."""
        raw = self.gamma_velocity(gamma_prev, gamma_next, dt)
        return raw / (ALPHA / PHI)

    def is_phase_transition_imminent(
        self,
        gamma_prev: float,
        gamma_next: float,
        dt: float,
        factor: float = 1.0,
    ) -> bool:
        """True when the normalised CREP velocity exceeds factor × 1."""
        return self.normalised_velocity(gamma_prev, gamma_next, dt) > factor

    # ------------------------------------------------------------------
    # CREP spectrum positions for GenesisAeon reference domains
    CREP_REFERENCE: dict[str, float] = {
        "Cygnus_X1_jet":   0.046,
        "Solar_flares":    0.014,
        "Qubit_decoherence": 0.050,
        "Apoptosis_ATP":   0.090,
        "Amazon":          0.116,
        "Phaethon":        0.165,
        "Seismic_GR":      0.200,
        "AMOC":            0.251,
        "Neural_criticality": 0.251,
        "Theta_cognitive": 0.251,
        "Sandpile_BTW":    0.296,
        "Sandpile_Manna":  0.376,
        "PoR_consensus":   0.367,
        "Diffusive_routing": 0.443,
        "Arctic_ice":      0.920,
    }

    def crep_spectrum_spacing(self) -> dict[str, float]:
        """Return ratio of consecutive Γ values in the ordered CREP spectrum."""
        sorted_items = sorted(self.CREP_REFERENCE.items(), key=lambda x: x[1])
        ratios: dict[str, float] = {}
        for i in range(1, len(sorted_items)):
            name_prev, g_prev = sorted_items[i - 1]
            name_curr, g_curr = sorted_items[i]
            if g_prev > 0:
                ratios[f"{name_prev}→{name_curr}"] = g_curr / g_prev
        return ratios

    @property
    def v_rig(self) -> float:
        return self._v_rig
