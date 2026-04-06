# StartupDetectionEvents

> Detect equipment startup intervals based on threshold crossings or sustained positive slope.

**Module:** `ts_shape.events.engineering.startup_events`  
**Guide:** [Process Engineering](../../guides/engineering.md)

---

## When to Use

Use to detect and characterize equipment startup events for motors, ovens, pumps, and similar assets. Supports multiple detection strategies including threshold-based, slope-based, and adaptive approaches. Also provides startup quality assessment and failed startup detection.

---

## Quick Example

```python
from ts_shape.events.engineering.startup_events import StartupDetectionEvents

detector = StartupDetectionEvents(
    df=motor_data,
    uuid="motor_current_01"
)

# Detect startups when current crosses 5A with hysteresis
startups = detector.detect_startup_by_threshold(
    threshold=5.0,
    hysteresis=0.5
)

# Assess quality of detected startups
quality = detector.assess_startup_quality(startup_events=startups)

# Detect startups that failed to reach operating conditions
failed = detector.detect_failed_startups(
    threshold=5.0,
    min_rise_duration="5s"
)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `detect_startup_by_threshold(threshold, hysteresis=None)` | Threshold-based startup detection | DataFrame of startup intervals |
| `detect_startup_by_slope(min_slope, slope_window='0s')` | Slope-based startup detection | DataFrame of startup intervals |
| `detect_startup_multi_signal(signals, logic='all')` | Multi-signal startup detection | DataFrame of startup intervals |
| `detect_startup_adaptive(baseline_window='1h', sensitivity=2.0)` | Adaptive baseline startup detection | DataFrame of startup intervals |
| `assess_startup_quality(startup_events)` | Quality assessment of startups | DataFrame with quality metrics |
| `track_startup_phases(phases)` | Phase tracking within startups | DataFrame with phase breakdowns |
| `detect_failed_startups(threshold, min_rise_duration='5s')` | Detect failed startup attempts | DataFrame of failed startups |

---

## Tips & Hints

!!! tip "Use adaptive detection for varying baselines"
    When the idle-state baseline drifts over time (e.g., ambient temperature changes), use `detect_startup_adaptive()` instead of a fixed threshold. It recalculates the baseline from a rolling window and adapts automatically.

!!! info "Related modules"
    - [Warm-Up Analysis](warmup-analysis.md) — characterize the thermal ramp following startup
    - [Rate of Change](rate-of-change.md) — detect the initial ramp rate during startup
    - [Threshold Monitoring](threshold-monitoring.md) — monitor operating limits after startup

---

## See Also

- [Process Engineering Guide](../../guides/engineering.md)
- [API Reference](../../reference/ts_shape/events/engineering/startup_events/)
