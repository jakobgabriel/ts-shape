# ScrapTracking

> Track material scrap and waste from scrap and reason-code signals.

**Module:** `ts_shape.events.production.scrap_tracking`
**Guide:** [Reporting Guide](../../guides/reporting.md)

---

## When to Use

Use for scrap/waste tracking and cost accounting. Converts scrap quantities to monetary cost by material type for financial reporting. Essential for plants focused on material efficiency and sustainability goals, where understanding scrap drivers enables targeted waste reduction.

---

## Quick Example

```python
from ts_shape.events.production.scrap_tracking import ScrapTracking

tracker = ScrapTracking(
    df=production_df,
    start_time="2024-01-01",
    end_time="2024-03-31"
)

# Scrap counts per shift
by_shift = tracker.scrap_by_shift(scrap_uuid="scrap-counter-001")

# Scrap breakdown by reason code
by_reason = tracker.scrap_by_reason(
    scrap_uuid="scrap-counter-001",
    reason_uuid="scrap-reason-001"
)

# Monetary cost of scrap by material type
material_costs = {"steel": 3.20, "aluminum": 5.80, "plastic": 1.10}
cost = tracker.scrap_cost(
    scrap_uuid="scrap-counter-001",
    part_id_uuid="part-id-001",
    material_costs=material_costs
)

# Daily scrap trend
trend = tracker.scrap_trend(scrap_uuid="scrap-counter-001", window="1D")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `scrap_by_shift(scrap_uuid)` | Scrap count per shift | `DataFrame` |
| `scrap_by_reason(scrap_uuid, reason_uuid)` | Scrap count grouped by reason code | `DataFrame` |
| `scrap_cost(scrap_uuid, part_id_uuid, material_costs)` | Monetary cost of scrap by material type | `DataFrame` |
| `scrap_trend(scrap_uuid, window='1D')` | Rolling trend of scrap counts over time | `DataFrame` |

---

## Tips & Hints

!!! tip "Track scrap at the point of generation"
    Place scrap counters as close to the source as possible. If scrap is only counted at end-of-line inspection, you lose visibility into which station generated it. Per-station scrap signals enable root-cause analysis.

!!! info "Related modules"
    - [Rework Tracking](rework-tracking.md) — parts that can be reworked instead of scrapped
    - [Quality Tracking](quality-tracking.md) — overall quality metrics including scrap rates
    - [OEE Calculator](oee-calculator.md) — scrap feeds into the quality component of OEE

---

## See Also

- [Reporting Guide](../../guides/reporting.md)
- [API Reference](../../reference/ts_shape/events/production/scrap_tracking/)
