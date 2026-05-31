"""VRIGCosmological — Diamond interface (Package 31).

Implements the standard GenesisAeon Diamond interface:
    run_cycle(), get_crep_state(), get_utac_state(),
    get_phase_events(), to_zenodo_record(), v_rig_value(), spike_times()
"""

from __future__ import annotations

import math

from vrig_cosmological.benchmark import VRIGBenchmark
from vrig_cosmological.constants import (
    PACKAGE_ID,
    SIGMA_PHI,
    V_RIG_KM_S,
    ZENODO_DOI,
)
from vrig_cosmological.crep_coupling import CREPCoupling
from vrig_cosmological.falsification import FalsificationTests
from vrig_cosmological.information_geometry import UTACState
from vrig_cosmological.spike_detector import SpikeEvent, VRIGSpikeDetector
from vrig_cosmological.vrig_calculator import VRIGCalculator


class VRIGCosmological:
    """GenesisAeon Package 31 — v_RIG Kosmologische Geschwindigkeit.

    Encapsulates the full v_RIG = c/(α⁻¹·Φ) framework as a Diamond-interface
    compatible system object.

    Usage
    -----
    >>> sys = VRIGCosmological()
    >>> result = sys.run_cycle(duration_years=83.0)
    >>> sys.v_rig_value()
    1352.118...
    >>> sys.spike_times()
    [1998.0, ...]
    """

    def __init__(
        self,
        spike_threshold: float = 1.0,
        start_year: float = 1940.0,
    ) -> None:
        self._threshold = spike_threshold
        self._start_year = start_year
        self._calc = VRIGCalculator()
        self._coupling = CREPCoupling(v_rig_km_s=V_RIG_KM_S)
        self._detector = VRIGSpikeDetector(threshold_normalised=spike_threshold)
        self._last_states: list[UTACState] = []
        self._last_spikes: list[SpikeEvent] = []

    # ------------------------------------------------------------------
    # Diamond interface
    # ------------------------------------------------------------------

    def run_cycle(self, duration_years: float = 83.0) -> dict[str, object]:
        """Run the full v_RIG analysis cycle.

        Generates synthetic ERA5-like UTAC parameter trajectory,
        detects v_RIG spikes, and runs all falsification tests.

        Returns
        -------
        dict with keys: v_rig, spikes, falsification, benchmark.
        """
        n = max(2, int(duration_years))
        self._last_states = VRIGSpikeDetector.synthetic_era5_states(
            n_years=n,
            start_year=self._start_year,
        )
        self._last_spikes = self._detector.detect(self._last_states)

        vrig_result = self._calc.compute()
        ft = FalsificationTests(spike_threshold=self._threshold)
        falsification_results = ft.run_all()

        bm = VRIGBenchmark()
        benchmark_results = bm.run()

        return {
            "v_rig_km_s": vrig_result.v_rig_km_s,
            "v_rig_uncertainty_km_s": vrig_result.uncertainty_km_s,
            "n_spikes": len(self._last_spikes),
            "spike_times": self.spike_times(),
            "falsification_passed": sum(1 for r in falsification_results if r.passed),
            "falsification_total": len(falsification_results),
            "benchmark_passed": sum(1 for r in benchmark_results if r.passed),
            "benchmark_total": len(benchmark_results),
            "duration_years": duration_years,
        }

    def get_crep_state(self) -> dict[str, object]:
        """Return current CREP state derived from v_RIG framework."""
        return {
            "Gamma": 0.251,  # v_RIG framework maps to AMOC/Neural scale
            "C": V_RIG_KM_S / 1000.0,  # normalised complexity
            "R": 1.0 / 137.036,        # fine-structure coupling
            "E": math.log(V_RIG_KM_S), # log-entropy scale
            "P": SIGMA_PHI,            # Frame Principle potential
            "domain": "information-geometry",
            "scale": "cosmological",
        }

    def get_utac_state(self) -> dict[str, object]:
        """Return UTAC parameter state at the end of last run_cycle."""
        if not self._last_states:
            return {"r": 0.3, "K": 1.0, "sigma": 2.2, "t": self._start_year}
        last = self._last_states[-1]
        return {"r": last.r, "K": last.K, "sigma": last.sigma, "t": last.t}

    def get_phase_events(self) -> list[dict[str, object]]:
        """Return list of phase events (v_RIG spike timestamps)."""
        return [
            {
                "time": s.time,
                "type": "v_RIG_spike",
                "speed": s.speed,
                "excess": s.excess,
            }
            for s in self._last_spikes
        ]

    def to_zenodo_record(self) -> dict[str, object]:
        """Return metadata dict suitable for Zenodo deposition."""
        vrig = self._calc.compute()
        return {
            "title": "v_RIG Kosmologische Geschwindigkeit — GenesisAeon Package 31",
            "description": (
                f"v_RIG = c/(α⁻¹·Φ) = {vrig.v_rig_km_s:.4f} ± "
                f"{vrig.uncertainty_km_s:.4f} km/s. "
                "Falsifizierbare kosmologische Vorhersage aus dem "
                "GenesisAeon UTAC/CREP-Framework."
            ),
            "creators": [{"name": "Römer, Johann", "affiliation": "MOR Research Collective"}],
            "keywords": ["v_RIG", "UTAC", "CREP", "information geometry",
                         "Fisher-Rao", "peculiar velocity", "cosmology"],
            "doi": ZENODO_DOI,
            "package_id": PACKAGE_ID,
            "v_rig_km_s": vrig.v_rig_km_s,
            "uncertainty_km_s": vrig.uncertainty_km_s,
        }

    # ------------------------------------------------------------------
    # Package-specific methods
    # ------------------------------------------------------------------

    def v_rig_value(self) -> float:
        """Return v_RIG = c/(α⁻¹·Φ) in km/s."""
        return self._calc.compute().v_rig_km_s

    def spike_times(self) -> list[float]:
        """Return timestamps where Fisher-Rao speed exceeded v_RIG threshold."""
        return [s.time for s in self._last_spikes]

    def __repr__(self) -> str:
        return (
            f"VRIGCosmological("
            f"v_RIG={self.v_rig_value():.4f} km/s, "
            f"package={PACKAGE_ID})"
        )
