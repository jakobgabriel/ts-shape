# PeriodSummary

> Aggregate daily metrics into weekly/monthly summaries.

**Module:** `ts_shape.events.production.period_summary`
**Guide:** [Reporting Guide](../../guides/reporting.md)

---

## When to Use

Use to roll up daily production data into weekly or monthly summaries. Enables period-over-period comparison for management reporting. Ideal for generating the weekly and monthly KPI reports that plant management and corporate teams rely on for capacity planning and performance reviews.

---

## Quick Example

```python
from ts_shape.events.production.period_summary import PeriodSummary

summarizer = PeriodSummary(
    df=production_df,
    start_time="2024-01-01",
    end_time="2024-06-30"
)

# Weekly summary from raw signals
weekly = summarizer.weekly_summary(counter_uuid="counter-001")

# Monthly summary from raw signals
monthly = summarizer.monthly_summary(counter_uuid="counter-001")

# Compare two specific periods
comparison = summarizer.compare_periods(
    counter_uuid="counter-001",
    period1=("2024-01-01", "2024-03-31"),
    period2=("2024-04-01", "2024-06-30")
)

# Or roll up an existing daily DataFrame
weekly_from_df = PeriodSummary.from_daily_data(
    daily_df=daily_metrics,
    freq="W"
)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `from_daily_data(daily_df, freq='W')` | Roll up a daily DataFrame to weekly or monthly frequency | `DataFrame` |
| `weekly_summary(counter_uuid)` | Weekly production summary from raw signals | `DataFrame` |
| `monthly_summary(counter_uuid)` | Monthly production summary from raw signals | `DataFrame` |
| `compare_periods(counter_uuid, period1, period2)` | Side-by-side comparison of two date ranges | `DataFrame` |

---

## Tips & Hints

!!! tip "Align periods to calendar boundaries"
    Use ISO week boundaries (Monday start) or calendar month boundaries for consistency. Partial weeks or months at the edges of your date range can skew averages and make period comparisons misleading.

!!! info "Related modules"
    - [Shift Reporting](shift-reporting.md) — shift-level data that feeds into daily and period summaries
    - [Target Tracking](target-tracking.md) — compare period summaries against targets
    - [OEE Calculator](oee-calculator.md) — period-level OEE trends

---

## See Also

- [Reporting Guide](../../guides/reporting.md)
- [API Reference](../../reference/ts_shape/events/production/period_summary/)
