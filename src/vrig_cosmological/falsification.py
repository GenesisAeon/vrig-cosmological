"""Explicit falsification tests for the v_RIG framework.

Three testable predictions from the GenesisAeon Package 31 specification:

  1. Regime-shift detection: v_RIG spike precedes UTAC phase event.
  2. Cosmological scale: v_RIG appears as characteristic scale in
     peculiar-velocity surveys.
  3. Information-geometric precession: spike leads phase transition by
     τ ≈ T₁ / v_RIG_normalised.
"""

from __future__ import annotations

from dataclasses import dataclass

from vrig_cosmological.constants import V_RIG_KM_S
from vrig_cosmological.peculiar_velocity import PeculiarVelocityAnalyzer
from vrig_cosmological.spike_detector import VRIGSpikeDetector


@dataclass(frozen=True)
class FalsificationResult:
    """Outcome of a single falsification test."""

    name: str
    passed: bool
    value: float | None
    expected: float | None
    tolerance: float | None
    notes: str


class FalsificationTests:
    """Run all three v_RIG falsification tests and return results.

    Tests are marked PASSED when predictions are *consistent* with the
    synthetic/reference data.  A test that fails here does NOT immediately
    falsify the framework — it signals that real observational data must
    be acquired to adjudicate.
    """

    def __init__(
        self,
        spike_threshold: float = 1.0,
        survey_window_km_s: float = 100.0,
        n_synthetic_galaxies: int = 1000,
    ) -> None:
        self._threshold = spike_threshold
        self._window = survey_window_km_s
        self._n_gal = n_synthetic_galaxies

    # ------------------------------------------------------------------

    def test_1_regime_shift_spike(self) -> FalsificationResult:
        """Prediction 1: v_RIG spike detected at ~1998 in ERA5-like data."""
        detector = VRIGSpikeDetector(threshold_normalised=self._threshold)
        states = VRIGSpikeDetector.synthetic_era5_states(
            regime_shift_year=1998.0
        )
        spikes = detector.detect(states)

        if not spikes:
            return FalsificationResult(
                name="Regime-shift spike detection",
                passed=False,
                value=None,
                expected=1998.0,
                tolerance=2.0,
                notes="No spikes detected in synthetic ERA5 trajectory.",
            )

        spike_t = spikes[0].time
        passed = abs(spike_t - 1998.0) <= 2.0
        return FalsificationResult(
            name="Regime-shift spike detection",
            passed=passed,
            value=spike_t,
            expected=1998.0,
            tolerance=2.0,
            notes=f"First spike at {spike_t:.1f} (expected 1998 ± 2 yr).",
        )

    # ------------------------------------------------------------------

    def test_2_peculiar_velocity_excess(self) -> FalsificationResult:
        """Prediction 2: Peculiar-velocity excess near v_RIG ≈ 1352 km/s."""
        analyzer = PeculiarVelocityAnalyzer(v_rig=V_RIG_KM_S)
        velocities = analyzer.synthetic_2mrs_velocities(n=self._n_gal)
        stats = analyzer.test_vrig_excess(velocities, window_km_s=self._window)

        excess_ratio = stats["excess_ratio"]
        passed = excess_ratio > 1.0  # more galaxies near v_RIG than control

        return FalsificationResult(
            name="Peculiar-velocity excess at v_RIG",
            passed=passed,
            value=excess_ratio,
            expected=1.0,
            tolerance=None,
            notes=(
                f"Excess ratio = {excess_ratio:.3f} "
                f"(p ≈ {stats['p_value_approx']:.3f}). "
                "Requires real 2MRS/CF4 data to confirm."
            ),
        )

    # ------------------------------------------------------------------

    def test_3_spike_precedes_transition(self) -> FalsificationResult:
        """Prediction 3: v_RIG spike precedes phase-transition event."""
        # The synthetic ERA5 state sequence has regime shift injected at 1998.
        # We check that the first spike occurs BEFORE the known transition.
        detector = VRIGSpikeDetector(threshold_normalised=self._threshold)
        states = VRIGSpikeDetector.synthetic_era5_states(
            regime_shift_year=1998.0
        )
        spikes = detector.detect(states)

        if not spikes:
            return FalsificationResult(
                name="Spike precedes phase transition",
                passed=False,
                value=None,
                expected=1998.0,
                tolerance=0.0,
                notes="No spikes detected; cannot test temporal ordering.",
            )

        # The phase-transition event = first year after the spike where
        # H* is crossed (approximated here as 1998 itself in synthetic data)
        spike_t = spikes[0].time
        transition_t = 1998.0
        passed = spike_t <= transition_t

        return FalsificationResult(
            name="Spike precedes phase transition",
            passed=passed,
            value=spike_t,
            expected=transition_t,
            tolerance=0.0,
            notes=(
                f"Spike at {spike_t:.1f}, transition at {transition_t:.1f}. "
                f"Lead = {transition_t - spike_t:.1f} yr."
            ),
        )

    # ------------------------------------------------------------------

    def run_all(self) -> list[FalsificationResult]:
        """Run all three tests and return results."""
        return [
            self.test_1_regime_shift_spike(),
            self.test_2_peculiar_velocity_excess(),
            self.test_3_spike_precedes_transition(),
        ]

    def summary(self, results: list[FalsificationResult] | None = None) -> str:
        if results is None:
            results = self.run_all()
        lines = ["v_RIG Falsification Tests", "=" * 40]
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"[{status}] {r.name}")
            lines.append(f"       {r.notes}")
        n_pass = sum(1 for r in results if r.passed)
        lines.append(f"\n{n_pass}/{len(results)} tests passed.")
        return "\n".join(lines)
