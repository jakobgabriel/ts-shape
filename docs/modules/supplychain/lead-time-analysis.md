# LeadTimeAnalysisEvents

> Analyze lead times between order placement and delivery.

**Module:** `ts_shape.events.supplychain.lead_time_analysis`
**Guide:** [Production Guide](../../guides/production.md)

---

## When to Use

Use to monitor supplier and internal process lead times. Pairs order and delivery events to compute lead times and flag anomalies that may disrupt production planning. Essential for supply chain reliability assessment and vendor performance tracking.

---

## Quick Example

```python
from ts_shape.events.supplychain.lead_time_analysis import LeadTimeAnalysisEvents

analyzer = LeadTimeAnalysisEvents(
    df=orders_df,
    timestamp_col="timestamp",
    event_type_col="event_type",
    order_id_col="order_id"
)

# Match order placement to delivery events
lead_times = analyzer.calculate_lead_times(
    order_event="ORDER_PLACED",
    delivery_event="DELIVERED"
)

# Summary statistics across all orders
stats = analyzer.lead_time_statistics()
print(f"Mean lead time: {stats['mean']:.1f} days")
print(f"95th percentile: {stats['p95']:.1f} days")

# Flag orders with abnormally long lead times
anomalies = analyzer.detect_lead_time_anomalies(threshold_std=2.0)
print(f"Anomalous deliveries: {len(anomalies)}")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `calculate_lead_times()` | Match orders to deliveries and compute durations | DataFrame with order ID, lead time, and timestamps |
| `lead_time_statistics()` | Summary statistics (mean, median, percentiles) | Dict with mean, median, std, p5, p25, p75, p95 |
| `detect_lead_time_anomalies()` | Flag orders with abnormal lead times | DataFrame of anomalous orders with deviation score |

---

## Tips & Notes

!!! tip "Segment lead times by supplier or product"
    Global lead time statistics can hide per-supplier variation. Group by supplier before calling `lead_time_statistics()` to identify which vendors are unreliable and which are consistently fast.

!!! info "Related modules"
    - [`InventoryMonitoringEvents`](inventory-monitoring.md) - Lead time variability directly affects reorder point calculations
    - [`DemandPatternEvents`](demand-patterns.md) - Demand spikes combined with long lead times create stockout risk
    - [`AnomalyCorrelationEvents`](../correlation/anomaly-correlation.md) - Correlate lead time anomalies with other supply chain disruptions

---

## See Also

- [Production Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/supplychain/lead_time_analysis/)
