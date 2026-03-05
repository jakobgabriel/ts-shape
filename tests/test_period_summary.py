"""Tests for PeriodSummary module."""

import pandas as pd
import pytest

from ts_shape.events.production.period_summary import PeriodSummary


def _make_multiday_df(days=14):
    """Create production counter data spanning multiple days."""
    rows = []
    counter = 0
    ok_counter = 0
    nok_counter = 0
    for day in range(1, days + 1):
        day_str = f"2024-01-{day:02d}"
        for hour in range(6, 22):
            t = pd.Timestamp(f"{day_str} {hour:02d}:00:00")
            counter += 80
            ok_counter += 77
            nok_counter += 3
            rows.append({"systime": t, "uuid": "prod_counter", "value_integer": counter})
            rows.append({"systime": t, "uuid": "ok_counter", "value_integer": ok_counter})
            rows.append({"systime": t, "uuid": "nok_counter", "value_integer": nok_counter})
    return pd.DataFrame(rows)


class TestPeriodSummary:

    def test_weekly_summary(self):
        df = _make_multiday_df(14)
        summary = PeriodSummary(df)
        result = summary.weekly_summary(counter_uuid="prod_counter")
        assert not result.empty
        assert "week_start" in result.columns
        assert "total_production" in result.columns
        assert "daily_avg" in result.columns

    def test_weekly_summary_with_quality(self):
        df = _make_multiday_df(14)
        summary = PeriodSummary(df)
        result = summary.weekly_summary(
            counter_uuid="prod_counter",
            ok_counter_uuid="ok_counter",
            nok_counter_uuid="nok_counter",
        )
        assert not result.empty
        assert "quality_pct" in result.columns
        # Quality should be ~96.25% (77/80)
        assert result["quality_pct"].iloc[0] > 90

    def test_monthly_summary(self):
        df = _make_multiday_df(14)
        summary = PeriodSummary(df)
        result = summary.monthly_summary(counter_uuid="prod_counter")
        assert not result.empty
        assert "year" in result.columns
        assert "month" in result.columns
        assert result["year"].iloc[0] == 2024

    def test_compare_periods(self):
        df = _make_multiday_df(14)
        summary = PeriodSummary(df)
        result = summary.compare_periods(
            counter_uuid="prod_counter",
            period1=("2024-01-01", "2024-01-07"),
            period2=("2024-01-08", "2024-01-14"),
        )
        assert not result.empty
        assert "metric" in result.columns
        assert "change_pct" in result.columns
        # Both periods have same daily production, so change should be ~0
        total_row = result[result["metric"] == "daily_avg"]
        assert not total_row.empty

    def test_empty_data(self):
        df = pd.DataFrame(columns=["systime", "uuid", "value_integer"])
        summary = PeriodSummary(df)
        assert summary.weekly_summary(counter_uuid="x").empty
        assert summary.monthly_summary(counter_uuid="x").empty
        assert summary.compare_periods(
            counter_uuid="x",
            period1=("2024-01-01", "2024-01-07"),
            period2=("2024-01-08", "2024-01-14"),
        ).empty
