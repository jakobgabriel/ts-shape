# DegradationDetectionEvents

> Detect degradation patterns in time series signals: trend degradation, variance increases, level shifts, and composite health scores.

**Module:** `ts_shape.events.maintenance.degradation_detection`
**Guide:** [Quality Guide](../../guides/quality.md)

---

## When to Use

Use for predictive maintenance monitoring. Tracks gradual degradation in bearing temperature, motor current, or any signal that slowly drifts before failure. Ideal when you need early warning of equipment deterioration before alarm thresholds are reached.

---

## Quick Example

```python
from ts_shape.events.maintenance.degradation_detection import DegradationDetectionEvents

detector = DegradationDetectionEvents(
    df=sensor_df,
    timestamp_col="timestamp",
    value_col="bearing_temp"
)

# Detect slow upward drift in bearing temperature
trend_events = detector.detect_trend_degradation(window="7D", slope_threshold=0.05)

# Check variance increase against a known-good baseline
variance_events = detector.detect_variance_increase(baseline_window="30D", threshold=2.0)

# Composite health score combining all indicators
score = detector.health_score(
    trend_weight=0.4, variance_weight=0.3, shift_weight=0.3
)
print(f"Health score: {score}/100")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `detect_trend_degradation()` | Rolling linear regression slope detection | DataFrame of intervals with degrading trend |
| `detect_variance_increase()` | Variance vs baseline comparison | DataFrame of intervals with elevated variance |
| `detect_level_shift()` | CUSUM-like mean shift detection | DataFrame of detected level shift events |
| `health_score()` | Composite 0-100 health score | Float score combining trend, variance, and shift indicators |

---

## Tips & Notes

!!! tip "Set a meaningful baseline window"
    Use the first stable operating period as your baseline. A poorly chosen baseline will produce false positives from `detect_variance_increase()` and `detect_level_shift()`.

!!! info "Related modules"
    - [`FailurePredictionEvents`](failure-prediction.md) - Estimate remaining useful life once degradation is confirmed
    - [`VibrationAnalysisEvents`](vibration-analysis.md) - Specialized degradation detection for vibration signals

---

## See Also

- [Quality Guide](../../guides/quality.md)
- [API Reference](../../reference/ts_shape/events/maintenance/degradation_detection/)
