"""Tests for ShiftHandoverReport module."""

import pandas as pd
import pytest

from ts_shape.events.production.shift_handover import ShiftHandoverReport


def _make_handover_df():
    """Create sample data for shift handover testing."""
    rows = []
    # Production counter
    for i, hour in enumerate(range(6, 22)):
        t = pd.Timestamp(f"2024-01-01 {hour:02d}:00:00")
        rows.append({"systime": t, "uuid": "prod_counter", "value_integer": i * 50})
    # OK counter
    for i, hour in enumerate(range(6, 22)):
        t = pd.Timestamp(f"2024-01-01 {hour:02d}:00:00")
        rows.append({"systime": t, "uuid": "ok_counter", "value_integer": i * 48})
    # NOK counter
    for i, hour in enumerate(range(6, 22)):
        t = pd.Timestamp(f"2024-01-01 {hour:02d}:00:00")
        rows.append({"systime": t, "uuid": "nok_counter", "value_integer": i * 2})
    # Machine state
    states = (["Running"] * 3 + ["Stopped"] + ["Running"] * 3 + ["Stopped"] +
              ["Running"] * 3 + ["Stopped"] + ["Running"] * 3 + ["Stopped"])
    for hour, state in zip(range(6, 22), states):
        t = pd.Timestamp(f"2024-01-01 {hour:02d}:00:00")
        rows.append({"systime": t, "uuid": "machine_state", "value_string": state})

    return pd.DataFrame(rows)


class TestShiftHandoverReport:

    def test_generate_report(self):
        df = _make_handover_df()
        report = ShiftHandoverReport(df)
        result = report.generate_report(
            counter_uuid="prod_counter",
            ok_counter_uuid="ok_counter",
            nok_counter_uuid="nok_counter",
            state_uuid="machine_state",
            targets={"shift_1": 400, "shift_2": 400, "shift_3": 400},
        )
        assert not result.empty
        assert "production" in result.columns
        assert "quality_pct" in result.columns
        assert "availability_pct" in result.columns

    def test_generate_report_specific_date(self):
        df = _make_handover_df()
        report = ShiftHandoverReport(df)
        result = report.generate_report(
            counter_uuid="prod_counter",
            ok_counter_uuid="ok_counter",
            nok_counter_uuid="nok_counter",
            state_uuid="machine_state",
            report_date="2024-01-01",
        )
        assert not result.empty

    def test_highlight_issues(self):
        df = _make_handover_df()
        report = ShiftHandoverReport(df)
        issues = report.highlight_issues(
            counter_uuid="prod_counter",
            ok_counter_uuid="ok_counter",
            nok_counter_uuid="nok_counter",
            state_uuid="machine_state",
            targets={"shift_1": 400, "shift_2": 400, "shift_3": 400},
            thresholds={
                "production_achievement_pct": 95,
                "quality_pct": 99,
                "availability_pct": 95,
            },
        )
        assert isinstance(issues, list)
        # With our synthetic data, some thresholds should be violated
        for issue in issues:
            assert "shift" in issue
            assert "metric" in issue
            assert "severity" in issue

    def test_empty_data(self):
        df = pd.DataFrame(columns=["systime", "uuid", "value_integer", "value_string"])
        report = ShiftHandoverReport(df)
        result = report.generate_report(
            counter_uuid="x",
            ok_counter_uuid="y",
            nok_counter_uuid="z",
            state_uuid="w",
        )
        assert result.empty

    def test_highlight_issues_empty(self):
        df = pd.DataFrame(columns=["systime", "uuid", "value_integer", "value_string"])
        report = ShiftHandoverReport(df)
        issues = report.highlight_issues(
            counter_uuid="x",
            ok_counter_uuid="y",
            nok_counter_uuid="z",
            state_uuid="w",
        )
        assert issues == []
