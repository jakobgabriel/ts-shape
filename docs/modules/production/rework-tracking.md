# ReworkTracking

> Track parts that require rework from rework counter and reason-code signals.

**Module:** `ts_shape.events.production.rework_tracking`
**Guide:** [Reporting Guide](../../guides/reporting.md)

---

## When to Use

Use to track rework events and their cost. Identifies which parts and reasons drive the most rework, enabling targeted process improvements. Especially valuable for plants where rework is a significant cost driver and management needs visibility into root causes and financial impact.

---

## Quick Example

```python
from ts_shape.events.production.rework_tracking import ReworkTracking

tracker = ReworkTracking(
    df=production_df,
    start_time="2024-01-01",
    end_time="2024-03-31"
)

# Rework counts per shift
by_shift = tracker.rework_by_shift(rework_uuid="rework-counter-001")

# Rework breakdown by reason code
by_reason = tracker.rework_by_reason(
    rework_uuid="rework-counter-001",
    reason_uuid="reason-code-001"
)

# Rework rate as percentage of total production
rate = tracker.rework_rate(
    rework_uuid="rework-counter-001",
    total_production_uuid="total-counter-001"
)

# Monetary cost of rework by part type
rework_costs = {"part-A": 12.50, "part-B": 8.75, "part-C": 22.00}
cost = tracker.rework_cost(
    rework_uuid="rework-counter-001",
    part_id_uuid="part-id-001",
    rework_costs=rework_costs
)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `rework_by_shift(rework_uuid)` | Rework count per shift | `DataFrame` |
| `rework_by_reason(rework_uuid, reason_uuid)` | Rework count grouped by reason code | `DataFrame` |
| `rework_rate(rework_uuid, total_production_uuid)` | Rework rate as percentage of total production | `DataFrame` |
| `rework_cost(rework_uuid, part_id_uuid, rework_costs)` | Monetary cost of rework by part type | `DataFrame` |
| `rework_trend(rework_uuid, window='1D')` | Rolling trend of rework counts over time | `DataFrame` |

---

## Tips & Hints

!!! tip "Combine with Pareto analysis"
    Sort `rework_by_reason` results by count descending to build a Pareto chart. Typically 20% of reason codes drive 80% of rework volume, giving you clear improvement targets.

!!! info "Related modules"
    - [Scrap Tracking](scrap-tracking.md) — track scrap/waste that cannot be reworked
    - [Quality Tracking](quality-tracking.md) — overall quality metrics including FPY
    - [Operator Performance](operator-performance.md) — quality by operator

---

## See Also

- [Reporting Guide](../../guides/reporting.md)
- [API Reference](../../reference/ts_shape/events/production/rework_tracking.md)
