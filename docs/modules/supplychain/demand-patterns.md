# DemandPatternEvents

> Analyze demand patterns from a timeseries demand signal.

**Module:** `ts_shape.events.supplychain.demand_pattern`
**Guide:** [Production Guide](../../guides/production.md)

---

## When to Use

Use to understand demand patterns for production planning. Identifies spikes, seasonal patterns, and trends that affect scheduling and inventory management. Works with order counts, request volumes, or any signal representing demand intensity over time.

---

## Quick Example

```python
from ts_shape.events.supplychain.demand_pattern import DemandPatternEvents

analyzer = DemandPatternEvents(
    df=orders_df,
    timestamp_col="timestamp",
    value_col="order_quantity"
)

# Aggregate demand per period
daily_demand = analyzer.demand_by_period(period="1D", agg="sum")

# Detect abnormal demand spikes
spikes = analyzer.detect_demand_spikes(
    window="7D", threshold_std=2.5
)
print(f"Detected {len(spikes)} demand spikes")

# Analyze day-of-week and hour-of-day seasonality
seasonality = analyzer.seasonality_summary()
print("Busiest day:", seasonality["day_of_week"].idxmax())
print("Peak hour:", seasonality["hour_of_day"].idxmax())
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `demand_by_period()` | Aggregate demand per time period | DataFrame with total/mean demand per period |
| `detect_demand_spikes()` | Flag abnormal demand levels | DataFrame of spike events with magnitude |
| `seasonality_summary()` | Day-of-week and hour-of-day patterns | DataFrame with average demand by time component |

---

## Tips & Hints

!!! tip "Remove known promotions before seasonality analysis"
    Promotional events create artificial spikes that distort `seasonality_summary()`. Filter out known promotion dates or use `detect_demand_spikes()` first to identify and exclude outliers before analyzing seasonal patterns.

!!! info "Related modules"
    - [`InventoryMonitoringEvents`](inventory-monitoring.md) - Monitor stock levels driven by the demand patterns you discover
    - [`LeadTimeAnalysisEvents`](lead-time-analysis.md) - Lead times that constrain how quickly you can respond to demand spikes
    - [`EnergyConsumptionEvents`](../energy/consumption-analysis.md) - Energy demand follows similar seasonal patterns

---

## See Also

- [Production Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/supplychain/demand_pattern.md)
