# QualityTracking

> Track NOK (defective) parts and quality metrics from OK/NOK counter signals.

**Module:** `ts_shape.events.production.quality_tracking`
**Guide:** [Production Monitoring](../../guides/production.md)

---

## When to Use

Use for quality tracking on production lines. Computes scrap rates, first-pass yield, and defect Pareto by reason code per shift. Pairs naturally with the OEE calculator's quality component and with part-level tracking for per-SKU quality analysis.

---

## Quick Example

```python
from ts_shape.events.production.quality_tracking import QualityTracking
import pandas as pd
import numpy as np

np.random.seed(42)
ok_counts = np.cumsum(np.random.choice([0, 1], size=480, p=[0.05, 0.95]))
nok_counts = np.cumsum(np.random.choice([0, 1], size=480, p=[0.97, 0.03]))
df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=480, freq="1min"),
    "ok_counter": ok_counts,
    "nok_counter": nok_counts,
    "part_id": ["PN-100"]*240 + ["PN-200"]*240,
    "defect_reason": np.random.choice(
        ["SCRATCH", "DIMENSION", "CRACK", "COSMETIC"], size=480
    ),
})

qt = QualityTracking(df, timestamp_column="timestamp")
by_shift = qt.nok_by_shift(ok_counter_uuid="ok_counter", nok_counter_uuid="nok_counter")
by_part = qt.quality_by_part(
    ok_counter_uuid="ok_counter", nok_counter_uuid="nok_counter", part_id_uuid="part_id"
)
by_reason = qt.nok_by_reason(nok_counter_uuid="nok_counter", defect_reason_uuid="defect_reason")
daily = qt.daily_quality_summary(ok_counter_uuid="ok_counter", nok_counter_uuid="nok_counter")
print(by_shift)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `nok_by_shift(ok_counter_uuid, nok_counter_uuid)` | Compute NOK count and scrap rate per shift | DataFrame with shift, ok_count, nok_count, and scrap_rate |
| `quality_by_part(ok_counter_uuid, nok_counter_uuid, part_id_uuid)` | Break down quality metrics by part number | DataFrame with part_id, ok_count, nok_count, and first_pass_yield |
| `nok_by_reason(nok_counter_uuid, defect_reason_uuid)` | Pareto of defect reasons by count | DataFrame with defect_reason, count, and cumulative percentage |
| `daily_quality_summary(ok_counter_uuid, nok_counter_uuid)` | Daily summary with total parts, rejects, and quality ratio | DataFrame with date, total, nok, and quality_ratio |

---

## Tips & Notes

!!! tip "Use monotonic counters, not deltas"
    Pass cumulative OK and NOK counters — the module computes deltas internally and handles counter resets. If your PLC provides per-cycle OK/NOK flags instead, convert them to cumulative sums first.

!!! info "Related modules"
    - [OEE Calculator](oee-calculator.md) — uses quality ratio as the third OEE factor
    - [Part Production Tracking](part-tracking.md) — production volumes to contextualize quality rates
    - [Batch Tracking](batch-tracking.md) — quality metrics per batch for process industries
    - [Cycle Time Tracking](cycle-time.md) — correlate slow cycles with quality defects

---

## See Also

- [Production Monitoring Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/production/quality_tracking/)
