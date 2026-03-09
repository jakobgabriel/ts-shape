# MachineStateEvents

> Detect run/idle transitions and intervals from a boolean state signal.

**Module:** `ts_shape.events.production.machine_state`
**Guide:** [Production Monitoring](../../guides/production.md)

---

## When to Use

Use as the foundational production module — machine state drives downtime, OEE, and throughput analysis. Requires a boolean run/idle signal from the PLC. Every production analytics workflow typically starts with machine state detection before layering on throughput, quality, or downtime analysis.

---

## Quick Example

```python
from ts_shape.events.production.machine_state import MachineStateEvents
import pandas as pd

df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=120, freq="30s"),
    "machine_running": [True]*20 + [False]*5 + [True]*40 + [False]*10 + [True]*45,
})

events = MachineStateEvents(df, state_column="machine_running")
intervals = events.detect_run_idle(min_duration="0s")
transitions = events.transition_events()
print(intervals.head())
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `detect_run_idle(min_duration='0s')` | Identify contiguous run and idle intervals, optionally filtering by minimum duration | DataFrame of intervals with start, end, duration, and state |
| `transition_events()` | Generate point events at each run-to-idle or idle-to-run transition | DataFrame of transition timestamps and direction |
| `detect_rapid_transitions(threshold='5s', min_count=3)` | Flag suspicious rapid state changes that may indicate sensor noise or PLC faults | DataFrame of rapid-transition windows |
| `state_quality_metrics()` | Compute data quality metrics such as gap count, coverage, and signal stability | Dict of quality metric values |

---

## Tips & Notes

!!! tip "Filter short idle gaps"
    Use `min_duration` in `detect_run_idle()` to ignore brief sensor glitches — a 2-5 second threshold works well for most PLCs.

!!! info "Related modules"
    - [Downtime Tracking](downtime.md) — categorizes idle intervals by reason code
    - [Micro-Stop Detection](micro-stops.md) — finds brief idles that accumulate into losses
    - [OEE Calculator](oee-calculator.md) — uses machine state for the availability component

---

## See Also

- [Production Monitoring Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/production/machine_state/)
