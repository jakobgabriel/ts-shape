# StatisticalProcessControlRuleBased

> Applies SPC rules (Western Electric Rules) to a DataFrame for event detection using control limit UUIDs and actual value UUIDs.

**Module:** `ts_shape.events.quality.statistical_process_control`  
**Guide:** [Quality Control & SPC](../../guides/quality.md)

---

## When to Use

Use for real-time quality monitoring when you have a process signal and corresponding control limits. Ideal for detecting shifts, trends, and patterns that indicate a process is going out of control per the 8 Western Electric rules. Requires a DataFrame with actual values and tolerance/control limit columns.

---

## Quick Example

```python
from ts_shape.events.quality.statistical_process_control import StatisticalProcessControlRuleBased

spc = StatisticalProcessControlRuleBased(
    df,
    actual_uuid="sensor:temp",
    tolerance_uuid="limit:temp",
)

# Run the full SPC pipeline (calculates limits + applies all rules)
result = spc.process()

# Or apply specific rules only
limits = spc.calculate_control_limits()
violations = spc.apply_rules_vectorized(selected_rules=[1, 2, 5])
summary = spc.interpret_violations(violations)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `calculate_control_limits()` | Calculate mean and 1/2/3 sigma limits | DataFrame with control limits |
| `calculate_dynamic_control_limits(method='moving_range', window=20)` | Adaptive control limits for non-stationary processes | DataFrame with dynamic limits |
| `apply_rules_vectorized(selected_rules=None)` | Apply selected Western Electric rules efficiently | DataFrame with violation flags |
| `detect_cusum_shifts(target, k, h)` | CUSUM shift detection for small sustained shifts | DataFrame with CUSUM statistics |
| `interpret_violations(violations_df)` | Generate human-readable violation interpretations | DataFrame with descriptions |
| `process(selected_rules=None)` | Full SPC pipeline: limits + rules + interpretation | DataFrame with complete results |
| `rule_1` through `rule_8` | Individual Western Electric rule checks | DataFrame with single rule flags |

---

## Tips & Notes

!!! tip "Start with the process() method"
    The `process()` method runs the complete pipeline and is the easiest entry point. Use individual rules or `apply_rules_vectorized(selected_rules=...)` only when you need to tune which rules apply to your specific process.

!!! info "Related modules"
    - [Tolerance Deviation](tolerance-deviation.md) — specification-limit-based deviation tracking with Cp/Cpk
    - [Capability Trending](capability-trending.md) — track capability indices over time
    - [Outlier Detection](outlier-detection.md) — statistical outlier detection as a preprocessing step

---

## See Also

- [Quality Control & SPC Guide](../../guides/quality.md) — narrative overview
- [API Reference](../../reference/ts_shape/events/quality/statistical_process_control/) — full parameter docs
