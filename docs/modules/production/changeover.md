# ChangeoverEvents

> Detect product/recipe changes and compute changeover windows.

**Module:** `ts_shape.events.production.changeover`
**Guide:** [Production Monitoring](../../guides/production.md)

---

## When to Use

Use to track product/recipe changes on production lines. Detects when the product signal changes value and computes changeover duration. Essential for understanding SMED (Single-Minute Exchange of Die) improvements and tracking setup time as a component of planned downtime.

---

## Quick Example

```python
from ts_shape.events.production.changeover import ChangeoverEvents
import pandas as pd

df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=360, freq="1min"),
    "product_id": ["SKU-A"]*120 + ["SKU-B"]*100 + ["SKU-A"]*140,
})

co = ChangeoverEvents(df, timestamp_column="timestamp")
changes = co.detect_changeover(product_uuid="product_id")
windows = co.changeover_window(product_uuid="product_id", until="fixed_window")
print(changes)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `detect_changeover(product_uuid)` | Generate point events at each product/recipe change | DataFrame with timestamp, previous product, and new product |
| `changeover_window(product_uuid, until='fixed_window')` | Compute changeover duration windows from change point to next stable production | DataFrame with start, end, duration, and product pair |
| `changeover_quality_metrics(product_uuid)` | Compute quality metrics around changeover events such as first-article pass rate | DataFrame with changeover quality statistics |

---

## Tips & Notes

!!! tip "Combine with machine state"
    Pair changeover detection with `MachineStateEvents` to distinguish changeover downtime from unplanned downtime — changeovers typically show a planned idle pattern.

!!! info "Related modules"
    - [Machine State](machine-state.md) — run/idle detection to separate changeover idle from unplanned stops
    - [Batch Tracking](batch-tracking.md) — similar concept for batch-ID signals in process industries
    - [Downtime Tracking](downtime.md) — categorize changeover as planned downtime

---

## See Also

- [Production Monitoring Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/production/changeover/)
