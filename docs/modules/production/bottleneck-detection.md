# BottleneckDetectionEvents

> Identify which station constrains a production line by analyzing utilization.

**Module:** `ts_shape.events.production.bottleneck_detection`
**Guide:** [OEE Analytics](../../guides/oee-analytics.md)

---

## When to Use

Use for multi-station line optimization. The bottleneck determines line output — finding it is the first step in improving throughput. This module compares utilization across stations and detects when the bottleneck shifts between stations over time.

---

## Quick Example

```python
from ts_shape.events.production.bottleneck_detection import BottleneckDetectionEvents
import pandas as pd
import numpy as np

np.random.seed(42)
df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=360, freq="1min"),
    "station_A": np.random.choice([True, False], size=360, p=[0.92, 0.08]),
    "station_B": np.random.choice([True, False], size=360, p=[0.98, 0.02]),
    "station_C": np.random.choice([True, False], size=360, p=[0.85, 0.15]),
})

bd = BottleneckDetectionEvents(df, timestamp_column="timestamp")
station_uuids = ["station_A", "station_B", "station_C"]
utilization = bd.station_utilization(station_uuids, window="1h")
bottleneck = bd.detect_bottleneck(station_uuids, window="1h")
shifts = bd.shifting_bottleneck(station_uuids, window="1h")
print(bottleneck)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `station_utilization(station_uuids, window='1h')` | Compute per-station uptime percentage per window | DataFrame with station, window, and utilization ratio |
| `detect_bottleneck(station_uuids, window='1h')` | Identify the bottleneck station (highest utilization) per window | DataFrame with window and bottleneck station identifier |
| `shifting_bottleneck(station_uuids, window='1h')` | Detect when the bottleneck shifts from one station to another | DataFrame of shift events with before/after station |
| `throughput_constraint_summary(station_uuids)` | Aggregate summary of how often each station is the bottleneck | DataFrame with station and percentage of time as bottleneck |

---

## Tips & Hints

!!! tip "The bottleneck has the highest utilization"
    Counter-intuitively, the station with the most uptime (not the most downtime) is usually the bottleneck — it is running flat-out trying to keep up. Stations with lower utilization are often waiting.

!!! info "Related modules"
    - [Flow Constraints](flow-constraints.md) — detects blocked/starved conditions between station pairs
    - [Machine State](machine-state.md) — provides the per-station run/idle signals
    - [Micro-Stop Detection](micro-stops.md) — uncovers hidden losses at the bottleneck station

---

## See Also

- [OEE Analytics Guide](../../guides/oee-analytics.md)
- [API Reference](../../reference/ts_shape/events/production/bottleneck_detection.md)
