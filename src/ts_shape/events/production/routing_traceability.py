"""Routing-based traceability using ID + handover signals.

In this pattern a single UUID carries the current item identifier (order number,
serial code, etc.) and a separate UUID carries a routing / handover integer
signal whose value indicates which station the item is being sent to.

Example: serial code "abc" is active while the handover signal reads 1 → the
item went to station 1.  Later the handover signal changes to 2 → the item
is now at station 2.

This module correlates both signals to reconstruct the full routing path.
"""

import pandas as pd  # type: ignore
import numpy as np
from typing import List, Dict, Any, Optional

from ts_shape.utils.base import Base


class RoutingTraceabilityEvents(Base):
    """Trace item routing using an ID signal paired with a handover signal.

    Two UUIDs work together:
    - **id_uuid**: string signal carrying the current order / serial number.
    - **routing_uuid**: integer/numeric signal whose value encodes the
      destination station (e.g., 1 = Station 1, 2 = Station 2).

    An optional ``station_map`` translates numeric values to human-readable
    station names.

    Example usage:
        trace = RoutingTraceabilityEvents(
            df,
            id_uuid='serial_code_signal',
            routing_uuid='handover_signal',
            station_map={1: 'Welding', 2: 'Painting', 3: 'Assembly'},
        )

        # Full routing timeline
        timeline = trace.build_routing_timeline()

        # Lead time per item
        lead = trace.lead_time()

        # Station visit statistics
        stats = trace.station_statistics()

        # Routing path frequency (which paths are most common)
        paths = trace.routing_paths()
    """

    def __init__(
        self,
        dataframe: pd.DataFrame,
        id_uuid: str,
        routing_uuid: str,
        *,
        station_map: Optional[Dict[int, str]] = None,
        event_uuid: str = "prod:routing_trace",
        id_value_column: str = "value_string",
        routing_value_column: str = "value_integer",
        time_column: str = "systime",
    ) -> None:
        """Initialize routing traceability.

        Args:
            dataframe: Input DataFrame with timeseries data.
            id_uuid: UUID of the signal carrying order/serial IDs.
            routing_uuid: UUID of the handover/routing signal (integer values).
            station_map: Optional mapping from routing integer to station name.
                         e.g. {1: 'Welding', 2: 'Painting', 3: 'Assembly'}
            event_uuid: UUID to tag derived events with.
            id_value_column: Column holding the order/serial ID string.
            routing_value_column: Column holding the routing integer value.
            time_column: Name of timestamp column.
        """
        super().__init__(dataframe, column_name=time_column)
        self.id_uuid = id_uuid
        self.routing_uuid = routing_uuid
        self.station_map = station_map or {}
        self.event_uuid = event_uuid
        self.id_value_column = id_value_column
        self.routing_value_column = routing_value_column
        self.time_column = time_column

        # Pre-filter signals
        self.id_data = (
            self.dataframe[self.dataframe["uuid"] == self.id_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        self.id_data[self.time_column] = pd.to_datetime(self.id_data[self.time_column])

        self.routing_data = (
            self.dataframe[self.dataframe["uuid"] == self.routing_uuid]
            .copy()
            .sort_values(self.time_column)
        )
        self.routing_data[self.time_column] = pd.to_datetime(
            self.routing_data[self.time_column]
        )

    def _station_name(self, value: Any) -> str:
        """Resolve a routing value to a station name."""
        try:
            v = int(value)
        except (ValueError, TypeError):
            v = value
        if v in self.station_map:
            return self.station_map[v]
        return f"Station {v}"

    # ------------------------------------------------------------------
    # build_routing_timeline
    # ------------------------------------------------------------------

    def build_routing_timeline(self) -> pd.DataFrame:
        """Correlate the ID signal with the routing signal to build a timeline.

        For each sample of the routing signal, the *current* item ID is
        determined via backward-fill merge (most recent ID at that timestamp).
        Contiguous intervals where the same (item_id, station) pair holds
        are grouped into single events.

        Returns:
            DataFrame with columns:
            - item_id: Order / serial number string.
            - routing_value: Raw routing signal value.
            - station_name: Human-readable station name.
            - start: First timestamp of interval.
            - end: Last timestamp of interval.
            - duration_seconds: Time at the station.
            - sample_count: Number of routing samples in interval.
            - station_sequence: Visit order per item (1-based).
            - uuid: Event UUID.
        """
        if self.routing_data.empty or self.id_data.empty:
            return pd.DataFrame(
                columns=[
                    "item_id", "routing_value", "station_name",
                    "start", "end", "duration_seconds", "sample_count",
                    "station_sequence", "uuid",
                ]
            )

        # Merge: for each routing sample, attach the most-recent item ID
        routing_subset = self.routing_data[
            [self.time_column, self.routing_value_column]
        ].copy()
        id_subset = self.id_data[
            [self.time_column, self.id_value_column]
        ].copy()

        merged = pd.merge_asof(
            routing_subset,
            id_subset,
            on=self.time_column,
            direction="backward",
        )

        merged = merged.rename(columns={
            self.id_value_column: "item_id",
            self.routing_value_column: "routing_value",
        })
        merged = merged.dropna(subset=["item_id"])
        merged["item_id"] = merged["item_id"].astype(str)

        if merged.empty:
            return pd.DataFrame(
                columns=[
                    "item_id", "routing_value", "station_name",
                    "start", "end", "duration_seconds", "sample_count",
                    "station_sequence", "uuid",
                ]
            )

        # Detect contiguous intervals of (item_id, routing_value)
        merged["combo"] = merged["item_id"] + "|" + merged["routing_value"].astype(str)
        merged["group"] = (merged["combo"] != merged["combo"].shift()).cumsum()

        rows: List[Dict[str, Any]] = []
        for _, seg in merged.groupby("group"):
            item_id = seg["item_id"].iloc[0]
            routing_val = seg["routing_value"].iloc[0]
            start = seg[self.time_column].iloc[0]
            end = seg[self.time_column].iloc[-1]
            rows.append({
                "item_id": item_id,
                "routing_value": routing_val,
                "station_name": self._station_name(routing_val),
                "start": start,
                "end": end,
                "duration_seconds": (end - start).total_seconds(),
                "sample_count": len(seg),
            })

        timeline = pd.DataFrame(rows)
        timeline = timeline.sort_values(["item_id", "start"]).reset_index(drop=True)
        timeline["station_sequence"] = timeline.groupby("item_id").cumcount() + 1
        timeline["uuid"] = self.event_uuid

        return timeline

    # ------------------------------------------------------------------
    # lead_time
    # ------------------------------------------------------------------

    def lead_time(self) -> pd.DataFrame:
        """Compute end-to-end lead time per item.

        Returns:
            DataFrame with columns:
            - item_id
            - first_station: Name of first station visited.
            - last_station: Name of last station visited.
            - first_seen: Earliest timestamp.
            - last_seen: Latest timestamp.
            - lead_time_seconds: Total elapsed time.
            - stations_visited: Number of distinct stations.
            - routing_path: Ordered station names joined by " -> ".
            - uuid: Event UUID.
        """
        timeline = self.build_routing_timeline()

        if timeline.empty:
            return pd.DataFrame(
                columns=[
                    "item_id", "first_station", "last_station",
                    "first_seen", "last_seen", "lead_time_seconds",
                    "stations_visited", "routing_path", "uuid",
                ]
            )

        rows: List[Dict[str, Any]] = []
        for item_id, grp in timeline.groupby("item_id"):
            grp = grp.sort_values("start")
            first_seen = grp["start"].iloc[0]
            last_seen = grp["end"].iloc[-1]
            routing_path = " -> ".join(grp["station_name"].tolist())
            rows.append({
                "item_id": item_id,
                "first_station": grp["station_name"].iloc[0],
                "last_station": grp["station_name"].iloc[-1],
                "first_seen": first_seen,
                "last_seen": last_seen,
                "lead_time_seconds": (last_seen - first_seen).total_seconds(),
                "stations_visited": grp["station_name"].nunique(),
                "routing_path": routing_path,
                "uuid": self.event_uuid,
            })

        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # station_statistics
    # ------------------------------------------------------------------

    def station_statistics(self) -> pd.DataFrame:
        """Compute dwell-time statistics per station across all items.

        Returns:
            DataFrame with columns:
            - station_name
            - routing_value
            - item_count: Number of distinct items seen.
            - min_dwell_seconds
            - avg_dwell_seconds
            - max_dwell_seconds
            - total_dwell_seconds
        """
        timeline = self.build_routing_timeline()

        if timeline.empty:
            return pd.DataFrame(
                columns=[
                    "station_name", "routing_value", "item_count",
                    "min_dwell_seconds", "avg_dwell_seconds",
                    "max_dwell_seconds", "total_dwell_seconds",
                ]
            )

        stats = timeline.groupby(["station_name", "routing_value"]).agg(
            item_count=("item_id", "nunique"),
            min_dwell_seconds=("duration_seconds", "min"),
            avg_dwell_seconds=("duration_seconds", "mean"),
            max_dwell_seconds=("duration_seconds", "max"),
            total_dwell_seconds=("duration_seconds", "sum"),
        ).reset_index()

        for col in ["min_dwell_seconds", "avg_dwell_seconds",
                     "max_dwell_seconds", "total_dwell_seconds"]:
            stats[col] = stats[col].round(2)

        return stats

    # ------------------------------------------------------------------
    # routing_paths
    # ------------------------------------------------------------------

    def routing_paths(self) -> pd.DataFrame:
        """Analyze routing path frequencies -- which station sequences are most common.

        Returns:
            DataFrame with columns:
            - routing_path: Ordered station names joined by " -> ".
            - item_count: Number of items that followed this path.
            - avg_lead_time_seconds: Average lead time for items on this path.
            - min_lead_time_seconds
            - max_lead_time_seconds
        """
        lead = self.lead_time()

        if lead.empty:
            return pd.DataFrame(
                columns=[
                    "routing_path", "item_count",
                    "avg_lead_time_seconds",
                    "min_lead_time_seconds",
                    "max_lead_time_seconds",
                ]
            )

        stats = lead.groupby("routing_path").agg(
            item_count=("item_id", "nunique"),
            avg_lead_time_seconds=("lead_time_seconds", "mean"),
            min_lead_time_seconds=("lead_time_seconds", "min"),
            max_lead_time_seconds=("lead_time_seconds", "max"),
        ).reset_index()

        for col in ["avg_lead_time_seconds", "min_lead_time_seconds",
                     "max_lead_time_seconds"]:
            stats[col] = stats[col].round(2)

        return stats.sort_values("item_count", ascending=False).reset_index(drop=True)
