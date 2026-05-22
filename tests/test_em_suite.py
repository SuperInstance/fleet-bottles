"""
Unit tests for benchmarks.em_suite.EMBenchmarkSuite.

Covers:
- Each of the four test methods returns a valid TestReport
- Pass/fail logic with reproducible seeded RNG
- Measurement dict shapes and threshold alignment
- Batch runner ordering
"""

import pytest

from benchmarks.em_suite import EMBenchmarkSuite, TestReport


class TestEMBenchmarkSuite:
    """Reproducible EMC suite validation."""

    @pytest.fixture
    def suite(self) -> EMBenchmarkSuite:
        return EMBenchmarkSuite(seed=42)

    # ------------------------------------------------------------------
    # Report structure assertions
    # ------------------------------------------------------------------

    def _assert_report_shape(self, report: TestReport, expected_name: str) -> None:
        assert report.name == expected_name
        assert isinstance(report.passed, bool)
        assert isinstance(report.measurements, dict)
        assert isinstance(report.thresholds, dict)
        assert isinstance(report.timestamp, float)
        assert isinstance(report.notes, list)
        # Every measurement must have a matching threshold
        assert set(report.measurements.keys()) == set(report.thresholds.keys())
        # All values are numeric
        for v in report.measurements.values():
            assert isinstance(v, (int, float))
        for v in report.thresholds.values():
            assert isinstance(v, (int, float))

    # ------------------------------------------------------------------
    # 1. Signal Integrity
    # ------------------------------------------------------------------

    def test_signal_integrity_returns_report(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_signal_integrity()
        self._assert_report_shape(report, "signal_integrity")

    def test_signal_integrity_pass_with_good_seed(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_signal_integrity()
        # Seed 42 generates nominal values well inside limits
        assert report.passed is True

    def test_signal_integrity_failure_mode(self) -> None:
        # Force a marginal seed that pushes one metric out of bounds
        suite = EMBenchmarkSuite(seed=19)
        report = suite.test_signal_integrity()
        assert report.passed is False

    def test_signal_integrity_threshold_keys(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_signal_integrity()
        expected = {
            "eye_height_mV",
            "eye_width_ps",
            "jitter_rms_ps",
            "rise_time_ps",
            "fall_time_ps",
            "crosstalk_db",
        }
        assert set(report.measurements.keys()) == expected

    # ------------------------------------------------------------------
    # 2. Thermal Emission
    # ------------------------------------------------------------------

    def test_thermal_emission_returns_report(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_thermal_emission()
        self._assert_report_shape(report, "thermal_emission")

    def test_thermal_emission_pass_with_good_seed(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_thermal_emission()
        assert report.passed is True

    def test_thermal_emission_failure_mode(self) -> None:
        suite = EMBenchmarkSuite(seed=2)
        report = suite.test_thermal_emission()
        # With seed=2, delta_t spikes above 35 °C in practice
        assert report.passed is False

    def test_thermal_emission_hotspot_count_is_int(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_thermal_emission()
        assert isinstance(report.measurements["hotspot_count"], int)
        assert report.measurements["hotspot_count"] >= 0

    # ------------------------------------------------------------------
    # 3. Power Line Noise
    # ------------------------------------------------------------------

    def test_power_line_noise_returns_report(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_power_line_noise()
        self._assert_report_shape(report, "power_line_noise")

    def test_power_line_noise_pass_with_good_seed(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_power_line_noise()
        assert report.passed is True

    def test_power_line_noise_failure_mode(self) -> None:
        suite = EMBenchmarkSuite(seed=5)
        report = suite.test_power_line_noise()
        assert report.passed is False

    def test_power_line_noise_ripple_positive(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_power_line_noise()
        assert report.measurements["ripple_12v_mVpp"] >= 0
        assert report.measurements["ripple_5v_mVpp"] >= 0
        assert report.measurements["ripple_3v3_mVpp"] >= 0

    # ------------------------------------------------------------------
    # 4. RF Interference
    # ------------------------------------------------------------------

    def test_rf_interference_returns_report(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_rf_interference()
        self._assert_report_shape(report, "rf_interference")

    def test_rf_interference_pass_with_good_seed(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_rf_interference()
        assert report.passed is True

    def test_rf_interference_failure_mode(self) -> None:
        suite = EMBenchmarkSuite(seed=2)
        report = suite.test_rf_interference()
        assert report.passed is False

    def test_rf_interference_shield_atten_positive(self, suite: EMBenchmarkSuite) -> None:
        report = suite.test_rf_interference()
        assert report.measurements["shield_atten_db"] >= 0

    # ------------------------------------------------------------------
    # Batch runner
    # ------------------------------------------------------------------

    def test_run_all_order_and_length(self, suite: EMBenchmarkSuite) -> None:
        reports = suite.run_all()
        assert len(reports) == 4
        names = [r.name for r in reports]
        assert names == [
            "signal_integrity",
            "thermal_emission",
            "power_line_noise",
            "rf_interference",
        ]

    def test_run_all_reports_are_passed_with_good_seed(self, suite: EMBenchmarkSuite) -> None:
        reports = suite.run_all()
        assert all(r.passed for r in reports)

    def test_run_all_includes_timestamps(self, suite: EMBenchmarkSuite) -> None:
        reports = suite.run_all()
        timestamps = [r.timestamp for r in reports]
        assert timestamps == sorted(timestamps)

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    def test_judge_below_boundary(self) -> None:
        assert EMBenchmarkSuite._judge(5.0, 5.0, "below") is True
        assert EMBenchmarkSuite._judge(5.01, 5.0, "below") is False

    def test_judge_above_boundary(self) -> None:
        assert EMBenchmarkSuite._judge(5.0, 5.0, "above") is True
        assert EMBenchmarkSuite._judge(4.99, 5.0, "above") is False

    def test_judge_bad_direction_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown direction"):
            EMBenchmarkSuite._judge(1.0, 2.0, "sideways")

    def test_reproducibility(self) -> None:
        a = EMBenchmarkSuite(seed=99).run_all()
        b = EMBenchmarkSuite(seed=99).run_all()
        for ra, rb in zip(a, b):
            assert ra.measurements == rb.measurements
            assert ra.passed == rb.passed
