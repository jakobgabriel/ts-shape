"""Weekly/monthly summary module.

Roll up daily metrics to weekly/monthly summaries:
- Weekly summary of KPIs
- Monthly totals and averages
- Period-over-period comparison
"""

import pandas as pd  # type: ignore
import numpy as np
from typing import Optional, Dict

from ts_shape.utils.base import Base


class PeriodSummary(Base):
    """Aggregate daily metrics into weekly/monthly summaries.

    Example usage:
        summary = PeriodSummary(df)

        # Weekly rollup
        weekly = summary.weekly_summary(
            counter_uuid='production_counter',
            ok_counter_uuid='good_parts',
            nok_counter_uuid='bad_parts',
        )

        # Monthly rollup
        monthly = summary.monthly_summary(
            counter_uuid='production_counter',
        )

        # Compare two periods
        comparison = summary.compare_periods(
            counter_uuid='production_counter',
            period1=('2024-01-01', '2024-01-07'),
            period2=('2024-01-08', '2024-01-14'),
        )
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        *,
        time_column: str = "systime",
    ) -> None:
        super().__init__(dataframe, column_name=time_column)
        self.time_column = time_column

    def _daily_counter(
        self,
        uuid: str,
        value_column: str = "value_integer",
    ) -> pd.DataFrame:
        """Get daily counter deltas."""
        data = (
            self.dataframe[self.dataframe["uuid"] == uuid]
            .copy()
            .sort_values(self.time_column)
        )
        if data.empty:
            return pd.DataFrame(columns=["date", "quantity"])

        data[self.time_column] = pd.to_datetime(data[self.time_column])
        data["date"] = data[self.time_column].dt.date

        results = []
        for date, grp in data.groupby("date"):
            grp = grp.sort_values(self.time_column)
            qty = max(0, grp[value_column].iloc[-1] - grp[value_column].iloc[0])
            results.append({"date": date, "quantity": int(qty)})

        return pd.DataFrame(results)

    def weekly_summary(
        self,
        counter_uuid: str,
        ok_counter_uuid: Optional[str] = None,
        nok_counter_uuid: Optional[str] = None,
        *,
        value_column: str = "value_integer",
    ) -> pd.DataFrame:
        """Roll up daily production to weekly summaries.

        Args:
            counter_uuid: UUID of production counter.
            ok_counter_uuid: UUID of good parts counter (optional).
            nok_counter_uuid: UUID of defective parts counter (optional).
            value_column: Column containing counter values.

        Returns:
            DataFrame with columns:
            - week_start, week_end, total_production, daily_avg,
              production_days, [ok_parts, nok_parts, quality_pct]
        """
        daily = self._daily_counter(counter_uuid, value_column)
        if daily.empty:
            cols = ["week_start", "week_end", "total_production", "daily_avg", "production_days"]
            if ok_counter_uuid:
                cols.extend(["ok_parts", "nok_parts", "quality_pct"])
            return pd.DataFrame(columns=cols)

        daily["date"] = pd.to_datetime(daily["date"])

        # Quality data
        ok_daily = None
        nok_daily = None
        if ok_counter_uuid:
            ok_daily = self._daily_counter(ok_counter_uuid, value_column)
            if not ok_daily.empty:
                ok_daily["date"] = pd.to_datetime(ok_daily["date"])
        if nok_counter_uuid:
            nok_daily = self._daily_counter(nok_counter_uuid, value_column)
            if not nok_daily.empty:
                nok_daily["date"] = pd.to_datetime(nok_daily["date"])

        daily = daily.set_index("date")
        results = []

        for week_start, grp in daily.groupby(pd.Grouper(freq="W-MON", label="left", closed="left")):
            if grp.empty:
                continue

            total_prod = grp["quantity"].sum()
            days = len(grp)
            daily_avg = total_prod / days if days > 0 else 0

            week_end = week_start + pd.Timedelta(days=6)

            row = {
                "week_start": week_start.date(),
                "week_end": week_end.date(),
                "total_production": int(total_prod),
                "daily_avg": round(daily_avg, 1),
                "production_days": days,
            }

            if ok_daily is not None and not ok_daily.empty:
                ok_week = ok_daily[
                    (ok_daily["date"] >= week_start) & (ok_daily["date"] <= week_end)
                ]
                row["ok_parts"] = int(ok_week["quantity"].sum()) if not ok_week.empty else 0

            if nok_daily is not None and not nok_daily.empty:
                nok_week = nok_daily[
                    (nok_daily["date"] >= week_start) & (nok_daily["date"] <= week_end)
                ]
                row["nok_parts"] = int(nok_week["quantity"].sum()) if not nok_week.empty else 0

            if "ok_parts" in row and "nok_parts" in row:
                total_q = row["ok_parts"] + row["nok_parts"]
                row["quality_pct"] = round(
                    row["ok_parts"] / total_q * 100 if total_q > 0 else 0, 1
                )

            results.append(row)

        return pd.DataFrame(results)

    def monthly_summary(
        self,
        counter_uuid: str,
        ok_counter_uuid: Optional[str] = None,
        nok_counter_uuid: Optional[str] = None,
        *,
        value_column: str = "value_integer",
    ) -> pd.DataFrame:
        """Roll up daily production to monthly summaries.

        Args:
            counter_uuid: UUID of production counter.
            ok_counter_uuid: UUID of good parts counter (optional).
            nok_counter_uuid: UUID of defective parts counter (optional).
            value_column: Column containing counter values.

        Returns:
            DataFrame with columns:
            - year, month, total_production, daily_avg,
              production_days, [ok_parts, nok_parts, quality_pct]
        """
        daily = self._daily_counter(counter_uuid, value_column)
        if daily.empty:
            cols = ["year", "month", "total_production", "daily_avg", "production_days"]
            if ok_counter_uuid:
                cols.extend(["ok_parts", "nok_parts", "quality_pct"])
            return pd.DataFrame(columns=cols)

        daily["date"] = pd.to_datetime(daily["date"])

        ok_daily = None
        nok_daily = None
        if ok_counter_uuid:
            ok_daily = self._daily_counter(ok_counter_uuid, value_column)
            if not ok_daily.empty:
                ok_daily["date"] = pd.to_datetime(ok_daily["date"])
        if nok_counter_uuid:
            nok_daily = self._daily_counter(nok_counter_uuid, value_column)
            if not nok_daily.empty:
                nok_daily["date"] = pd.to_datetime(nok_daily["date"])

        daily = daily.set_index("date")
        results = []

        for month_start, grp in daily.groupby(pd.Grouper(freq="MS")):
            if grp.empty:
                continue

            total_prod = grp["quantity"].sum()
            days = len(grp)
            daily_avg = total_prod / days if days > 0 else 0

            month_end = month_start + pd.offsets.MonthEnd(0)

            row = {
                "year": month_start.year,
                "month": month_start.month,
                "total_production": int(total_prod),
                "daily_avg": round(daily_avg, 1),
                "production_days": days,
            }

            if ok_daily is not None and not ok_daily.empty:
                ok_month = ok_daily[
                    (ok_daily["date"] >= month_start) & (ok_daily["date"] <= month_end)
                ]
                row["ok_parts"] = int(ok_month["quantity"].sum()) if not ok_month.empty else 0

            if nok_daily is not None and not nok_daily.empty:
                nok_month = nok_daily[
                    (nok_daily["date"] >= month_start) & (nok_daily["date"] <= month_end)
                ]
                row["nok_parts"] = int(nok_month["quantity"].sum()) if not nok_month.empty else 0

            if "ok_parts" in row and "nok_parts" in row:
                total_q = row["ok_parts"] + row["nok_parts"]
                row["quality_pct"] = round(
                    row["ok_parts"] / total_q * 100 if total_q > 0 else 0, 1
                )

            results.append(row)

        return pd.DataFrame(results)

    def compare_periods(
        self,
        counter_uuid: str,
        period1: tuple[str, str],
        period2: tuple[str, str],
        *,
        value_column: str = "value_integer",
    ) -> pd.DataFrame:
        """Compare production between two time periods.

        Args:
            counter_uuid: UUID of production counter.
            period1: Tuple of (start_date, end_date) for first period.
            period2: Tuple of (start_date, end_date) for second period.
            value_column: Column containing counter values.

        Returns:
            DataFrame with columns:
            - metric, period1_value, period2_value, change, change_pct
        """
        daily = self._daily_counter(counter_uuid, value_column)
        if daily.empty:
            return pd.DataFrame(
                columns=["metric", "period1_value", "period2_value", "change", "change_pct"]
            )

        daily["date"] = pd.to_datetime(daily["date"]).dt.date

        p1_start = pd.to_datetime(period1[0]).date()
        p1_end = pd.to_datetime(period1[1]).date()
        p2_start = pd.to_datetime(period2[0]).date()
        p2_end = pd.to_datetime(period2[1]).date()

        p1_data = daily[(daily["date"] >= p1_start) & (daily["date"] <= p1_end)]
        p2_data = daily[(daily["date"] >= p2_start) & (daily["date"] <= p2_end)]

        def _metrics(data: pd.DataFrame) -> Dict[str, float]:
            if data.empty:
                return {"total_production": 0, "daily_avg": 0.0, "production_days": 0,
                        "min_daily": 0, "max_daily": 0}
            return {
                "total_production": int(data["quantity"].sum()),
                "daily_avg": round(data["quantity"].mean(), 1),
                "production_days": len(data),
                "min_daily": int(data["quantity"].min()),
                "max_daily": int(data["quantity"].max()),
            }

        m1 = _metrics(p1_data)
        m2 = _metrics(p2_data)

        rows = []
        for metric in m1:
            v1 = m1[metric]
            v2 = m2[metric]
            change = v2 - v1
            change_pct = (change / v1 * 100) if v1 != 0 else 0.0

            rows.append({
                "metric": metric,
                "period1_value": v1,
                "period2_value": v2,
                "change": round(change, 1),
                "change_pct": round(change_pct, 1),
            })

        return pd.DataFrame(rows)
