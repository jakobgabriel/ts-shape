import pandas as pd  # type: ignore
from typing import List, Dict, Any

from ts_shape.utils.base import Base


class LineThroughputEvents(Base):
    """Production: Line Throughput

    Methods:
    - count_parts: Part counts per fixed window from a monotonically increasing counter.
    - takt_adherence: Cycle time violations against a takt time from step/boolean triggers.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        *,
        event_uuid: str = "prod:throughput",
        time_column: str = "systime",
    ) -> None:
        super().__init__(dataframe, column_name=time_column)
        self.event_uuid = event_uuid
        self.time_column = time_column

    def count_parts(
        self,
        counter_uuid: str,
        *,
        value_column: str = "value_integer",
        window: str = "1m",
    ) -> pd.DataFrame:
        """Compute parts per window for a counter uuid.

        Returns columns: window_start, uuid, source_uuid, is_delta, count
        """
        c = (
            self.dataframe[self.dataframe["uuid"] == counter_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        if c.empty:
            return pd.DataFrame(
                columns=["window_start", "uuid", "source_uuid", "is_delta", "count"]
            )
        c[self.time_column] = pd.to_datetime(c[self.time_column])
        c = c.set_index(self.time_column)
        # take diff of last values within each window
        grp = c[value_column].resample(window)
        counts = grp.max().fillna(method="ffill").diff().fillna(0).clip(lower=0)
        out = counts.to_frame("count").reset_index().rename(columns={self.time_column: "window_start"})
        out["uuid"] = self.event_uuid
        out["source_uuid"] = counter_uuid
        out["is_delta"] = True
        return out

    def takt_adherence(
        self,
        cycle_uuid: str,
        *,
        value_column: str = "value_bool",
        takt_time: str = "60s",
        min_violation: str = "0s",
    ) -> pd.DataFrame:
        """Flag cycles whose durations exceed the takt_time.

        For boolean triggers: detect True rising edges as cycle boundaries.
        For integer steps: detect increments as cycle boundaries.

        Returns: systime (at boundary), uuid, source_uuid, is_delta, cycle_time_seconds, violation
        """
        s = (
            self.dataframe[self.dataframe["uuid"] == cycle_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        if s.empty:
            return pd.DataFrame(
                columns=[
                    "systime",
                    "uuid",
                    "source_uuid",
                    "is_delta",
                    "cycle_time_seconds",
                    "violation",
                ]
            )
        s[self.time_column] = pd.to_datetime(s[self.time_column])
        if value_column == "value_bool":
            s["prev"] = s[value_column].shift(fill_value=False)
            edges = s[(~s["prev"]) & (s[value_column].fillna(False))]
            times = edges[self.time_column].reset_index(drop=True)
        else:
            s["prev"] = s[value_column].shift(1)
            edges = s[s[value_column].fillna(0) != s["prev"].fillna(0)]
            times = edges[self.time_column].reset_index(drop=True)
        if len(times) < 2:
            return pd.DataFrame(
                columns=[
                    "systime",
                    "uuid",
                    "source_uuid",
                    "is_delta",
                    "cycle_time_seconds",
                    "violation",
                ]
            )
        cycle_times = (times.diff().dt.total_seconds()).iloc[1:].reset_index(drop=True)
        min_td = pd.to_timedelta(min_violation).total_seconds()
        target = pd.to_timedelta(takt_time).total_seconds()
        viol = (cycle_times - target) >= min_td
        out = pd.DataFrame(
            {
                "systime": times.iloc[1:].reset_index(drop=True),
                "uuid": self.event_uuid,
                "source_uuid": cycle_uuid,
                "is_delta": True,
                "cycle_time_seconds": cycle_times,
                "violation": viol,
            }
        )
        return out

