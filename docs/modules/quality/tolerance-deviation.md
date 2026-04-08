# ToleranceDeviationEvents

> Processes DataFrame data for comparing tolerance and actual values with severity classification and process capability indices.

**Module:** `ts_shape.events.quality.tolerance_deviation`  
**Guide:** [Quality Control & SPC](../../guides/quality.md)

---

## When to Use

Use when you have process signals with defined upper/lower specification limits and need to track deviations with severity classification. Computes Cp/Cpk/Pp/Ppk indices for process capability assessment. Requires a DataFrame with actual measurement values and corresponding specification limits.

---

## Quick Example

```python
from ts_shape.events.quality.tolerance_deviation import ToleranceDeviationEvents

tdev = ToleranceDeviationEvents(df, value_column="value_double")

# Apply tolerance checks with severity classification
events = tdev.process_and_group_data_with_events()

# Compute process capability indices
capability = tdev.compute_capability_indices(target_value=50.0)
print(f"Cpk: {capability['Cpk']:.2f}, Ppk: {capability['Ppk']:.2f}")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `process_and_group_data_with_events()` | Apply tolerance checks with severity classification | DataFrame with deviation events and severity levels |
| `compute_capability_indices(target_value=None)` | Calculate Cp, Cpk, Pp, Ppk capability indices | Dictionary with capability metrics |

---

## Tips & Hints

!!! tip "Set a target value for Cpk accuracy"
    When calling `compute_capability_indices`, always provide the `target_value` parameter if your process has a nominal target. Without it, the method assumes the midpoint of the specification range, which may overestimate Cpk for off-center processes.

!!! info "Related modules"
    - [SPC Rules](spc.md) — Western Electric rule-based monitoring with control limits
    - [Capability Trending](capability-trending.md) — track Cp/Cpk over rolling time windows
    - [Sensor Drift](sensor-drift.md) — detect calibration drift that can cause systematic deviations

---

## See Also

- [Quality Control & SPC Guide](../../guides/quality.md) — narrative overview
- [API Reference](../../reference/ts_shape/events/quality/tolerance_deviation.md) — full parameter docs
