"""Fundamental constants for the v_RIG framework.

All values from CODATA 2018 / IAU 2012 / Planck 2018.
"""

import math

# Speed of light (exact by SI definition), km/s
C_KM_S: float = 299_792.458

# Fine-structure constant (CODATA 2018)
ALPHA: float = 1.0 / 137.035_999_084
ALPHA_UNCERTAINTY: float = 1.5e-10  # relative uncertainty

# Golden ratio (exact)
PHI: float = (1.0 + math.sqrt(5.0)) / 2.0  # 1.6180339887...

# v_RIG = c / (α⁻¹ · Φ) = c · α / Φ  [km/s]
V_RIG_KM_S: float = C_KM_S * ALPHA / PHI  # ≈ 1352.12 km/s

# CMB dipole velocity, km/s (Planck 2018)
V_CMB_DIPOLE_KM_S: float = 369.82
V_CMB_DIPOLE_UNCERTAINTY: float = 0.11

# Derived ratios
V_RIG_RATIO_CMB: float = V_RIG_KM_S / V_CMB_DIPOLE_KM_S  # ≈ 3.66
ALPHA_PHI_PRODUCT: float = ALPHA / PHI  # ≈ 0.00451 = v_RIG / c

# UTAC frame principle
SIGMA_PHI: float = 1.0 / 16.0

# Package metadata
ZENODO_DOI: str = "10.5281/zenodo.17472834"
PACKAGE_ID: int = 31
