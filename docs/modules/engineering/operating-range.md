# OperatingRangeEvents

> Analyze the operating envelope of a signal — what ranges it operates in and when the operating point shifts.

**Module:** `ts_shape.events.engineering.operating_range`  
**Guide:** [Process Engineering](../../guides/engineering.md)

---

## When to Use

Use for operating envelope analysis. Tracks what ranges your process actually operates in and detects regime changes that may indicate product changeovers or process shifts. Useful for building golden-run profiles and detecting off-spec operation.

---

## Quick Example

```python
from ts_shape.events.engineering.operating_range import OperatingRangeEvents

analyzer = OperatingRangeEvents(
    df=process_data,
    uuid="extruder_speed_01"
)

# Get the operating envelope per hour
envelope = analyzer.operating_envelope(window="1h")

# Detect when the operating point shifts significantly
shifts = analyzer.detect_regime_change(
    window="1h",
    shift_threshold=2.0
)

# Calculate time in a target operating range
in_range = analyzer.time_in_range(
    lower=180.0,
    upper=220.0,
    window="1h"
)

# Value distribution histogram
distribution = analyzer.value_distribution(n_bins=10)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `operating_envelope(window='1h')` | Per-window min/max/mean envelope | DataFrame with envelope stats |
| `detect_regime_change(window='1h', shift_threshold=2.0)` | Operating point shifts | DataFrame of regime changes |
| `time_in_range(lower, upper, window='1h')` | Time in target range per window | DataFrame with in-range durations |
| `value_distribution(n_bins=10)` | Value histogram | DataFrame with bin counts |

---

## Tips & Hints

!!! tip "Use time_in_range for OEE-style metrics"
    `time_in_range()` gives you the fraction of each window spent within spec. Aggregate this over a shift or day to get a process-level "in-spec percentage" that complements OEE availability and quality metrics.

!!! info "Related modules"
    - [Steady State Detection](steady-state.md) — filter to steady-state before analyzing the operating envelope
    - [Threshold Monitoring](threshold-monitoring.md) — alarm when the envelope breaches hard limits
    - [Process Windows](process-windows.md) — windowed statistics for shift-level reporting

---

## See Also

- [Process Engineering Guide](../../guides/engineering.md)
- [API Reference](../../reference/ts_shape/events/engineering/operating_range.md)
