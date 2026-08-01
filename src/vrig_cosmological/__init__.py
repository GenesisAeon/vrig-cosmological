"""vrig-cosmological — GenesisAeon Package 31.

v_RIG = c / (α⁻¹ · Φ) ≈ 1352.12 km/s

A falsifiable cosmological velocity scale derived from the fine-structure
constant α and the golden ratio Φ. Implements the Fisher-Rao information-
geometric interpretation, ERA5 spike detection, and cosmological survey
comparisons.
"""

from vrig_cosmological.constants import ALPHA, C_KM_S, PHI, V_RIG_KM_S
from vrig_cosmological.system import VRIGCosmological
from vrig_cosmological.vrig_calculator import VRIGCalculator, compute_vrig

__version__ = "0.1.0"
__author__ = "GenesisAeon / Johann Römer"
__zenodo__ = "10.5281/zenodo.20934822"
__package_id__ = 31

__all__ = [
    "VRIGCosmological",
    "VRIGCalculator",
    "compute_vrig",
    "V_RIG_KM_S",
    "ALPHA",
    "PHI",
    "C_KM_S",
]
