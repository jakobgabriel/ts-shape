# GaugeRepeatabilityEvents

> Measurement System Analysis (MSA) for inline sensors. Evaluates repeatability and reproducibility using repeated measurements.

**Module:** `ts_shape.events.quality.gauge_repeatability`  
**Guide:** [Quality Control & SPC](../../guides/quality.md)

---

## When to Use

Use for Measurement System Analysis when qualifying inline sensors. Required by IATF 16949 and other quality standards. Evaluates whether measurement variation comes from the equipment (repeatability) or the operator/condition (reproducibility). Run during sensor installation, after calibration, or on a periodic qualification schedule.

---

## Quick Example

```python
from ts_shape.events.quality.gauge_repeatability import GaugeRepeatabilityEvents

grr = GaugeRepeatabilityEvents(
    df,
    value_column="measurement",
    part_column="part_id",
    operator_column="operator",
)

# Equipment Variation (repeatability)
ev = grr.repeatability(n_trials=3)

# Appraiser Variation (reproducibility)
av = grr.reproducibility()

# Full GR&R summary with tolerance range
summary = grr.gauge_rr_summary(tolerance_range=10.0)
print(f"GR&R %: {summary['grr_percent']:.1f}%")
print(f"Acceptable: {summary['grr_percent'] < 10}")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `repeatability(n_trials=None)` | Equipment Variation (EV) — within-operator, within-part variation | Dictionary with EV metrics |
| `reproducibility()` | Appraiser Variation (AV) — between-operator variation | Dictionary with AV metrics |
| `gauge_rr_summary(tolerance_range=None)` | Full GR&R summary: EV, AV, GR&R, %GR&R, ndc | Dictionary with complete MSA results |
| `measurement_bias(reference_values)` | Compare measurements to known reference standards | DataFrame with bias statistics |

---

## Tips & Hints

!!! tip "Interpret %GR&R against AIAG guidelines"
    A %GR&R below 10% is generally acceptable, 10-30% may be acceptable depending on the application, and above 30% indicates the measurement system needs improvement. Always provide the `tolerance_range` to get %GR&R relative to the specification width.

!!! info "Related modules"
    - [Multi-Sensor Validation](multi-sensor-validation.md) — cross-validate redundant sensors in production
    - [Sensor Drift](sensor-drift.md) — monitor calibration drift between MSA studies
    - [Capability Trending](capability-trending.md) — ensure measurement system supports required Cpk

---

## See Also

- [Quality Control & SPC Guide](../../guides/quality.md) — narrative overview
- [API Reference](../../reference/ts_shape/events/quality/gauge_repeatability/) — full parameter docs
