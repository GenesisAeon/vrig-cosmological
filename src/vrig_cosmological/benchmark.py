"""Benchmark v_RIG framework against published targets.

All targets from Package 31 specification (GenesisAeon roadmap).
"""

from __future__ import annotations

from dataclasses import dataclass

from vrig_cosmological.constants import ALPHA, PHI
from vrig_cosmological.falsification import FalsificationTests
from vrig_cosmological.vrig_calculator import VRIGCalculator

VRIG_TARGETS: dict[str, tuple[float, float | None]] = {
    "v_rig_km_s":              (1352.07,  0.05),
    "v_rig_ratio_cmb_dipole":  (3.66,     0.02),
    "era5_spike_year":         (1998.0,   2.0),
    "spike_precedes_transition": (1.0,    None),   # bool encoded as 1=True
    "alpha_phi_product":       (0.004513, 0.00005),
}


@dataclass(frozen=True)
class BenchmarkResult:
    name: str
    target: float
    tolerance: float | None
    measured: float | None
    passed: bool
    notes: str


class VRIGBenchmark:
    """Run all benchmark checks and report pass/fail per target."""

    def run(self) -> list[BenchmarkResult]:
        results: list[BenchmarkResult] = []
        calc = VRIGCalculator()
        vrig = calc.compute()

        # ------ numerical targets ------
        results.append(self._check(
            "v_rig_km_s", VRIG_TARGETS["v_rig_km_s"],
            vrig.v_rig_km_s,
            f"Computed {vrig.v_rig_km_s:.4f} km/s",
        ))

        results.append(self._check(
            "v_rig_ratio_cmb_dipole", VRIG_TARGETS["v_rig_ratio_cmb_dipole"],
            vrig.ratio_cmb_dipole,
            f"v_RIG / v_CMB = {vrig.ratio_cmb_dipole:.4f}",
        ))

        results.append(self._check(
            "alpha_phi_product", VRIG_TARGETS["alpha_phi_product"],
            ALPHA / PHI,
            f"α/Φ = {ALPHA / PHI:.6f}",
        ))

        # ------ falsification tests ------
        ft = FalsificationTests()
        t1 = ft.test_1_regime_shift_spike()
        spike_year = t1.value if t1.value is not None else float("nan")
        results.append(self._check(
            "era5_spike_year", VRIG_TARGETS["era5_spike_year"],
            spike_year,
            t1.notes,
        ))

        t3 = ft.test_3_spike_precedes_transition()
        precedes_val = 1.0 if t3.passed else 0.0
        results.append(BenchmarkResult(
            name="spike_precedes_transition",
            target=1.0,
            tolerance=None,
            measured=precedes_val,
            passed=t3.passed,
            notes=t3.notes,
        ))

        return results

    # ------------------------------------------------------------------

    @staticmethod
    def _check(
        name: str,
        target_tol: tuple[float, float | None],
        measured: float,
        notes: str,
    ) -> BenchmarkResult:
        target, tol = target_tol
        if tol is None:
            passed = bool(measured == target)
        else:
            passed = abs(measured - target) <= tol
        return BenchmarkResult(
            name=name,
            target=target,
            tolerance=tol,
            measured=measured,
            passed=passed,
            notes=notes,
        )

    def summary(self) -> str:
        results = self.run()
        lines = ["v_RIG Benchmark", "=" * 40]
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            tol_str = f"±{r.tolerance}" if r.tolerance is not None else "bool"
            measured_str = f"{r.measured:.4f}" if r.measured is not None else "N/A"
            lines.append(
                f"[{status}] {r.name:35s}  "
                f"target={r.target} {tol_str}  measured={measured_str}"
            )
            if not r.passed:
                lines.append(f"         {r.notes}")
        n_pass = sum(1 for r in results if r.passed)
        lines.append(f"\n{n_pass}/{len(results)} benchmarks passed.")
        return "\n".join(lines)
