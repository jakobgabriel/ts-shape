# ShiftHandoverReport

> Generate automated shift handover reports combining production, quality, and downtime.

**Module:** `ts_shape.events.production.shift_handover`
**Guide:** [Reporting Guide](../../guides/reporting.md)

---

## When to Use

Use to generate automated shift handover reports for shift meetings. Combines production, quality, and downtime data into a single summary with issue highlighting. Replaces manual handover notes with a structured, data-driven report that ensures nothing is missed between shifts.

---

## Quick Example

```python
from ts_shape.events.production.shift_handover import ShiftHandoverReport

report = ShiftHandoverReport(
    df=production_df,
    start_time="2024-01-15 06:00",
    end_time="2024-01-15 14:00"
)

# Generate from raw signals
handover = report.generate_report(
    counter_uuid="counter-001",
    ok_counter_uuid="ok-counter-001",
    nok_counter_uuid="nok-counter-001",
    state_uuid="machine-state-001"
)

# Highlight issues that need attention
thresholds = {"min_output": 450, "min_quality_pct": 98.0, "max_downtime_min": 30}
issues = report.highlight_issues(thresholds=thresholds)

# Or build from pre-computed DataFrames
handover = ShiftHandoverReport.from_shift_data(
    production_df=shift_production,
    quality_df=shift_quality,
    downtime_df=shift_downtime
)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `from_shift_data(production_df, quality_df=None, downtime_df=None)` | Build report from pre-computed DataFrames | `ShiftHandoverReport` |
| `generate_report(counter_uuid, ok_counter_uuid, nok_counter_uuid, state_uuid)` | Generate report from raw signal UUIDs | `DataFrame` |
| `highlight_issues(thresholds=None)` | Identify issues exceeding thresholds for incoming shift attention | `DataFrame` |

---

## Tips & Notes

!!! tip "Customize thresholds per line"
    Different production lines have different normal operating ranges. Set per-line thresholds in `highlight_issues` so that alerts are meaningful and not ignored due to false positives.

!!! info "Related modules"
    - [Shift Reporting](shift-reporting.md) — production totals feeding into handover reports
    - [Quality Tracking](quality-tracking.md) — quality data for the handover
    - [Downtime Tracking](downtime-tracking.md) — downtime data for the handover

---

## See Also

- [Reporting Guide](../../guides/reporting.md)
- [API Reference](../../reference/ts_shape/events/production/shift_handover/)
