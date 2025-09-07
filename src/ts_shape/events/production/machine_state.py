import pandas as pd  # type: ignore
from typing import List, Dict, Any

from ts_shape.utils.base import Base


class MachineStateEvents(Base):
    """Production: Machine State

    Detect run/idle transitions and intervals from a boolean state signal.

    Classes:
    - MachineStateEvents: Run/idle state intervals and transitions.
      - detect_run_idle: Intervalize run/idle states with optional min duration filter.
      - transition_events: Point events on state changes (idle->run, run->idle).
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        run_state_uuid: str,
        *,
        event_uuid: str = "prod:run_idle",
        value_column: str = "value_bool",
        time_column: str = "systime",
    ) -> None:
        super().__init__(dataframe, column_name=time_column)
        self.run_state_uuid = run_state_uuid
        self.event_uuid = event_uuid
        self.value_column = value_column
        self.time_column = time_column
        self.series = (
            self.dataframe[self.dataframe["uuid"] == self.run_state_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        self.series[self.time_column] = pd.to_datetime(self.series[self.time_column])

    def detect_run_idle(self, min_duration: str = "0s") -> pd.DataFrame:
        """Return intervals labeled as 'run' or 'idle'.

        - min_duration: discard intervals shorter than this duration.
        Columns: start, end, uuid, source_uuid, is_delta, state
        """
        if self.series.empty:
            return pd.DataFrame(
                columns=["start", "end", "uuid", "source_uuid", "is_delta", "state"]
            )
        s = self.series[[self.time_column, self.value_column]].copy()
        s["state"] = s[self.value_column].fillna(False).astype(bool)
        state_change = (s["state"] != s["state"].shift()).cumsum()
        min_td = pd.to_timedelta(min_duration)
        rows: List[Dict[str, Any]] = []
        for _, seg in s.groupby(state_change):
            state = bool(seg["state"].iloc[0])
            start = seg[self.time_column].iloc[0]
            end = seg[self.time_column].iloc[-1]
            if (end - start) < min_td:
                continue
            rows.append(
                {
                    "start": start,
                    "end": end,
                    "uuid": self.event_uuid,
                    "source_uuid": self.run_state_uuid,
                    "is_delta": True,
                    "state": "run" if state else "idle",
                }
            )
        return pd.DataFrame(rows)

    def transition_events(self) -> pd.DataFrame:
        """Return point events at state transitions.

        Columns: systime, uuid, source_uuid, is_delta, transition ('idle_to_run'|'run_to_idle')
        """
        if self.series.empty:
            return pd.DataFrame(
                columns=["systime", "uuid", "source_uuid", "is_delta", "transition"]
            )
        s = self.series[[self.time_column, self.value_column]].copy()
        s["state"] = s[self.value_column].fillna(False).astype(bool)
        s["prev"] = s["state"].shift()
        changes = s[s["state"] != s["prev"]].dropna(subset=["prev"])  # ignore first row
        if changes.empty:
            return pd.DataFrame(
                columns=["systime", "uuid", "source_uuid", "is_delta", "transition"]
            )
        changes = changes.rename(columns={self.time_column: "systime"})
        changes["transition"] = changes.apply(
            lambda r: "idle_to_run" if (r["prev"] is False and r["state"] is True) else "run_to_idle",
            axis=1,
        )
        return pd.DataFrame(
            {
                "systime": changes["systime"],
                "uuid": self.event_uuid,
                "source_uuid": self.run_state_uuid,
                "is_delta": True,
                "transition": changes["transition"],
            }
        )

