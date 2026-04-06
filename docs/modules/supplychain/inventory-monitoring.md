# InventoryMonitoringEvents

> Monitor inventory levels from a timeseries signal and detect supply chain events.

**Module:** `ts_shape.events.supplychain.inventory_monitoring`
**Guide:** [Production Guide](../../guides/production.md)

---

## When to Use

Use for real-time inventory monitoring in manufacturing. Tracks stock levels, calculates consumption rates, and predicts when a stockout will occur based on current consumption trends. Works with any signal representing a quantity that depletes over time and is periodically replenished.

---

## Quick Example

```python
from ts_shape.events.supplychain.inventory_monitoring import InventoryMonitoringEvents

monitor = InventoryMonitoringEvents(
    df=inventory_df,
    timestamp_col="timestamp",
    value_col="stock_level"
)

# Flag intervals where stock drops below safety threshold
low_stock = monitor.detect_low_stock(threshold=100, min_duration="2H")
print(f"Low stock events: {len(low_stock)}")

# Calculate rolling consumption rate
rate = monitor.consumption_rate(window="1D")

# Detect when stock falls below the reorder point
breaches = monitor.reorder_point_breach(reorder_point=250)

# Predict time until stockout at current consumption rate
prediction = monitor.stockout_prediction(window="7D")
if prediction is not None:
    print(f"Predicted stockout in: {prediction.days} days")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `detect_low_stock()` | Flag low inventory intervals | DataFrame of periods below stock threshold |
| `consumption_rate()` | Rolling consumption rate | DataFrame with consumption rate per window |
| `reorder_point_breach()` | Detect when stock falls below reorder point | DataFrame of breach events with timestamps |
| `stockout_prediction()` | Time estimate until stockout | Timedelta estimate or None if stock is stable |

---

## Tips & Hints

!!! tip "Account for replenishment events"
    Stock level jumps (replenishments) can skew `consumption_rate()`. Filter out positive deltas or use a median-based rate to get robust consumption estimates that ignore restocking spikes.

!!! info "Related modules"
    - [`DemandPatternEvents`](demand-patterns.md) - Understand demand patterns driving inventory depletion
    - [`LeadTimeAnalysisEvents`](lead-time-analysis.md) - Monitor supplier lead times that affect reorder timing
    - [`EnergyConsumptionEvents`](../energy/consumption-analysis.md) - Similar depletion pattern analysis for energy resources

---

## See Also

- [Production Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/supplychain/inventory_monitoring/)
