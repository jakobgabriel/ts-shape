# OEECalculator

> Calculate Overall Equipment Effectiveness from timeseries signals: Availability x Performance x Quality.

**Module:** `ts_shape.events.production.oee_calculator`
**Guide:** [OEE Analytics](../../guides/oee-analytics.md)

---

## When to Use

Use for daily OEE reporting. Combines availability (from machine state), performance (from part counters vs ideal cycle time), and quality (from good/reject counters) into the standard OEE metric. World-class OEE is typically 85% or above; this module helps identify which of the three factors is the biggest loss.

---

## Quick Example

```python
from ts_shape.events.production.oee_calculator import OEECalculator
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=480, freq="1min"),
    "machine_running": [True]*400 + [False]*30 + [True]*50,
    "part_counter": np.arange(1, 481),
    "reject_counter": np.cumsum(np.random.choice([0, 1], size=480, p=[0.97, 0.03])),
})

oee = OEECalculator(df, timestamp_column="timestamp")
availability = oee.calculate_availability(run_state_uuid="machine_running")
performance = oee.calculate_performance(counter_uuid="part_counter", ideal_cycle_time="55s")
quality = oee.calculate_quality(total_uuid="part_counter", reject_uuid="reject_counter")
result = oee.calculate_oee(
    run_state_uuid="machine_running",
    counter_uuid="part_counter",
    ideal_cycle_time="55s",
)
print(f"OEE: {result['oee']:.1%}")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `calculate_availability(run_state_uuid)` | Compute availability ratio from run/idle state signal | Float between 0.0 and 1.0 |
| `calculate_performance(counter_uuid, ideal_cycle_time)` | Compute performance ratio: actual output vs theoretical maximum at ideal cycle time | Float between 0.0 and 1.0 |
| `calculate_quality(total_uuid, reject_uuid)` | Compute quality ratio: good parts divided by total parts produced | Float between 0.0 and 1.0 |
| `calculate_oee(run_state_uuid, counter_uuid, ideal_cycle_time)` | Compute full OEE as Availability x Performance x Quality with daily breakdown | Dict with oee, availability, performance, quality, and daily DataFrame |

---

## Tips & Notes

!!! tip "Validate each factor independently"
    Always check availability, performance, and quality separately before looking at the combined OEE number. A single factor can mask improvement in the others.

!!! info "Related modules"
    - [Machine State](machine-state.md) — provides the run/idle signal for availability
    - [Line Throughput](line-throughput.md) — provides part counts for performance
    - [Quality Tracking](quality-tracking.md) — provides OK/NOK counts for quality
    - [Micro-Stop Detection](micro-stops.md) — uncovers hidden availability losses

---

## See Also

- [OEE Analytics Guide](../../guides/oee-analytics.md)
- [API Reference](../../reference/ts_shape/events/production/oee_calculator/)
