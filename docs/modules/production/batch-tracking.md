# BatchTrackingEvents

> Track batch/recipe production from a batch-ID string signal.

**Module:** `ts_shape.events.production.batch_tracking`
**Guide:** [OEE Analytics](../../guides/oee-analytics.md)

---

## When to Use

Use for batch production environments (food, pharma, chemicals). Tracks batch boundaries from a batch-ID signal and computes duration and yield statistics. Essential for regulatory traceability and for optimizing batch scheduling to minimize transition losses.

---

## Quick Example

```python
from ts_shape.events.production.batch_tracking import BatchTrackingEvents
import pandas as pd
import numpy as np

df = pd.DataFrame({
    "timestamp": pd.date_range("2024-01-01 06:00", periods=360, freq="1min"),
    "batch_id": ["BATCH-001"]*90 + ["BATCH-002"]*120 + ["BATCH-003"]*150,
    "part_counter": np.arange(1, 361),
})

bt = BatchTrackingEvents(df, timestamp_column="timestamp")
batches = bt.detect_batches()
stats = bt.batch_duration_stats()
yields = bt.batch_yield(counter_uuid="part_counter")
matrix = bt.batch_transition_matrix()
print(batches)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `detect_batches()` | Identify batch start and end times from value changes in the batch-ID signal | DataFrame with batch_id, start, end, and duration |
| `batch_duration_stats()` | Compute duration statistics (min, mean, max, std) grouped by batch type | DataFrame with duration statistics per batch type |
| `batch_yield(counter_uuid)` | Calculate production yield per batch using a counter signal | DataFrame with batch_id and total parts produced |
| `batch_transition_matrix()` | Build a matrix showing which batch follows which, useful for scheduling analysis | DataFrame pivot table of from-batch vs to-batch counts |

---

## Tips & Hints

!!! tip "Watch for empty or null batch IDs"
    Gaps in the batch-ID signal (empty strings or nulls) often represent cleaning or changeover periods. Filter these out or treat them as explicit changeover events.

!!! info "Related modules"
    - [Changeover](changeover.md) — detects product changes, complementary for discrete manufacturing
    - [Part Production Tracking](part-tracking.md) — tracks production by part number rather than batch
    - [Quality Tracking](quality-tracking.md) — quality metrics that can be joined to batch data

---

## See Also

- [OEE Analytics Guide](../../guides/oee-analytics.md)
- [API Reference](../../reference/ts_shape/events/production/batch_tracking/)
