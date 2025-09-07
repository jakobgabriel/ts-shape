import pandas as pd  # type: ignore
from typing import Optional, List, Dict, Any

from ts_shape.utils.base import Base


class SetpointChangeEvents(Base):
    """
    Detect step/ramp changes on a setpoint signal and compute follow-up KPIs
    like time-to-settle and overshoot based on an actual (process) value.

    Schema assumptions (columns):
    - uuid, sequence_number, systime, plctime, is_delta
    - value_integer, value_string, value_double, value_bool, value_bytes
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        setpoint_uuid: str,
        *,
        event_uuid: str = "setpoint_change_event",
        value_column: str = "value_double",
        time_column: str = "systime",
    ) -> None:
        super().__init__(dataframe, column_name=time_column)
        self.setpoint_uuid = setpoint_uuid
        self.event_uuid = event_uuid
        self.value_column = value_column
        self.time_column = time_column

        # isolate setpoint series and ensure proper dtypes/sort
        self.sp = (
            self.dataframe[self.dataframe["uuid"] == self.setpoint_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        self.sp[self.time_column] = pd.to_datetime(self.sp[self.time_column])

    # ---- Change detection ----
    def detect_setpoint_steps(self, min_delta: float, min_hold: str = "0s") -> pd.DataFrame:
        """
        Point events at times where the setpoint changes by >= min_delta and the
        new level holds for at least `min_hold` (no subsequent change within that time).

        Returns:
            DataFrame with columns: start, end (== start), uuid, is_delta,
            change_type='step', magnitude, prev_level, new_level.
        """
        if self.sp.empty:
            return pd.DataFrame(
                columns=[
                    "start",
                    "end",
                    "uuid",
                    "is_delta",
                    "change_type",
                    "magnitude",
                    "prev_level",
                    "new_level",
                ]
            )

        sp = self.sp[[self.time_column, self.value_column]].copy()
        sp["prev"] = sp[self.value_column].shift(1)
        sp["delta"] = sp[self.value_column] - sp["prev"]
        change_mask = sp["delta"].abs() >= float(min_delta)

        # hold condition: next change must be after min_hold
        change_times = sp.loc[change_mask, self.time_column]
        min_hold_td = pd.to_timedelta(min_hold)
        next_change_times = change_times.shift(-1)
        hold_ok = (next_change_times - change_times >= min_hold_td) | next_change_times.isna()
        valid_change_times = change_times[hold_ok]

        rows: List[Dict[str, Any]] = []
        for t in valid_change_times:
            row = sp.loc[sp[self.time_column] == t].iloc[0]
            rows.append(
                {
                    "start": t,
                    "end": t,
                    "uuid": self.event_uuid,
                    "is_delta": True,
                    "change_type": "step",
                    "magnitude": float(row["delta"]),
                    "prev_level": float(row["prev"]) if pd.notna(row["prev"]) else None,
                    "new_level": float(row[self.value_column]),
                }
            )

        return pd.DataFrame(rows)

    def detect_setpoint_ramps(self, min_rate: float, min_duration: str = "0s") -> pd.DataFrame:
        """
        Interval events where |dS/dt| >= min_rate for at least `min_duration`.

        Returns:
            DataFrame with columns: start, end, uuid, is_delta, change_type='ramp',
            avg_rate, delta.
        """
        if self.sp.empty:
            return pd.DataFrame(
                columns=["start", "end", "uuid", "is_delta", "change_type", "avg_rate", "delta"]
            )

        sp = self.sp[[self.time_column, self.value_column]].copy()
        sp["dt_s"] = sp[self.time_column].diff().dt.total_seconds()
        sp["dv"] = sp[self.value_column].diff()
        sp["rate"] = sp["dv"] / sp["dt_s"]
        rate_mask = sp["rate"].abs() >= float(min_rate)

        # group contiguous True segments
        group_id = (rate_mask != rate_mask.shift()).cumsum()
        events: List[Dict[str, Any]] = []
        min_d = pd.to_timedelta(min_duration)
        for gid, seg in sp.groupby(group_id):
            seg_mask_true = rate_mask.loc[seg.index]
            if not seg_mask_true.any():
                continue
            # boundaries
            start_time = seg.loc[seg_mask_true, self.time_column].iloc[0]
            end_time = seg.loc[seg_mask_true, self.time_column].iloc[-1]
            if (end_time - start_time) < min_d:
                continue
            avg_rate = seg.loc[seg_mask_true, "rate"].mean()
            delta = seg.loc[seg_mask_true, "dv"].sum()
            events.append(
                {
                    "start": start_time,
                    "end": end_time,
                    "uuid": self.event_uuid,
                    "is_delta": True,
                    "change_type": "ramp",
                    "avg_rate": float(avg_rate) if pd.notna(avg_rate) else None,
                    "delta": float(delta) if pd.notna(delta) else None,
                }
            )

        return pd.DataFrame(events)

    def detect_setpoint_changes(
        self,
        *,
        min_delta: float = 0.0,
        min_rate: Optional[float] = None,
        min_hold: str = "0s",
        min_duration: str = "0s",
    ) -> pd.DataFrame:
        """
        Unified setpoint change table (steps + ramps) with standardized columns.
        """
        steps = self.detect_setpoint_steps(min_delta=min_delta, min_hold=min_hold)
        ramps = (
            self.detect_setpoint_ramps(min_rate=min_rate, min_duration=min_duration)
            if min_rate is not None
            else pd.DataFrame(columns=["start", "end", "uuid", "is_delta", "change_type", "avg_rate", "delta"])
        )
        # ensure uniform columns
        if not steps.empty:
            steps = steps.assign(avg_rate=None, delta=None)[
                [
                    "start",
                    "end",
                    "uuid",
                    "is_delta",
                    "change_type",
                    "magnitude",
                    "prev_level",
                    "new_level",
                    "avg_rate",
                    "delta",
                ]
            ]
        if not ramps.empty:
            ramps = ramps.assign(magnitude=None, prev_level=None, new_level=None)[
                [
                    "start",
                    "end",
                    "uuid",
                    "is_delta",
                    "change_type",
                    "magnitude",
                    "prev_level",
                    "new_level",
                    "avg_rate",
                    "delta",
                ]
            ]
        frames = [df for df in (steps, ramps) if not df.empty]
        combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(
            columns=[
                "start",
                "end",
                "uuid",
                "is_delta",
                "change_type",
                "magnitude",
                "prev_level",
                "new_level",
                "avg_rate",
                "delta",
            ]
        )
        return combined.sort_values(["start", "end"]) if not combined.empty else combined

    # ---- Follow-up KPIs ----
    def time_to_settle(
        self,
        actual_uuid: str,
        *,
        tol: float,
        hold: str = "0s",
        lookahead: str = "10m",
    ) -> pd.DataFrame:
        """
        For each setpoint change (any change), compute time until the actual signal
        is within ±`tol` of the new setpoint for a continuous duration of `hold`.

        Returns:
            DataFrame with columns: start, uuid, is_delta, t_settle_seconds, settled.
        """
        if self.sp.empty:
            return pd.DataFrame(columns=["start", "uuid", "is_delta", "t_settle_seconds", "settled"])

        actual = (
            self.dataframe[self.dataframe["uuid"] == actual_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        actual[self.time_column] = pd.to_datetime(actual[self.time_column])
        hold_td = pd.to_timedelta(hold)
        look_td = pd.to_timedelta(lookahead)

        # change instants
        sp = self.sp[[self.time_column, self.value_column]].copy()
        sp["prev"] = sp[self.value_column].shift(1)
        sp["delta"] = sp[self.value_column] - sp["prev"]
        change_times = sp.loc[sp["delta"].abs() > 0, [self.time_column, self.value_column]].reset_index(drop=True)

        rows: List[Dict[str, Any]] = []
        for _, c in change_times.iterrows():
            t0 = c[self.time_column]
            s_new = float(c[self.value_column])
            window = actual[(actual[self.time_column] >= t0) & (actual[self.time_column] <= t0 + look_td)]
            if window.empty:
                rows.append({"start": t0, "uuid": self.event_uuid, "is_delta": True, "t_settle_seconds": None, "settled": False})
                continue
            err = (window[self.value_column] - s_new).abs()
            inside = err <= tol

            # time to first entry within tolerance (ignores hold)
            if inside.any():
                first_idx = inside[inside].index[0]
                t_enter = window.loc[first_idx, self.time_column]
            else:
                t_enter = None

            # determine if any contiguous inside segment satisfies hold duration
            settled = False
            if inside.any():
                gid = (inside.ne(inside.shift())).cumsum()
                for _, seg in window.groupby(gid):
                    seg_inside = inside.loc[seg.index]
                    if not seg_inside.iloc[0]:
                        continue
                    start_seg = seg[self.time_column].iloc[0]
                    end_seg = seg[self.time_column].iloc[-1]
                    if (end_seg - start_seg) >= hold_td:
                        settled = True
                        break

            rows.append(
                {
                    "start": t0,
                    "uuid": self.event_uuid,
                    "is_delta": True,
                    "t_settle_seconds": (t_enter - t0).total_seconds() if t_enter is not None else None,
                    "settled": bool(settled),
                }
            )

        return pd.DataFrame(rows)

    def overshoot_metrics(
        self,
        actual_uuid: str,
        *,
        window: str = "10m",
    ) -> pd.DataFrame:
        """
        For each change, compute peak overshoot relative to the new setpoint
        within a lookahead window.

        Returns:
            DataFrame with columns: start, uuid, is_delta, overshoot_abs,
            overshoot_pct, t_peak_seconds.
        """
        if self.sp.empty:
            return pd.DataFrame(columns=["start", "uuid", "is_delta", "overshoot_abs", "overshoot_pct", "t_peak_seconds"])

        actual = (
            self.dataframe[self.dataframe["uuid"] == actual_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        actual[self.time_column] = pd.to_datetime(actual[self.time_column])
        look_td = pd.to_timedelta(window)

        sp = self.sp[[self.time_column, self.value_column]].copy()
        sp["prev"] = sp[self.value_column].shift(1)
        sp["delta"] = sp[self.value_column] - sp["prev"]
        changes = sp.loc[sp["delta"].abs() > 0, [self.time_column, self.value_column, "delta"]]

        out_rows: List[Dict[str, Any]] = []
        for _, r in changes.iterrows():
            t0 = r[self.time_column]
            s_new = float(r[self.value_column])
            delta = float(r["delta"]) if pd.notna(r["delta"]) else 0.0
            win = actual[(actual[self.time_column] >= t0) & (actual[self.time_column] <= t0 + look_td)]
            if win.empty:
                out_rows.append(
                    {
                        "start": t0,
                        "uuid": self.event_uuid,
                        "is_delta": True,
                        "overshoot_abs": None,
                        "overshoot_pct": None,
                        "t_peak_seconds": None,
                    }
                )
                continue
            err = win[self.value_column] - s_new
            if delta >= 0:
                peak = err.max()
                t_peak = win.loc[err.idxmax(), self.time_column]
            else:
                peak = -err.min()  # magnitude for downward step
                t_peak = win.loc[err.idxmin(), self.time_column]
            overshoot_abs = float(peak) if pd.notna(peak) else None
            overshoot_pct = (overshoot_abs / abs(delta)) if (delta != 0 and overshoot_abs is not None) else None
            out_rows.append(
                {
                    "start": t0,
                    "uuid": self.event_uuid,
                    "is_delta": True,
                    "overshoot_abs": overshoot_abs,
                    "overshoot_pct": float(overshoot_pct) if overshoot_pct is not None else None,
                    "t_peak_seconds": (t_peak - t0).total_seconds() if pd.notna(t_peak) else None,
                }
            )

        return pd.DataFrame(out_rows)
