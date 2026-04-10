# AnomalyCorrelationEvents

> Correlate anomaly events across multiple signals to find coincident patterns, cascading failures, and root cause candidates.

**Module:** `ts_shape.events.correlation.anomaly_correlation`
**Guide:** [Statistics Guide](../../guides/statistics.md)

---

## When to Use

Use after anomaly detection on individual signals to understand relationships. Finds root cause candidates by identifying which signals' anomalies consistently precede others. Essential for complex systems where a fault in one subsystem cascades through multiple sensors.

---

## Quick Example

```python
from ts_shape.events.correlation.anomaly_correlation import AnomalyCorrelationEvents

correlator = AnomalyCorrelationEvents(
    df=anomaly_df,
    timestamp_col="timestamp",
    signal_col="signal_name",
    anomaly_col="is_anomaly"
)

# Find anomalies that co-occur within a 10-minute window
coincident = correlator.coincident_anomalies(window="10T")
print(f"Found {len(coincident)} coincident anomaly groups")

# Detect cascading patterns: signal A anomaly precedes signal B
cascades = correlator.cascade_detection(
    window="15T", min_occurrences=3
)

# Rank signals by how often their anomalies precede others
ranking = correlator.root_cause_ranking()
print("Top root cause candidates:")
print(ranking.head(5)[["signal_name", "precedence_score"]])
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `coincident_anomalies()` | Co-occurring anomalies within time window | DataFrame of anomaly groups with participating signals |
| `cascade_detection()` | Anomaly A precedes anomaly B within window | DataFrame of directed cascade pairs with counts |
| `root_cause_ranking()` | Rank signals by how often they precede others | DataFrame of signals ranked by precedence score |

---

## Tips & Hints

!!! tip "Tune the cascade window carefully"
    A window that is too short misses real cascades; too long produces false associations. Start with the known propagation time of your process (e.g., fluid transit time between sensors) and adjust from there.

!!! info "Related modules"
    - [`SignalCorrelationEvents`](signal-correlation.md) - Correlate raw signal values instead of anomaly events
    - [`FailurePredictionEvents`](../maintenance/failure-prediction.md) - Predict failure timing once root cause is identified
    - [`DegradationDetectionEvents`](../maintenance/degradation-detection.md) - Detect the degradation patterns that generate anomalies

---

## See Also

- [Statistics Guide](../../guides/statistics.md)
- [API Reference](../../reference/ts_shape/events/correlation/anomaly_correlation.md)
