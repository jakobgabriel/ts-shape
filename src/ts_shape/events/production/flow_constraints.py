import pandas as pd  # type: ignore
from typing import Dict, Any, List

from ts_shape.utils.base import Base


class FlowConstraintEvents(Base):
    """Production: Flow Constraints

    - blocked_events: upstream running while downstream not consuming.
    - starved_events: downstream idle due to lack of upstream supply.
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        *,
        time_column: str = "systime",
        event_uuid: str = "prod:flow",
    ) -> None:
        super().__init__(dataframe, column_name=time_column)
        self.time_column = time_column
        self.event_uuid = event_uuid

    def _align_bool(self, uuid: str) -> pd.DataFrame:
        s = (
            self.dataframe[self.dataframe["uuid"] == uuid]
            .copy()
            .sort_values(self.time_column)
        )
        s[self.time_column] = pd.to_datetime(s[self.time_column])
        s["state"] = s["value_bool"].fillna(False).astype(bool)
        return s[[self.time_column, "state"]]

    def blocked_events(
        self,
        *,
        roles: Dict[str, str],
        tolerance: str = "200ms",
        min_duration: str = "0s",
    ) -> pd.DataFrame:
        """Blocked: upstream_run=True while downstream_run=False.

        roles = {'upstream_run': uuid, 'downstream_run': uuid}
        """
        up = self._align_bool(roles["upstream_run"])  # time, state
        dn = self._align_bool(roles["downstream_run"])  # time, state
        if up.empty or dn.empty:
            return pd.DataFrame(
                columns=["start", "end", "uuid", "source_uuid", "is_delta", "type"]
            )
        tol = pd.to_timedelta(tolerance)
        merged = pd.merge_asof(up, dn, on=self.time_column, suffixes=("_up", "_dn"), tolerance=tol, direction="nearest")
        cond = merged["state_up"] & (~merged["state_dn"].fillna(False))
        gid = (cond.ne(cond.shift())).cumsum()
        min_td = pd.to_timedelta(min_duration)
        rows: List[Dict[str, Any]] = []
        for _, seg in merged.groupby(gid):
            m = cond.loc[seg.index]
            if not m.any():
                continue
            start = seg[self.time_column].iloc[0]
            end = seg[self.time_column].iloc[-1]
            if (end - start) < min_td:
                continue
            rows.append(
                {
                    "start": start,
                    "end": end,
                    "uuid": self.event_uuid,
                    "source_uuid": roles["upstream_run"],
                    "is_delta": True,
                    "type": "blocked",
                }
            )
        return pd.DataFrame(rows)

    def starved_events(
        self,
        *,
        roles: Dict[str, str],
        tolerance: str = "200ms",
        min_duration: str = "0s",
    ) -> pd.DataFrame:
        """Starved: downstream_run=True while upstream_run=False.

        roles = {'upstream_run': uuid, 'downstream_run': uuid}
        """
        up = self._align_bool(roles["upstream_run"])  # time, state
        dn = self._align_bool(roles["downstream_run"])  # time, state
        if up.empty or dn.empty:
            return pd.DataFrame(
                columns=["start", "end", "uuid", "source_uuid", "is_delta", "type"]
            )
        tol = pd.to_timedelta(tolerance)
        merged = pd.merge_asof(dn, up, on=self.time_column, suffixes=("_dn", "_up"), tolerance=tol, direction="nearest")
        cond = merged["state_dn"] & (~merged["state_up"].fillna(False))
        gid = (cond.ne(cond.shift())).cumsum()
        min_td = pd.to_timedelta(min_duration)
        rows: List[Dict[str, Any]] = []
        for _, seg in merged.groupby(gid):
            m = cond.loc[seg.index]
            if not m.any():
                continue
            start = seg[self.time_column].iloc[0]
            end = seg[self.time_column].iloc[-1]
            if (end - start) < min_td:
                continue
            rows.append(
                {
                    "start": start,
                    "end": end,
                    "uuid": self.event_uuid,
                    "source_uuid": roles["downstream_run"],
                    "is_delta": True,
                    "type": "starved",
                }
            )
        return pd.DataFrame(rows)

