# FlowConstraintEvents

> Detect blocked and starved conditions between upstream/downstream stations.

**Module:** `ts_shape.events.production.flow_constraints`
**Guide:** [Production Monitoring](../../guides/production.md)

---

## When to Use

Use for multi-station line analysis. Identifies where material flow is constrained — blocked (downstream can't keep up) or starved (upstream can't supply). Understanding flow constraints is critical for line balancing and identifying the true bottleneck versus symptomatic idle time.

---

## Quick Example

```python
from ts_shape.events.production.flow_constraints import FlowConstraintEvents
import pandas as pd

df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=240, freq="30s"),
    "station_1_running": [True]*50 + [True]*40 + [False]*20 + [True]*130,
    "station_2_running": [True]*50 + [False]*40 + [False]*20 + [True]*130,
})

roles = {"upstream": "station_1_running", "downstream": "station_2_running"}
fc = FlowConstraintEvents(df, timestamp_column="timestamp")
blocked = fc.blocked_events(roles=roles, tolerance="200ms")
starved = fc.starved_events(roles=roles, tolerance="200ms")
print(blocked.head())
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `blocked_events(roles, tolerance='200ms')` | Detect intervals where upstream is running but downstream is stopped (blocked condition) | DataFrame of blocked intervals with start, end, and duration |
| `starved_events(roles, tolerance='200ms')` | Detect intervals where downstream is idle due to no upstream supply (starved condition) | DataFrame of starved intervals with start, end, and duration |
| `flow_constraint_analytics(roles)` | Comprehensive analytics combining blocked, starved, and free-flow statistics | Dict with summary metrics and interval DataFrames |

---

## Tips & Hints

!!! tip "Use tolerance to handle signal jitter"
    Set `tolerance` to account for PLC scan-time differences between stations — 200ms to 1s is typical. Without tolerance, you may get false blocked/starved detections from timing mismatches.

!!! info "Related modules"
    - [Bottleneck Detection](bottleneck-detection.md) — identifies which station constrains the line
    - [Machine State](machine-state.md) — provides the per-station run/idle signals used as input
    - [Line Throughput](line-throughput.md) — measures the throughput impact of flow constraints

---

## See Also

- [Production Monitoring Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/production/flow_constraints.md)
