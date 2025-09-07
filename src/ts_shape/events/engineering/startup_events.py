import pandas as pd  # type: ignore
from typing import List, Dict, Any

from ts_shape.utils.base import Base


class StartupDetectionEvents(Base):
    """
    Detect equipment startup intervals based on threshold crossings or
    sustained positive slope in a numeric metric (speed, temperature, etc.).

    Schema assumptions (columns):
    - uuid, sequence_number, systime, plctime, is_delta
    - value_integer, value_string, value_double, value_bool, value_bytes
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        target_uuid: str,
        *,
        event_uuid: str = "startup_event",
        value_column: str = "value_double",
        time_column: str = "systime",
    ) -> None:
        super().__init__(dataframe, column_name=time_column)
        self.target_uuid = target_uuid
        self.event_uuid = event_uuid
        self.value_column = value_column
        self.time_column = time_column

        self.series = (
            self.dataframe[self.dataframe["uuid"] == self.target_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        self.series[self.time_column] = pd.to_datetime(self.series[self.time_column])

    def detect_startup_by_threshold(
        self,
        *,
        threshold: float,
        hysteresis: tuple[float, float] | None = None,
        min_above: str = "0s",
    ) -> pd.DataFrame:
        """
        Startup begins at first crossing above `threshold` (or hysteresis enter)
        and is valid only if the metric stays above the (exit) threshold for at
        least `min_above`.

        Returns:
            DataFrame with columns: start, end, uuid, is_delta, method, threshold.
        """
        if self.series.empty:
            return pd.DataFrame(columns=["start", "end", "uuid", "is_delta", "method", "threshold"])

        enter_thr = threshold if hysteresis is None else hysteresis[0]
        exit_thr = threshold if hysteresis is None else hysteresis[1]
        min_above_td = pd.to_timedelta(min_above)

        s = self.series[[self.time_column, self.value_column]].copy()
        above_enter = s[self.value_column] >= enter_thr
        rising = (~above_enter.shift(fill_value=False)) & above_enter
        rise_times = s.loc[rising, self.time_column]

        events: List[Dict[str, Any]] = []
        for t0 in rise_times:
            # ensure dwell above exit threshold for min_above
            win = s[(s[self.time_column] >= t0) & (s[self.time_column] <= t0 + min_above_td)]
            if win.empty:
                continue
            if (win[self.value_column] >= exit_thr).all():
                events.append(
                    {
                        "start": t0,
                        "end": t0 + min_above_td,
                        "uuid": self.event_uuid,
                        "is_delta": True,
                        "method": "threshold",
                        "threshold": float(threshold),
                    }
                )

        return pd.DataFrame(events)

    def detect_startup_by_slope(
        self,
        *,
        min_slope: float,
        slope_window: str = "0s",
        min_duration: str = "0s",
    ) -> pd.DataFrame:
        """
        Startup intervals where per-second slope >= `min_slope` for at least
        `min_duration`. `slope_window` is accepted for API completeness but the
        current implementation uses instantaneous slope between samples.

        Returns:
            DataFrame with columns: start, end, uuid, is_delta, method, min_slope, avg_slope.
        """
        if self.series.empty:
            return pd.DataFrame(columns=["start", "end", "uuid", "is_delta", "method", "min_slope", "avg_slope"])

        s = self.series[[self.time_column, self.value_column]].copy()
        s["dt_s"] = s[self.time_column].diff().dt.total_seconds()
        s["dv"] = s[self.value_column].diff()
        s["slope"] = s["dv"] / s["dt_s"]
        mask = s["slope"] >= float(min_slope)

        gid = (mask != mask.shift()).cumsum()
        min_d = pd.to_timedelta(min_duration)
        events: List[Dict[str, Any]] = []
        for _, seg in s.groupby(gid):
            seg_mask = mask.loc[seg.index]
            if not seg_mask.any():
                continue
            start_t = seg.loc[seg_mask, self.time_column].iloc[0]
            end_t = seg.loc[seg_mask, self.time_column].iloc[-1]
            if (end_t - start_t) < min_d:
                continue
            avg_slope = seg.loc[seg_mask, "slope"].mean()
            events.append(
                {
                    "start": start_t,
                    "end": end_t,
                    "uuid": self.event_uuid,
                    "is_delta": True,
                    "method": "slope",
                    "min_slope": float(min_slope),
                    "avg_slope": float(avg_slope) if pd.notna(avg_slope) else None,
                }
            )

        return pd.DataFrame(events)

