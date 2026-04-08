# MultiProcessTraceabilityEvents

> Trace items across a multi-station topology with parallel paths.

**Module:** `ts_shape.events.production.multi_process_traceability`
**Guide:** [Traceability Guide](../../guides/traceability.md)

---

## When to Use

Use for complex manufacturing topologies with parallel process lines, merges, and splits. Tracks items through non-linear routings where a single item may visit multiple stations simultaneously (e.g., sub-assemblies built in parallel then merged). This is the most powerful traceability module, suited for automotive or electronics assembly lines.

---

## Quick Example

```python
from ts_shape.events.production.multi_process_traceability import MultiProcessTraceabilityEvents

tracer = MultiProcessTraceabilityEvents(
    df=production_df,
    topology={
        "line_a": ["station-a1", "station-a2"],
        "line_b": ["station-b1", "station-b2"],
        "merge":  ["station-merge"],
        "final":  ["station-final-test"],
    },
    id_uuid="order-id-uuid"
)

# Full timeline across all stations
timeline = tracer.build_timeline()

# Items at multiple stations simultaneously
parallel = tracer.parallel_activity()

# Handover events between stations
handovers = tracer.handover_log()

# Most common routing paths
paths = tracer.routing_paths()
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `build_timeline()` | Full timeline across all stations and lines | `DataFrame` |
| `lead_time()` | End-to-end lead time per item | `DataFrame` |
| `parallel_activity()` | Detect items at multiple stations simultaneously | `DataFrame` |
| `handover_log()` | Log of handover events between stations | `DataFrame` |
| `station_statistics()` | Dwell time statistics per station | `DataFrame` |
| `routing_paths()` | Frequency of each unique routing path | `DataFrame` |

---

## Tips & Hints

!!! tip "Define your topology explicitly"
    Providing a topology dict lets the module distinguish parallel lines from sequential steps. Without it, the module must infer ordering from timestamps alone, which can be ambiguous.

!!! info "Related modules"
    - [Order Traceability](order-traceability.md) — simpler linear tracing
    - [Routing Traceability](routing-traceability.md) — routing with state signals
    - [Bottleneck Detection](bottleneck-detection.md) — identify bottlenecks in multi-station flows

---

## See Also

- [Traceability Guide](../../guides/traceability.md)
- [API Reference](../../reference/ts_shape/events/production/multi_process_traceability.md)
