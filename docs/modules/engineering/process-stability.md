# ProcessStabilityIndex

> Generate a single 0-100 stability score per shift/day for a signal.

**Module:** `ts_shape.events.engineering.process_stability_index`  
**Guide:** [Process Engineering](../../guides/engineering.md)

---

## When to Use

Use as a single-number KPI for process health dashboards. Answers "is my process running well today?" at a glance. Combine with other modules for detailed root cause analysis when the score drops. Ideal for management dashboards, shift handover summaries, and cross-plant benchmarking.

---

## Quick Example

```python
from ts_shape.events.engineering.process_stability_index import ProcessStabilityIndex

scorer = ProcessStabilityIndex(
    df=process_data,
    uuid="reactor_temperature_01"
)

# Get a 0-100 stability score per 8-hour shift
scores = scorer.stability_score(window="8h")

# Track score trend over the past 7 shifts
trend = scorer.score_trend(window="8h", n_windows=7)

# Find the 5 worst 1-hour periods for investigation
worst = scorer.worst_periods(window="1h", n=5)

# Compare current performance to historical best
comparison = scorer.stability_comparison(window="8h")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `stability_score(window='8h')` | Composite 0-100 stability score | DataFrame with scores per window |
| `score_trend(window='8h', n_windows=7)` | Score trend over N windows | DataFrame with trend data |
| `worst_periods(window='1h', n=5)` | N worst-scoring windows | DataFrame of worst periods |
| `stability_comparison(window='8h')` | Compare to historical best | DataFrame with comparison metrics |

---

## Tips & Hints

!!! tip "Use worst_periods to drill down from a low score"
    When the shift-level score drops, call `worst_periods(window='1h', n=5)` to pinpoint the exact hours that dragged the score down. Then use module-specific tools (disturbance recovery, rate of change, etc.) on those windows for root cause analysis.

!!! info "Related modules"
    - [Process Windows](process-windows.md) — detailed windowed statistics behind the score
    - [Disturbance Recovery](disturbance-recovery.md) — investigate disturbances that lowered the score
    - [Control Loop Health](control-loop-health.md) — loop-level diagnostics when control quality degrades
    - [Steady State Detection](steady-state.md) — stability score is most meaningful during steady state

---

## See Also

- [Process Engineering Guide](../../guides/engineering.md)
- [API Reference](../../reference/ts_shape/events/engineering/process_stability_index.md)
