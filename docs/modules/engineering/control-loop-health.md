# ControlLoopHealthEvents

> Continuously assess PID/control loop health from setpoint + actual pairs.

**Module:** `ts_shape.events.engineering.control_loop_health`  
**Guide:** [Process Engineering](../../guides/engineering.md)

---

## When to Use

Use for ongoing PID loop health monitoring. Detects oscillation, valve saturation, and degrading control performance. Complements setpoint events by monitoring between setpoint changes — while setpoint events evaluate transitions, this module evaluates steady-state control quality.

---

## Quick Example

```python
from ts_shape.events.engineering.control_loop_health import ControlLoopHealthEvents

monitor = ControlLoopHealthEvents(
    df=loop_data,
    uuid="setpoint_flow_01"
)

# Compute error integrals (IAE, ISE, ITAE) per hour
integrals = monitor.error_integrals(window="1h")

# Detect oscillation in the control error
oscillations = monitor.detect_oscillation(
    window="5min",
    min_crossings=4
)

# Check for valve saturation
saturation = monitor.output_saturation(
    high_limit=100.0,
    low_limit=0.0,
    window="1h"
)

# Generate an 8-hour shift-level report card
report = monitor.loop_health_summary(window="8h")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `error_integrals(window='1h')` | IAE/ISE/ITAE per window | DataFrame with integral metrics |
| `detect_oscillation(window='5min', min_crossings=4)` | Error oscillation detection | DataFrame of oscillation events |
| `output_saturation(high_limit=100.0, low_limit=0.0, window='1h')` | Valve/output saturation | DataFrame with saturation stats |
| `loop_health_summary(window='8h')` | Shift-level report card | DataFrame with health grades |

---

## Tips & Hints

!!! tip "Use IAE trends for early tuning degradation"
    A rising IAE trend across shifts — even when all values are within spec — signals that the loop is slowly losing control authority. Catch this early with `error_integrals()` before operators notice sluggish response or oscillation.

!!! info "Related modules"
    - [Setpoint Events](setpoint-events.md) — evaluate control performance during setpoint transitions
    - [Signal Comparison](signal-comparison.md) — detect divergence between setpoint and actual
    - [Disturbance Recovery](disturbance-recovery.md) — measure recovery after external upsets

---

## See Also

- [Process Engineering Guide](../../guides/engineering.md)
- [API Reference](../../reference/ts_shape/events/engineering/control_loop_health/)
