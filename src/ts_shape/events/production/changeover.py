import pandas as pd  # type: ignore
from typing import List, Dict, Any, Optional

from ts_shape.utils.base import Base


class ChangeoverEvents(Base):
    """Production: Changeover

    Detect product/recipe changes and compute changeover windows without
    requiring a dedicated 'first good' signal.

    Methods:
    - detect_changeover: point events when product/recipe changes.
    - changeover_window: derive an end time via fixed window or 'stable_band' metrics.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        *,
        event_uuid: str = "prod:changeover",
        time_column: str = "systime",
    ) -> None:
        super().__init__(dataframe, column_name=time_column)
        self.event_uuid = event_uuid
        self.time_column = time_column

    def detect_changeover(
        self,
        product_uuid: str,
        *,
        value_column: str = "value_string",
        min_hold: str = "0s",
    ) -> pd.DataFrame:
        """Emit point events when the product/recipe changes value.

        Uses a hold check: the new product must persist for at least min_hold
        until the next change.
        """
        p = (
            self.dataframe[self.dataframe["uuid"] == product_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        if p.empty:
            return pd.DataFrame(
                columns=["systime", "uuid", "source_uuid", "is_delta", "new_value"]
            )
        p[self.time_column] = pd.to_datetime(p[self.time_column])
        series = p[value_column]
        changed = series.ne(series.shift())
        change_times = p.loc[changed, self.time_column]
        min_td = pd.to_timedelta(min_hold)
        next_change = change_times.shift(-1)
        ok = (next_change - change_times >= min_td) | next_change.isna()
        change_times = change_times[ok]
        out = p[p[self.time_column].isin(change_times)][
            [self.time_column, value_column]
        ].rename(columns={self.time_column: "systime", value_column: "new_value"})
        out["uuid"] = self.event_uuid
        out["source_uuid"] = product_uuid
        out["is_delta"] = True
        return out[["systime", "uuid", "source_uuid", "is_delta", "new_value"]]

    def changeover_window(
        self,
        product_uuid: str,
        *,
        value_column: str = "value_string",
        start_time: Optional[pd.Timestamp] = None,
        until: str = "fixed_window",
        config: Optional[Dict[str, Any]] = None,
        fallback: Optional[Dict[str, Any]] = None,
    ) -> pd.DataFrame:
        """Compute changeover windows per product change.

        until:
          - fixed_window: end = start + config['duration'] (e.g., '10m')
          - stable_band: end when all metrics stabilize within band for hold:
                config = {
                  'metrics': [
                    {'uuid': 'm1', 'value_column': 'value_double', 'band': 0.2, 'hold': '2m'},
                    ...
                  ]
                }
        fallback: {'default_duration': '10m', 'completed': False}
        """
        config = config or {}
        fallback = fallback or {"default_duration": "10m", "completed": False}

        changes = self.detect_changeover(product_uuid, value_column=value_column, min_hold=config.get("min_hold", "0s"))
        if start_time is not None:
            changes = changes[changes["systime"] >= pd.to_datetime(start_time)]
        if changes.empty:
            return pd.DataFrame(
                columns=["start", "end", "uuid", "source_uuid", "is_delta", "method", "completed"]
            )

        rows: List[Dict[str, Any]] = []
        for _, r in changes.iterrows():
            t0 = pd.to_datetime(r["systime"])
            if until == "fixed_window":
                duration = pd.to_timedelta(config.get("duration", "10m"))
                end = t0 + duration
                rows.append(
                    {
                        "start": t0,
                        "end": end,
                        "uuid": self.event_uuid,
                        "source_uuid": product_uuid,
                        "is_delta": True,
                        "method": "fixed_window",
                        "completed": True,
                    }
                )
                continue

            if until == "stable_band":
                metric_defs = config.get("metrics", [])
                metric_ends: List[pd.Timestamp] = []
                for mdef in metric_defs:
                    uid = mdef["uuid"]
                    vcol = mdef.get("value_column", "value_double")
                    band = float(mdef.get("band", 0.0))
                    hold_td = pd.to_timedelta(mdef.get("hold", "0s"))
                    s = (
                        self.dataframe[self.dataframe["uuid"] == uid]
                        .copy()
                        .sort_values(self.time_column)
                    )
                    s[self.time_column] = pd.to_datetime(s[self.time_column])
                    s = s[s[self.time_column] >= t0]
                    if s.empty:
                        continue
                    # Rolling median reference and band mask
                    # Use expanding median to be robust soon after change
                    ref = s[vcol].expanding(min_periods=3).median()
                    inside = (s[vcol] - ref).abs() <= band
                    if not inside.any():
                        continue
                    gid = (inside.ne(inside.shift())).cumsum()
                    end_found: Optional[pd.Timestamp] = None
                    for _, seg in s.groupby(gid):
                        seg_inside = inside.loc[seg.index]
                        if not seg_inside.iloc[0]:
                            continue
                        start_seg = seg[self.time_column].iloc[0]
                        end_seg = seg[self.time_column].iloc[-1]
                        if (end_seg - start_seg) >= hold_td:
                            end_found = start_seg
                            break
                    if end_found is not None:
                        metric_ends.append(end_found)
                if metric_defs and len(metric_ends) == len(metric_defs):
                    end = max(metric_ends)
                    rows.append(
                        {
                            "start": t0,
                            "end": end,
                            "uuid": self.event_uuid,
                            "source_uuid": product_uuid,
                            "is_delta": True,
                            "method": "stable_band",
                            "completed": True,
                        }
                    )
                    continue

            # fallback
            end = t0 + pd.to_timedelta(fallback.get("default_duration", "10m"))
            rows.append(
                {
                    "start": t0,
                    "end": end,
                    "uuid": self.event_uuid,
                    "source_uuid": product_uuid,
                    "is_delta": True,
                    "method": until,
                    "completed": bool(fallback.get("completed", False)),
                }
            )

        return pd.DataFrame(rows)

