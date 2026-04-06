# CycleTimeTracking

> Track cycle times by part number from part-ID and cycle-trigger signals.

**Module:** `ts_shape.events.production.cycle_time_tracking`
**Guide:** [Production Monitoring](../../guides/production.md)

---

## When to Use

Use to track individual cycle durations and identify slow cycles. Essential for performance analysis in OEE and for detecting tool wear or process drift. When cycle times gradually increase over a shift, it often indicates tool degradation or thermal effects that need attention.

---

## Quick Example

```python
from ts_shape.events.production.cycle_time_tracking import CycleTimeTracking
import pandas as pd
import numpy as np

np.random.seed(42)
cycle_times = np.random.normal(loc=55, scale=3, size=200)
cycle_times[50:55] = 90  # simulate slow cycles
df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=200, freq="1min"),
    "part_id": ["PN-100"]*100 + ["PN-200"]*100,
    "cycle_trigger": cycle_times,
})

ct = CycleTimeTracking(df, timestamp_column="timestamp")
by_part = ct.cycle_time_by_part(part_id_uuid="part_id", cycle_trigger_uuid="cycle_trigger")
stats = ct.cycle_time_statistics(part_id_uuid="part_id", cycle_trigger_uuid="cycle_trigger")
slow = ct.detect_slow_cycles(
    part_id_uuid="part_id", cycle_trigger_uuid="cycle_trigger", threshold_factor=1.5
)
print(stats)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `cycle_time_by_part(part_id_uuid, cycle_trigger_uuid)` | Compute cycle time for each part number from trigger signal intervals | DataFrame with timestamp, part_id, and cycle_time |
| `cycle_time_statistics(part_id_uuid, cycle_trigger_uuid)` | Calculate min, avg, max, and std deviation of cycle time per part number | DataFrame with part_id and statistical columns |
| `detect_slow_cycles(part_id_uuid, cycle_trigger_uuid, threshold_factor=1.5)` | Flag cycles exceeding a multiple of the average cycle time for that part | DataFrame of slow cycle events with timestamp and overshoot |
| `cycle_time_trend(part_id_uuid, cycle_trigger_uuid, part_number)` | Analyze cycle time trend for a specific part number over time | DataFrame with timestamp and rolling average cycle time |
| `hourly_cycle_time_summary(part_id_uuid, cycle_trigger_uuid)` | Summarize cycle times per hour per part for shift review dashboards | DataFrame with hour, part_id, and summary statistics |

---

## Tips & Hints

!!! tip "Use threshold_factor relative to each part"
    The `detect_slow_cycles` method computes the threshold per part number, so a 1.5x factor means 1.5 times the average for that specific SKU — no need to hard-code absolute limits for each part.

!!! info "Related modules"
    - [Line Throughput](line-throughput.md) — takt adherence from the throughput perspective
    - [Part Production Tracking](part-tracking.md) — production quantities per part
    - [OEE Calculator](oee-calculator.md) — uses cycle time for the performance component
    - [Micro-Stop Detection](micro-stops.md) — brief stops that inflate apparent cycle time

---

## See Also

- [Production Monitoring Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/production/cycle_time_tracking/)
