"""
EMBenchmarkSuite — Electromagnetic Compatibility Test Suite for Fleet Hardware.

Runs four canonical EMC tests on fleet hardware modules:
1. Signal Integrity (eye diagram metrics, jitter, rise/fall times)
2. Thermal Emission (IR temperature deltas, hotspot mapping)
3. Power Line Noise (conducted EMI on DC rails)
4. RF Interference (radiated emissions & susceptibility)

Each method returns a Pass/Fail Report dict with numerical measurements.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestReport:
    """Immutable-ish report for a single EMC test."""
    __test__ = False  # Prevent pytest collection

    name: str
    passed: bool
    measurements: dict[str, float]
    thresholds: dict[str, float]
    timestamp: float = field(default_factory=time.time)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "passed": self.passed,
            "measurements": self.measurements,
            "thresholds": self.thresholds,
            "timestamp": self.timestamp,
            "notes": self.notes,
        }


class EMBenchmarkSuite:
    """
    Orchestrates electromagnetic-compatibility validation for fleet hardware.

    Typical usage:
        suite = EMBenchmarkSuite(seed=42)  # reproducible in tests
        report = suite.test_signal_integrity()
        assert report.passed
    """

    def __init__(self, seed: int | None = None) -> None:
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _gauss(self, mu: float, sigma: float) -> float:
        return self._rng.gauss(mu, sigma)

    @staticmethod
    def _judge(value: float, limit: float, direction: str = "below") -> bool:
        """Return True if value satisfies the limit constraint."""
        if direction == "below":
            return value <= limit
        if direction == "above":
            return value >= limit
        raise ValueError(f"Unknown direction: {direction}")

    # ------------------------------------------------------------------
    # 1. Signal Integrity
    # ------------------------------------------------------------------

    def test_signal_integrity(self) -> TestReport:
        """
        Validate high-speed differential-pair signal integrity.

        Measurements:
            - eye_height_mV     : vertical eye opening (mV)
            - eye_width_ps      : horizontal eye opening (ps)
            - jitter_rms_ps     : random jitter (RMS, ps)
            - rise_time_ps      : 20 %-80 % rise time (ps)
            - fall_time_ps      : 20 %-80 % fall time (ps)
            - crosstalk_db      : near-end crosstalk (dB)

        Thresholds mirror typical PCIe-Gen4 / 10GbE margins.
        """
        thresholds = {
            "eye_height_mV": 120.0,   # min
            "eye_width_ps": 30.0,      # min
            "jitter_rms_ps": 5.0,      # max
            "rise_time_ps": 25.0,      # max
            "fall_time_ps": 25.0,      # max
            "crosstalk_db": -30.0,     # max (less negative = worse)
        }

        # Simulate readings (slightly jittery around nominal)
        measurements = {
            "eye_height_mV": self._gauss(180.0, 20.0),
            "eye_width_ps": self._gauss(45.0, 5.0),
            "jitter_rms_ps": abs(self._gauss(3.0, 0.8)),
            "rise_time_ps": abs(self._gauss(18.0, 2.5)),
            "fall_time_ps": abs(self._gauss(18.5, 2.5)),
            "crosstalk_db": self._gauss(-35.0, 3.0),
        }

        passed = (
            self._judge(measurements["eye_height_mV"], thresholds["eye_height_mV"], "above")
            and self._judge(measurements["eye_width_ps"], thresholds["eye_width_ps"], "above")
            and self._judge(measurements["jitter_rms_ps"], thresholds["jitter_rms_ps"], "below")
            and self._judge(measurements["rise_time_ps"], thresholds["rise_time_ps"], "below")
            and self._judge(measurements["fall_time_ps"], thresholds["fall_time_ps"], "below")
            and self._judge(measurements["crosstalk_db"], thresholds["crosstalk_db"], "below")
        )

        notes = []
        if measurements["eye_height_mV"] < thresholds["eye_height_mV"] * 1.2:
            notes.append("Eye height marginal — inspect PCB stack-up.")
        if measurements["jitter_rms_ps"] > thresholds["jitter_rms_ps"] * 0.8:
            notes.append("Jitter approaching limit — check ref-clock source.")

        return TestReport(
            name="signal_integrity",
            passed=passed,
            measurements=measurements,
            thresholds=thresholds,
            notes=notes,
        )

    # ------------------------------------------------------------------
    # 2. Thermal Emission
    # ------------------------------------------------------------------

    def test_thermal_emission(self) -> TestReport:
        """
        Validate thermal hotspot deltas under worst-case load.

        Measurements:
            - delta_t_max_C      : max temperature rise above ambient (°C)
            - hotspot_count      : number of spots > 10 °C rise
            - uniformity_index   : std-dev of IR grid (lower is better)
            - soak_time_s        : time to reach steady state (s)
            - emissivity_est     : derived surface emissivity (0-1)

        Thresholds align with MIL-STD-810G Method 501.7 + fleet derating.
        """
        thresholds = {
            "delta_t_max_C": 35.0,      # max rise allowed
            "hotspot_count": 3,         # max discrete hotspots
            "uniformity_index": 8.0,    # max std-dev
            "soak_time_s": 600.0,       # max seconds to steady state
            "emissivity_est": 0.85,     # min (for accurate IR)
        }

        measurements = {
            "delta_t_max_C": self._gauss(28.0, 5.0),
            "hotspot_count": max(0, int(round(self._gauss(1.5, 1.0)))),
            "uniformity_index": abs(self._gauss(4.5, 1.5)),
            "soak_time_s": abs(self._gauss(350.0, 80.0)),
            "emissivity_est": max(0.0, min(1.0, self._gauss(0.90, 0.05))),
        }

        passed = (
            self._judge(measurements["delta_t_max_C"], thresholds["delta_t_max_C"], "below")
            and self._judge(measurements["hotspot_count"], thresholds["hotspot_count"], "below")
            and self._judge(measurements["uniformity_index"], thresholds["uniformity_index"], "below")
            and self._judge(measurements["soak_time_s"], thresholds["soak_time_s"], "below")
            and self._judge(measurements["emissivity_est"], thresholds["emissivity_est"], "above")
        )

        notes = []
        if measurements["delta_t_max_C"] > 30.0:
            notes.append("Thermal headroom thin — consider heatsink fin density.")
        if measurements["uniformity_index"] > 6.0:
            notes.append("Uneven heat spread — verify TIM application.")

        return TestReport(
            name="thermal_emission",
            passed=passed,
            measurements=measurements,
            thresholds=thresholds,
            notes=notes,
        )

    # ------------------------------------------------------------------
    # 3. Power Line Noise
    # ------------------------------------------------------------------

    def test_power_line_noise(self) -> TestReport:
        """
        Conducted EMI scan on primary DC rails (12 V, 5 V, 3.3 V).

        Measurements:
            - ripple_12v_mVpp    : 12 V rail ripple (mV pp)
            - ripple_5v_mVpp     : 5 V rail ripple (mV pp)
            - ripple_3v3_mVpp    : 3.3 V rail ripple (mV pp)
            - psrr_12v_db        : power-supply rejection ratio at 1 kHz
            - psrr_5v_db         : same for 5 V rail
            - psrr_3v3_db        : same for 3.3 V rail

        Thresholds follow IPC-9592B Class B + 6 dB fleet margin.
        """
        thresholds = {
            "ripple_12v_mVpp": 120.0,
            "ripple_5v_mVpp": 50.0,
            "ripple_3v3_mVpp": 30.0,
            "psrr_12v_db": 60.0,
            "psrr_5v_db": 55.0,
            "psrr_3v3_db": 50.0,
        }

        measurements = {
            "ripple_12v_mVpp": abs(self._gauss(70.0, 15.0)),
            "ripple_5v_mVpp": abs(self._gauss(25.0, 8.0)),
            "ripple_3v3_mVpp": abs(self._gauss(15.0, 5.0)),
            "psrr_12v_db": self._gauss(72.0, 5.0),
            "psrr_5v_db": self._gauss(65.0, 4.0),
            "psrr_3v3_db": self._gauss(58.0, 4.0),
        }

        passed = (
            self._judge(measurements["ripple_12v_mVpp"], thresholds["ripple_12v_mVpp"], "below")
            and self._judge(measurements["ripple_5v_mVpp"], thresholds["ripple_5v_mVpp"], "below")
            and self._judge(measurements["ripple_3v3_mVpp"], thresholds["ripple_3v3_mVpp"], "below")
            and self._judge(measurements["psrr_12v_db"], thresholds["psrr_12v_db"], "above")
            and self._judge(measurements["psrr_5v_db"], thresholds["psrr_5v_db"], "above")
            and self._judge(measurements["psrr_3v3_db"], thresholds["psrr_3v3_db"], "above")
        )

        notes = []
        if measurements["ripple_3v3_mVpp"] > thresholds["ripple_3v3_mVpp"] * 0.7:
            notes.append("3.3 V ripple nearing limit — review LDO bypass caps.")
        if measurements["psrr_3v3_db"] < thresholds["psrr_3v3_db"] + 10.0:
            notes.append("3.3 V PSRR low — sensitive analog rails at risk.")

        return TestReport(
            name="power_line_noise",
            passed=passed,
            measurements=measurements,
            thresholds=thresholds,
            notes=notes,
        )

    # ------------------------------------------------------------------
    # 4. RF Interference
    # ------------------------------------------------------------------

    def test_rf_interference(self) -> TestReport:
        """
        Radiated emissions (RE) and radiated susceptibility (RS) sweep.

        Measurements:
            - re_max_dbuv_m      : peak radiated emission (dBµV/m)
            - re_margin_db       : margin below CISPR 32 Class B limit
            - rs_1v_m            : field strength where 1 V dip appears (V/m)
            - rs_ber_degradation : bit-error-rate delta during sweep (%)
            - antenna_coupling_db: unintended antenna coupling (dB)
            - shield_atten_db    : enclosure shielding effectiveness (dB)

        Thresholds derived from CISPR 32 / MIL-STD-461G RS103.
        """
        thresholds = {
            "re_max_dbuv_m": 40.0,       # max emission
            "re_margin_db": 6.0,         # min margin below limit
            "rs_1v_m": 10.0,             # min field for 1 V dip (higher = better)
            "rs_ber_degradation": 0.1,   # max BER delta (%)
            "antenna_coupling_db": -40.0,# max coupling (less negative = worse)
            "shield_atten_db": 40.0,     # min shielding attenuation
        }

        measurements = {
            "re_max_dbuv_m": self._gauss(32.0, 4.0),
            "re_margin_db": self._gauss(14.0, 3.0),
            "rs_1v_m": abs(self._gauss(25.0, 6.0)),
            "rs_ber_degradation": abs(self._gauss(0.03, 0.02)),
            "antenna_coupling_db": self._gauss(-48.0, 5.0),
            "shield_atten_db": self._gauss(55.0, 8.0),
        }

        passed = (
            self._judge(measurements["re_max_dbuv_m"], thresholds["re_max_dbuv_m"], "below")
            and self._judge(measurements["re_margin_db"], thresholds["re_margin_db"], "above")
            and self._judge(measurements["rs_1v_m"], thresholds["rs_1v_m"], "above")
            and self._judge(measurements["rs_ber_degradation"], thresholds["rs_ber_degradation"], "below")
            and self._judge(measurements["antenna_coupling_db"], thresholds["antenna_coupling_db"], "below")
            and self._judge(measurements["shield_atten_db"], thresholds["shield_atten_db"], "above")
        )

        notes = []
        if measurements["re_margin_db"] < 10.0:
            notes.append("RE margin slim — review cable routing & gaskets.")
        if measurements["shield_atten_db"] < 50.0:
            notes.append("Shielding below 50 dB — check seam conductivity.")

        return TestReport(
            name="rf_interference",
            passed=passed,
            measurements=measurements,
            thresholds=thresholds,
            notes=notes,
        )

    # ------------------------------------------------------------------
    # Batch runner
    # ------------------------------------------------------------------

    def run_all(self) -> list[TestReport]:
        """Execute the full EMC suite and return reports in canonical order."""
        return [
            self.test_signal_integrity(),
            self.test_thermal_emission(),
            self.test_power_line_noise(),
            self.test_rf_interference(),
        ]
