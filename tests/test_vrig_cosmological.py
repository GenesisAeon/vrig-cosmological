"""Tests for vrig-cosmological Package 31."""

import math
import pytest

from vrig_cosmological import V_RIG_KM_S, VRIGCalculator, compute_vrig
from vrig_cosmological.constants import ALPHA, ALPHA_UNCERTAINTY, C_KM_S, PHI
from vrig_cosmological.crep_coupling import CREPCoupling, CREPState
from vrig_cosmological.falsification import FalsificationTests
from vrig_cosmological.benchmark import VRIGBenchmark
from vrig_cosmological.information_geometry import FisherRaoMetric, UTACState, FisherRaoVelocityTimeSeries
from vrig_cosmological.peculiar_velocity import PeculiarVelocityAnalyzer
from vrig_cosmological.spike_detector import VRIGSpikeDetector
from vrig_cosmological.system import VRIGCosmological


# ─────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────

class TestConstants:
    def test_vrig_value(self):
        assert abs(V_RIG_KM_S - 1352.07) < 0.05

    def test_alpha_inverse(self):
        assert abs(1.0 / ALPHA - 137.036) < 0.001

    def test_phi_exact(self):
        assert abs(PHI - (1 + math.sqrt(5)) / 2) < 1e-12

    def test_c_exact(self):
        assert C_KM_S == pytest.approx(299792.458)

    def test_alpha_phi_product(self):
        assert abs(ALPHA / PHI - 0.004513) < 0.00005


# ─────────────────────────────────────────────────────────────────
# VRIGCalculator
# ─────────────────────────────────────────────────────────────────

class TestVRIGCalculator:
    def test_compute_value(self):
        r = VRIGCalculator().compute()
        assert r.v_rig_km_s == pytest.approx(1352.07, abs=0.05)

    def test_uncertainty_positive(self):
        r = VRIGCalculator().compute()
        assert r.uncertainty_km_s > 0

    def test_ratio_cmb(self):
        r = VRIGCalculator().compute()
        assert r.ratio_cmb_dipole == pytest.approx(3.66, abs=0.02)

    def test_ratio_c(self):
        r = VRIGCalculator().compute()
        assert r.ratio_c == pytest.approx(ALPHA / PHI, rel=1e-9)

    def test_natural_form(self):
        calc = VRIGCalculator()
        assert calc.v_rig_natural() == pytest.approx(ALPHA / PHI, rel=1e-9)

    def test_compute_vrig_convenience(self):
        r = compute_vrig()
        assert abs(r.v_rig_km_s - V_RIG_KM_S) < 0.001

    def test_summary_contains_vrig(self):
        s = VRIGCalculator().summary()
        assert "v_RIG" in s
        assert "1352" in s


# ─────────────────────────────────────────────────────────────────
# Information Geometry
# ─────────────────────────────────────────────────────────────────

class TestFisherRaoMetric:
    def _make_state(self, t=0.0):
        return UTACState(t=t, r=0.3, K=1.0, sigma=2.2)

    def test_metric_diagonal_positive(self):
        m = FisherRaoMetric()
        g = m.metric_diagonal(self._make_state())
        assert all(v > 0 for v in g)

    def test_geodesic_speed_zero_when_static(self):
        m = FisherRaoMetric()
        speed = m.geodesic_speed(self._make_state(), (0.0, 0.0, 0.0))
        assert speed == pytest.approx(0.0)

    def test_geodesic_speed_positive(self):
        m = FisherRaoMetric()
        speed = m.geodesic_speed(self._make_state(), (1.0, 0.0, 0.0))
        assert speed > 0

    def test_velocity_timeseries_length(self):
        states = [UTACState(t=float(i), r=0.3, K=1.0, sigma=2.2) for i in range(5)]
        ts = FisherRaoVelocityTimeSeries()
        v = ts.compute(states)
        assert len(v) == 4

    def test_velocity_timeseries_empty_on_single_state(self):
        ts = FisherRaoVelocityTimeSeries()
        v = ts.compute([UTACState(t=0, r=0.3, K=1.0, sigma=2.2)])
        assert len(v) == 0


# ─────────────────────────────────────────────────────────────────
# Spike Detector
# ─────────────────────────────────────────────────────────────────

class TestVRIGSpikeDetector:
    def test_spike_detected_at_regime_shift(self):
        detector = VRIGSpikeDetector(threshold_normalised=1.0)
        states = VRIGSpikeDetector.synthetic_era5_states(regime_shift_year=1998.0)
        spikes = detector.detect(states)
        assert len(spikes) >= 1

    def test_spike_time_near_1998(self):
        detector = VRIGSpikeDetector(threshold_normalised=1.0)
        states = VRIGSpikeDetector.synthetic_era5_states(regime_shift_year=1998.0)
        spikes = detector.detect(states)
        assert any(abs(s.time - 1998.0) <= 2.0 for s in spikes)

    def test_spike_has_positive_excess(self):
        detector = VRIGSpikeDetector(threshold_normalised=1.0)
        states = VRIGSpikeDetector.synthetic_era5_states()
        spikes = detector.detect(states)
        for s in spikes:
            assert s.excess >= 0.0

    def test_no_spike_above_very_high_threshold(self):
        detector = VRIGSpikeDetector(threshold_normalised=1e9)
        states = VRIGSpikeDetector.synthetic_era5_states()
        spikes = detector.detect(states)
        assert spikes == []


# ─────────────────────────────────────────────────────────────────
# CREP Coupling
# ─────────────────────────────────────────────────────────────────

class TestCREPCoupling:
    def test_crep_state_gamma(self):
        s = CREPState(C=0.5, R=0.5, E=0.5, P=0.5)
        assert s.gamma == pytest.approx(0.5)

    def test_crep_state_negative_raises(self):
        with pytest.raises(ValueError):
            CREPState(C=-1.0, R=1.0, E=1.0, P=1.0)

    def test_gamma_velocity_zero(self):
        c = CREPCoupling()
        assert c.gamma_velocity(0.5, 0.5, 1.0) == pytest.approx(0.0)

    def test_gamma_velocity_positive(self):
        c = CREPCoupling()
        assert c.gamma_velocity(0.2, 0.5, 1.0) == pytest.approx(0.3)

    def test_spectrum_spacing_positive(self):
        c = CREPCoupling()
        ratios = c.crep_spectrum_spacing()
        assert all(v > 0 for v in ratios.values())


# ─────────────────────────────────────────────────────────────────
# Peculiar Velocity
# ─────────────────────────────────────────────────────────────────

class TestPeculiarVelocity:
    def test_compare_all_length(self):
        a = PeculiarVelocityAnalyzer()
        results = a.compare_all()
        assert len(results) >= 5

    def test_cmb_ratio(self):
        a = PeculiarVelocityAnalyzer()
        r = a.compare_to("CMB_dipole")
        assert r.ratio == pytest.approx(V_RIG_KM_S / 369.82, rel=1e-4)

    def test_synthetic_velocities_positive(self):
        a = PeculiarVelocityAnalyzer()
        v = a.synthetic_2mrs_velocities(n=200)
        assert (v > 0).all()

    def test_excess_test_returns_dict(self):
        a = PeculiarVelocityAnalyzer()
        v = a.synthetic_2mrs_velocities(n=500)
        stats = a.test_vrig_excess(v)
        assert "excess_ratio" in stats
        assert "p_value_approx" in stats


# ─────────────────────────────────────────────────────────────────
# Falsification
# ─────────────────────────────────────────────────────────────────

class TestFalsification:
    def test_all_three_tests_run(self):
        ft = FalsificationTests()
        results = ft.run_all()
        assert len(results) == 3

    def test_regime_shift_passes(self):
        ft = FalsificationTests()
        r = ft.test_1_regime_shift_spike()
        assert r.passed

    def test_spike_precedes_transition(self):
        ft = FalsificationTests()
        r = ft.test_3_spike_precedes_transition()
        assert r.passed

    def test_summary_contains_pass(self):
        ft = FalsificationTests()
        s = ft.summary()
        assert "PASS" in s


# ─────────────────────────────────────────────────────────────────
# Benchmark
# ─────────────────────────────────────────────────────────────────

class TestBenchmark:
    def test_all_benchmarks_pass(self):
        bm = VRIGBenchmark()
        results = bm.run()
        failed = [r for r in results if not r.passed]
        assert failed == [], f"Failed benchmarks: {[r.name for r in failed]}"

    def test_summary_string(self):
        bm = VRIGBenchmark()
        s = bm.summary()
        assert "PASS" in s


# ─────────────────────────────────────────────────────────────────
# Diamond Interface (VRIGCosmological)
# ─────────────────────────────────────────────────────────────────

class TestVRIGCosmological:
    def test_v_rig_value(self):
        sys = VRIGCosmological()
        assert abs(sys.v_rig_value() - 1352.07) < 0.05

    def test_run_cycle_returns_dict(self):
        sys = VRIGCosmological()
        result = sys.run_cycle(duration_years=83.0)
        assert isinstance(result, dict)
        assert "v_rig_km_s" in result

    def test_run_cycle_spikes(self):
        sys = VRIGCosmological()
        result = sys.run_cycle(duration_years=83.0)
        assert result["n_spikes"] >= 1

    def test_spike_times_list(self):
        sys = VRIGCosmological()
        sys.run_cycle()
        assert isinstance(sys.spike_times(), list)

    def test_get_crep_state(self):
        sys = VRIGCosmological()
        state = sys.get_crep_state()
        assert "Gamma" in state
        assert "domain" in state

    def test_get_utac_state(self):
        sys = VRIGCosmological()
        state = sys.get_utac_state()
        assert "r" in state
        assert "K" in state

    def test_get_phase_events_after_run(self):
        sys = VRIGCosmological()
        sys.run_cycle()
        events = sys.get_phase_events()
        assert isinstance(events, list)

    def test_to_zenodo_record(self):
        sys = VRIGCosmological()
        rec = sys.to_zenodo_record()
        assert "v_rig_km_s" in rec
        assert "doi" in rec
        assert rec["package_id"] == 31

    def test_repr(self):
        sys = VRIGCosmological()
        r = repr(sys)
        assert "VRIGCosmological" in r
        assert "1352" in r
