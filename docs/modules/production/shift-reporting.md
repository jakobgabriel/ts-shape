# ShiftReporting

> Simple shift-based production reporting from counter and part-ID signals.

**Module:** `ts_shape.events.production.shift_reporting`
**Guide:** [Production Guide](../../guides/production.md)

---

## When to Use

Use for daily shift performance reporting. Computes production quantities per shift and compares to targets and historical performance. Ideal for shift supervisors who need a quick view of how each shift performed relative to plan.

---

## Quick Example

```python
from ts_shape.events.production.shift_reporting import ShiftReporting

reporter = ShiftReporting(
    df=production_df,
    start_time="2024-01-01",
    end_time="2024-01-31"
)

# Production totals per shift
shift_prod = reporter.shift_production(counter_uuid="counter-001")

# Compare shifts over the last 7 days
comparison = reporter.shift_comparison(counter_uuid="counter-001", days=7)

# Check actual vs targets
targets = {"morning": 500, "afternoon": 480, "night": 400}
result = reporter.shift_targets(counter_uuid="counter-001", targets=targets)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `shift_production(counter_uuid, part_id_uuid=None)` | Production totals per shift, optionally split by part ID | `DataFrame` |
| `shift_comparison(counter_uuid, days=7)` | Compare shift performance over a number of days | `DataFrame` |
| `shift_targets(counter_uuid, targets)` | Compare actual production against per-shift targets | `DataFrame` |
| `best_and_worst_shifts(counter_uuid, days=30)` | Identify best and worst performing shifts over a period | `DataFrame` |

---

## Tips & Hints

!!! tip "Define shift boundaries consistently"
    Ensure your shift start and end times are aligned with your plant's actual shift calendar. Misaligned boundaries will split production counts incorrectly.

!!! info "Related modules"
    - [Target Tracking](target-tracking.md) — generic target vs actual comparison
    - [Shift Handover](shift-handover.md) — full handover reports combining production, quality, and downtime
    - [Period Summary](period-summary.md) — roll up shift data into weekly/monthly summaries

---

## See Also

- [Production Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/production/shift_reporting/)
