# VibrationAnalysisEvents

> Analyse vibration signals from industrial equipment: RMS exceedance, amplitude growth, and bearing health indicators.

**Module:** `ts_shape.events.maintenance.vibration_analysis`
**Guide:** [Quality Guide](../../guides/quality.md)

---

## When to Use

Use for rotating equipment monitoring (motors, pumps, compressors). Computes standard ISO 10816 vibration indicators for bearing health assessment. Works with accelerometer or velocity sensor data sampled at regular intervals.

---

## Quick Example

```python
from ts_shape.events.maintenance.vibration_analysis import VibrationAnalysisEvents

analyzer = VibrationAnalysisEvents(
    df=vibration_df,
    timestamp_col="timestamp",
    value_col="accel_x"
)

# Detect RMS exceedance against a known-good baseline
rms_events = analyzer.detect_rms_exceedance(
    window="1H", baseline_rms=2.5, threshold_factor=1.5
)

# Track amplitude growth over time
growth = analyzer.detect_amplitude_growth(window="1D", slope_threshold=0.01)

# Full bearing health indicators per window
health = analyzer.bearing_health_indicators(window="4H")
print(health[["rms", "peak", "crest_factor", "kurtosis"]].tail())
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `detect_rms_exceedance()` | Rolling RMS vs baseline threshold | DataFrame of windows exceeding RMS threshold |
| `detect_amplitude_growth()` | Peak-to-peak amplitude trend detection | DataFrame of windows with growing amplitude |
| `bearing_health_indicators()` | RMS, peak, crest factor, kurtosis per window | DataFrame with all health indicators per window |

---

## Tips & Notes

!!! tip "Use ISO 10816 thresholds for RMS baseline"
    For standard industrial motors, ISO 10816 provides vibration severity thresholds by machine class. Use these as your `baseline_rms` and `threshold_factor` values for meaningful alerts.

!!! info "Related modules"
    - [`DegradationDetectionEvents`](degradation-detection.md) - General-purpose degradation detection for any signal type
    - [`FailurePredictionEvents`](failure-prediction.md) - Estimate remaining useful life from vibration trends
    - [`SignalCorrelationEvents`](../correlation/signal-correlation.md) - Correlate vibration with temperature or current signals

---

## See Also

- [Quality Guide](../../guides/quality.md)
- [API Reference](../../reference/ts_shape/events/maintenance/vibration_analysis/)
