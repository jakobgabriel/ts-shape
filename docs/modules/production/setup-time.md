# SetupTimeTracking

> Track and analyze setup/changeover durations for SMED analysis.

**Module:** `ts_shape.events.production.setup_time_tracking`
**Guide:** [Reporting Guide](../../guides/reporting.md)

---

## When to Use

Use for SMED (Single-Minute Exchange of Dies) analysis. Tracks setup durations and analyzes them by product transition to identify which changeovers take longest. Essential for lean manufacturing initiatives aimed at reducing changeover time and increasing available production time.

---

## Quick Example

```python
from ts_shape.events.production.setup_time_tracking import SetupTimeTracking

tracker = SetupTimeTracking(
    df=production_df,
    start_time="2024-01-01",
    end_time="2024-03-31"
)

# List every setup event with duration
setups = tracker.setup_durations(state_uuid="machine-state-001")

# Setup statistics grouped by product transition
by_product = tracker.setup_by_product(
    state_uuid="machine-state-001",
    part_id_uuid="part-id-001"
)

# Overall setup time statistics
stats = tracker.setup_statistics(state_uuid="machine-state-001")

# Weekly trend of setup durations
trend = tracker.setup_trend(state_uuid="machine-state-001", window="1W")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `setup_durations(state_uuid)` | List every setup event with start, end, and duration | `DataFrame` |
| `setup_by_product(state_uuid, part_id_uuid)` | Setup time statistics grouped by product transition pair | `DataFrame` |
| `setup_statistics(state_uuid)` | Overall setup time statistics (mean, median, std, total) | `DataFrame` |
| `setup_trend(state_uuid, window='1W')` | Rolling trend of setup durations over time | `DataFrame` |

---

## Tips & Notes

!!! tip "Separate internal and external setup tasks"
    SMED distinguishes between internal setup (machine stopped) and external setup (done while running). If your state signal encodes both, filter for internal-only to get the true changeover impact.

!!! info "Related modules"
    - [Changeover](changeover.md) — changeover event detection from state transitions
    - [Performance Loss](performance-loss.md) — speed losses that may occur after setup
    - [OEE Calculator](oee-calculator.md) — setup time feeds into availability losses

---

## See Also

- [Reporting Guide](../../guides/reporting.md)
- [API Reference](../../reference/ts_shape/events/production/setup_time_tracking/)
