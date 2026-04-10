# DutyCycleEvents

> Analyze on/off patterns from a boolean signal: duty cycle, intervals, transitions, excessive cycling.

**Module:** `ts_shape.events.production.duty_cycle`
**Guide:** [OEE Analytics](../../guides/oee-analytics.md)

---

## When to Use

Use for equipment utilization analysis. Tracks on/off patterns for motors, heaters, or any boolean actuator. Excessive cycling may indicate control issues or equipment degradation. Monitoring duty cycle trends over time helps predict maintenance needs before failures occur.

---

## Quick Example

```python
from ts_shape.events.production.duty_cycle import DutyCycleEvents
import pandas as pd
import numpy as np

np.random.seed(42)
# Simulate a heater cycling on and off
state = []
for _ in range(50):
    state.extend([True] * np.random.randint(20, 60))
    state.extend([False] * np.random.randint(10, 40))
df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=len(state), freq="1s"),
    "heater_on": state[:len(state)],
})

dc = DutyCycleEvents(df, state_column="heater_on")
intervals = dc.on_off_intervals()
duty = dc.duty_cycle_per_window(window="1h")
excessive = dc.excessive_cycling(max_transitions=20, window="1h")
print(duty.head())
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `on_off_intervals()` | List all on and off intervals with start, end, and duration | DataFrame of intervals with state, start, end, and duration |
| `duty_cycle_per_window(window='1h')` | Compute percentage of time the signal is ON per time window | DataFrame with window and duty_cycle ratio |
| `cycle_count(window='1h')` | Count the number of on-to-off or off-to-on transitions per window | DataFrame with window and transition count |
| `excessive_cycling(max_transitions=20, window='1h')` | Flag windows where the transition count exceeds a threshold | DataFrame of flagged windows with transition count |

---

## Tips & Hints

!!! tip "Set thresholds based on equipment specs"
    Motor contactors and relay-driven heaters have rated cycle counts. Use `excessive_cycling` with the manufacturer's limit to detect wear before failure — for example, many contactors are rated for 100,000 mechanical cycles.

!!! info "Related modules"
    - [Machine State](machine-state.md) — similar analysis but focused on production run/idle rather than equipment on/off
    - [Alarm Management](alarm-management.md) — chattering alarms are analogous to excessive cycling
    - [Micro-Stop Detection](micro-stops.md) — brief off-periods in the duty cycle may qualify as micro-stops

---

## See Also

- [OEE Analytics Guide](../../guides/oee-analytics.md)
- [API Reference](../../reference/ts_shape/events/production/duty_cycle.md)
