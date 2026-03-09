# MicroStopEvents

> Detect brief idle intervals that individually seem harmless but accumulate into significant availability losses.

**Module:** `ts_shape.events.production.micro_stop_detection`
**Guide:** [OEE Analytics](../../guides/oee-analytics.md)

---

## When to Use

Use to uncover hidden availability losses. Micro-stops (under 30s) are often invisible in standard reports but can add up to significant lost time. Common causes include sensor misfeeds, part jams, and minor alignment issues that operators clear without logging a downtime event.

---

## Quick Example

```python
from ts_shape.events.production.micro_stop_detection import MicroStopEvents
import pandas as pd
import numpy as np

np.random.seed(42)
# Simulate a machine with frequent brief stops
running = []
for _ in range(100):
    running.extend([True] * np.random.randint(10, 30))
    running.extend([False] * np.random.randint(1, 4))  # 1-3 second stops
df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=len(running), freq="1s"),
    "machine_running": running[:len(running)],
})

ms = MicroStopEvents(df, state_column="machine_running")
stops = ms.detect_micro_stops(max_duration="30s")
frequency = ms.micro_stop_frequency(window="1h")
impact = ms.micro_stop_impact(window="1h")
print(f"Found {len(stops)} micro-stops")
print(impact.head())
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `detect_micro_stops(max_duration='30s')` | Find all idle intervals shorter than the specified threshold | DataFrame of micro-stop intervals with start, end, and duration |
| `micro_stop_frequency(window='1h')` | Count micro-stops per time window to identify problem periods | DataFrame with window and micro-stop count |
| `micro_stop_impact(window='1h')` | Calculate cumulative time lost to micro-stops vs total available time per window | DataFrame with window, lost_time, available_time, and loss_ratio |
| `micro_stop_patterns(hour_grouping=True)` | Cluster micro-stops by time of day or shift to find recurring patterns | DataFrame with grouping key and pattern statistics |

---

## Tips & Notes

!!! tip "Adjust max_duration to your process"
    The 30-second default works for high-speed discrete manufacturing. For slower processes (e.g., assembly), consider increasing to 60-120 seconds. The key is to capture stops below your standard downtime reporting threshold.

!!! info "Related modules"
    - [Machine State](machine-state.md) — provides the run/idle signal that micro-stop detection analyzes
    - [OEE Calculator](oee-calculator.md) — micro-stops appear as availability losses in OEE
    - [Duty Cycle](duty-cycle.md) — excessive cycling patterns may correlate with micro-stop clusters

---

## See Also

- [OEE Analytics Guide](../../guides/oee-analytics.md)
- [API Reference](../../reference/ts_shape/events/production/micro_stop_detection/)
