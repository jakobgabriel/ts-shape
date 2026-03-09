# RoutingTraceabilityEvents

> Trace item routing using an ID signal paired with a state/routing signal.

**Module:** `ts_shape.events.production.routing_traceability`
**Guide:** [Traceability Guide](../../guides/traceability.md)

---

## When to Use

Use when items follow defined routing paths through stations. Pairs an ID signal with a routing/state signal to track which process step each item is in. This is especially useful when a single station can perform multiple process steps and you need to distinguish between them.

---

## Quick Example

```python
from ts_shape.events.production.routing_traceability import RoutingTraceabilityEvents

tracer = RoutingTraceabilityEvents(
    df=production_df,
    id_uuid="serial-number-uuid",
    routing_uuid="routing-step-uuid",
    station_uuids=["station-001", "station-002", "station-003"]
)

# Correlate ID with routing signal
timeline = tracer.build_routing_timeline()

# End-to-end lead time per item
lead_times = tracer.lead_time()

# Which routing paths are most common?
paths = tracer.routing_paths()

# Dwell time statistics per routing step
stats = tracer.station_statistics()
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `build_routing_timeline()` | Correlate ID signal with routing signal per station | `DataFrame` |
| `lead_time()` | End-to-end lead time per item | `DataFrame` |
| `station_statistics()` | Dwell time statistics per routing step | `DataFrame` |
| `routing_paths()` | Frequency of each unique routing path taken | `DataFrame` |

---

## Tips & Notes

!!! tip "Map routing codes to readable names"
    Routing signals often carry numeric codes. Map them to human-readable step names before analysis for clearer reports and visualizations.

!!! info "Related modules"
    - [Order Traceability](order-traceability.md) — simpler tracing without routing signals
    - [Multi-Process Traceability](multi-process-traceability.md) — handles parallel paths and merges
    - [Cycle Time Tracking](cycle-time-tracking.md) — per-step cycle time analysis

---

## See Also

- [Traceability Guide](../../guides/traceability.md)
- [API Reference](../../reference/ts_shape/events/production/routing_traceability/)
