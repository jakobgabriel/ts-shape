"""Automated shift handover report generation.

Standardize shift-to-shift communication:
- Production summary
- Quality summary
- Downtime summary
- Issues to watch
"""

import pandas as pd  # type: ignore
import numpy as np
from typing import Optional, Dict, List
from datetime import date as DateType

from ts_shape.utils.base import Base


class ShiftHandoverReport(Base):
    """Generate automated shift handover reports.

    Combines production, quality, and downtime data into a single summary
    suitable for shift handover meetings.

    Example usage:
        report = ShiftHandoverReport(df)

        # Generate full report
        result = report.generate_report(
            counter_uuid='production_counter',
            ok_counter_uuid='good_parts',
            nok_counter_uuid='bad_parts',
            state_uuid='machine_state',
            targets={'shift_1': 450, 'shift_2': 450, 'shift_3': 400},
            quality_target_pct=98.0,
        )

        # Highlight issues
        issues = report.highlight_issues(
            counter_uuid='production_counter',
            ok_counter_uuid='good_parts',
            nok_counter_uuid='bad_parts',
            state_uuid='machine_state',
            thresholds={
                'production_achievement_pct': 95,
                'quality_pct': 98,
                'availability_pct': 90,
            },
        )
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        *,
        time_column: str = "systime",
        shift_definitions: Optional[Dict[str, tuple[str, str]]] = None,
    ) -> None:
        super().__init__(dataframe, column_name=time_column)
        self.time_column = time_column
        self.shift_definitions = shift_definitions or {
            "shift_1": ("06:00", "14:00"),
            "shift_2": ("14:00", "22:00"),
            "shift_3": ("22:00", "06:00"),
        }

    def _assign_shift(self, timestamp: pd.Timestamp) -> str:
        time = timestamp.time()
        for shift_name, (start, end) in self.shift_definitions.items():
            start_time = pd.to_datetime(start).time()
            end_time = pd.to_datetime(end).time()
            if start_time < end_time:
                if start_time <= time < end_time:
                    return shift_name
            else:
                if time >= start_time or time < end_time:
                    return shift_name
        return "unknown"

    def _counter_by_shift(
        self,
        uuid: str,
        value_column: str,
    ) -> pd.DataFrame:
        """Get counter deltas grouped by date/shift."""
        data = (
            self.dataframe[self.dataframe["uuid"] == uuid]
            .copy()
            .sort_values(self.time_column)
        )
        if data.empty:
            return pd.DataFrame(columns=["date", "shift", "quantity"])

        data[self.time_column] = pd.to_datetime(data[self.time_column])
        data["shift"] = data[self.time_column].apply(self._assign_shift)
        data["date"] = data[self.time_column].dt.date

        results = []
        for (dt, shift), grp in data.groupby(["date", "shift"]):
            grp = grp.sort_values(self.time_column)
            qty = max(0, grp[value_column].iloc[-1] - grp[value_column].iloc[0])
            results.append({"date": dt, "shift": shift, "quantity": int(qty)})

        return pd.DataFrame(results)

    def _availability_by_shift(
        self,
        state_uuid: str,
        running_value: str,
        value_column: str,
    ) -> pd.DataFrame:
        """Compute availability grouped by date/shift."""
        data = (
            self.dataframe[self.dataframe["uuid"] == state_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        if data.empty:
            return pd.DataFrame(columns=["date", "shift", "availability_pct", "downtime_minutes"])

        data[self.time_column] = pd.to_datetime(data[self.time_column])
        data["shift"] = data[self.time_column].apply(self._assign_shift)
        data["date"] = data[self.time_column].dt.date
        data["is_running"] = data[value_column] == running_value
        data["duration_s"] = data[self.time_column].diff().shift(-1).dt.total_seconds()
        data = data[data["duration_s"].notna()]

        results = []
        for (dt, shift), grp in data.groupby(["date", "shift"]):
            up = grp.loc[grp["is_running"], "duration_s"].sum()
            down = grp.loc[~grp["is_running"], "duration_s"].sum()
            total = up + down
            avail = (up / total * 100) if total > 0 else 0.0
            results.append({
                "date": dt,
                "shift": shift,
                "availability_pct": round(avail, 1),
                "downtime_minutes": round(down / 60, 1),
            })

        return pd.DataFrame(results)

    def generate_report(
        self,
        counter_uuid: str,
        ok_counter_uuid: str,
        nok_counter_uuid: str,
        state_uuid: str,
        *,
        targets: Optional[Dict[str, float]] = None,
        quality_target_pct: float = 98.0,
        availability_target_pct: float = 90.0,
        running_value: str = "Running",
        value_column_counter: str = "value_integer",
        value_column_state: str = "value_string",
        report_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Generate a shift handover report.

        Args:
            counter_uuid: UUID of production counter.
            ok_counter_uuid: UUID of good parts counter.
            nok_counter_uuid: UUID of defective parts counter.
            state_uuid: UUID of machine state signal.
            targets: Per-shift production targets.
            quality_target_pct: Quality target percentage.
            availability_target_pct: Availability target percentage.
            running_value: Value indicating machine is running.
            value_column_counter: Column for counter values.
            value_column_state: Column for state values.
            report_date: Specific date (YYYY-MM-DD). If None, uses latest date.

        Returns:
            DataFrame with columns:
            - date, shift, production, production_target, production_achievement_pct,
              ok_parts, nok_parts, quality_pct, availability_pct, downtime_minutes
        """
        # Production
        prod = self._counter_by_shift(counter_uuid, value_column_counter)
        ok = self._counter_by_shift(ok_counter_uuid, value_column_counter)
        nok = self._counter_by_shift(nok_counter_uuid, value_column_counter)
        avail = self._availability_by_shift(state_uuid, running_value, value_column_state)

        if prod.empty:
            return pd.DataFrame(columns=[
                "date", "shift", "production", "production_target",
                "production_achievement_pct", "ok_parts", "nok_parts",
                "quality_pct", "availability_pct", "downtime_minutes",
            ])

        # Filter to report date
        if report_date:
            target_date = pd.to_datetime(report_date).date()
        else:
            target_date = prod["date"].max()

        prod = prod[prod["date"] == target_date]

        # Merge all data
        result = prod.rename(columns={"quantity": "production"})

        if not ok.empty:
            ok_filt = ok[ok["date"] == target_date].rename(columns={"quantity": "ok_parts"})
            result = result.merge(ok_filt[["date", "shift", "ok_parts"]], on=["date", "shift"], how="left")
        else:
            result["ok_parts"] = 0

        if not nok.empty:
            nok_filt = nok[nok["date"] == target_date].rename(columns={"quantity": "nok_parts"})
            result = result.merge(nok_filt[["date", "shift", "nok_parts"]], on=["date", "shift"], how="left")
        else:
            result["nok_parts"] = 0

        if not avail.empty:
            avail_filt = avail[avail["date"] == target_date]
            result = result.merge(
                avail_filt[["date", "shift", "availability_pct", "downtime_minutes"]],
                on=["date", "shift"], how="left",
            )
        else:
            result["availability_pct"] = 0.0
            result["downtime_minutes"] = 0.0

        result = result.fillna(0)

        # Targets
        if targets:
            result["production_target"] = result["shift"].map(targets).fillna(0)
            result["production_achievement_pct"] = (
                result["production"] / result["production_target"] * 100
            ).where(result["production_target"] > 0, 0).round(1)
        else:
            result["production_target"] = 0.0
            result["production_achievement_pct"] = 0.0

        # Quality
        total = result["ok_parts"] + result["nok_parts"]
        result["quality_pct"] = (
            (result["ok_parts"] / total * 100).where(total > 0, 0).round(1)
        )

        cols = [
            "date", "shift", "production", "production_target",
            "production_achievement_pct", "ok_parts", "nok_parts",
            "quality_pct", "availability_pct", "downtime_minutes",
        ]
        return result[cols].reset_index(drop=True)

    def highlight_issues(
        self,
        counter_uuid: str,
        ok_counter_uuid: str,
        nok_counter_uuid: str,
        state_uuid: str,
        *,
        thresholds: Optional[Dict[str, float]] = None,
        targets: Optional[Dict[str, float]] = None,
        running_value: str = "Running",
        value_column_counter: str = "value_integer",
        value_column_state: str = "value_string",
        report_date: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Identify issues that need attention.

        Args:
            counter_uuid: UUID of production counter.
            ok_counter_uuid: UUID of good parts counter.
            nok_counter_uuid: UUID of defective parts counter.
            state_uuid: UUID of machine state signal.
            thresholds: Minimum acceptable values for each metric.
                Defaults to production_achievement_pct=95, quality_pct=98, availability_pct=90.
            targets: Per-shift production targets.
            running_value: Value indicating machine is running.
            value_column_counter: Column for counter values.
            value_column_state: Column for state values.
            report_date: Specific date (YYYY-MM-DD).

        Returns:
            List of dicts with keys: shift, metric, value, threshold, severity.
            severity is 'warning' (within 5% of threshold) or 'critical'.
        """
        thresholds = thresholds or {
            "production_achievement_pct": 95.0,
            "quality_pct": 98.0,
            "availability_pct": 90.0,
        }

        report = self.generate_report(
            counter_uuid, ok_counter_uuid, nok_counter_uuid, state_uuid,
            targets=targets,
            running_value=running_value,
            value_column_counter=value_column_counter,
            value_column_state=value_column_state,
            report_date=report_date,
        )

        if report.empty:
            return []

        issues = []
        for _, row in report.iterrows():
            for metric, threshold in thresholds.items():
                if metric not in row:
                    continue
                value = row[metric]
                if value < threshold:
                    severity = "warning" if value >= threshold * 0.95 else "critical"
                    issues.append({
                        "shift": row["shift"],
                        "metric": metric,
                        "value": round(float(value), 1),
                        "threshold": threshold,
                        "severity": severity,
                    })

        return issues
