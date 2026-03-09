# FailurePredictionEvents

> Predict remaining useful life and detect escalating failure patterns.

**Module:** `ts_shape.events.maintenance.failure_prediction`
**Guide:** [Quality Guide](../../guides/quality.md)

---

## When to Use

Use when a degradation trend has been identified and you need to estimate how much time remains before a failure threshold is reached. Pairs well with `DegradationDetectionEvents` for a complete predictive maintenance pipeline.

---

## Quick Example

```python
from ts_shape.events.maintenance.failure_prediction import FailurePredictionEvents

predictor = FailurePredictionEvents(
    df=sensor_df,
    timestamp_col="timestamp",
    value_col="bearing_temp"
)

# Estimate remaining useful life via linear extrapolation
rul = predictor.remaining_useful_life(threshold=95.0, window="7D")
print(f"Estimated RUL: {rul.days:.1f} days")

# Detect escalating threshold breaches
exceedances = predictor.detect_exceedance_pattern(
    threshold=80.0, window="1D", min_exceedances=3
)

# Time estimate to reach critical threshold
tte = predictor.time_to_threshold(threshold=95.0)
print(f"Time to threshold: {tte}")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `remaining_useful_life()` | RUL via linear extrapolation to threshold | Timedelta estimate of remaining life |
| `detect_exceedance_pattern()` | Escalating threshold breaches over time | DataFrame of windows with increasing breach frequency |
| `time_to_threshold()` | Time estimate to reach a given threshold | Timedelta or None if trend is stable |

---

## Tips & Notes

!!! tip "Combine with degradation detection"
    Run `DegradationDetectionEvents.detect_trend_degradation()` first to confirm a real trend exists. Calling `remaining_useful_life()` on a stationary signal will return unreliable estimates.

!!! info "Related modules"
    - [`DegradationDetectionEvents`](degradation-detection.md) - Detect degradation trends before estimating RUL
    - [`VibrationAnalysisEvents`](vibration-analysis.md) - Vibration-specific failure indicators for rotating equipment

---

## See Also

- [Quality Guide](../../guides/quality.md)
- [API Reference](../../reference/ts_shape/events/maintenance/failure_prediction/)
