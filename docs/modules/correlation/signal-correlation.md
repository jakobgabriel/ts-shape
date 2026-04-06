# SignalCorrelationEvents

> Analyze time-windowed correlations between pairs of numeric signals.

**Module:** `ts_shape.events.correlation.signal_correlation`
**Guide:** [Statistics Guide](../../guides/statistics.md)

---

## When to Use

Use to monitor relationships between process variables. Detects when normally correlated signals (e.g., pressure and temperature) start to diverge, indicating process changes or sensor issues. Also useful for validating sensor redundancy and identifying leading indicators.

---

## Quick Example

```python
from ts_shape.events.correlation.signal_correlation import SignalCorrelationEvents

correlator = SignalCorrelationEvents(
    df=process_df,
    timestamp_col="timestamp",
    value_col="pressure",
    second_value_col="temperature"
)

# Rolling Pearson correlation between pressure and temperature
rolling = correlator.rolling_correlation(window="4H")

# Find periods where the correlation breaks down
breakdowns = correlator.correlation_breakdown(
    window="4H", threshold=0.5, min_duration="2H"
)
print(f"Found {len(breakdowns)} correlation breakdown periods")

# Cross-correlation with time lag to find leading indicators
lag_corr = correlator.lag_correlation(max_lag="30T", step="5T")
best_lag = lag_corr.loc[lag_corr["correlation"].idxmax()]
print(f"Best lag: {best_lag['lag']} with r={best_lag['correlation']:.3f}")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `rolling_correlation()` | Rolling Pearson correlation over time | DataFrame with correlation coefficient per window |
| `correlation_breakdown()` | Periods where correlation drops below threshold | DataFrame of breakdown intervals with duration |
| `lag_correlation()` | Cross-correlation with time lag | DataFrame of correlation values at each lag offset |

---

## Tips & Hints

!!! tip "Use lag correlation to find leading indicators"
    `lag_correlation()` can reveal that one signal leads another by a fixed delay. This is valuable for building early warning systems where an upstream variable predicts a downstream change.

!!! info "Related modules"
    - [`AnomalyCorrelationEvents`](anomaly-correlation.md) - Correlate detected anomalies across signals instead of raw values
    - [`DegradationDetectionEvents`](../maintenance/degradation-detection.md) - Detect degradation when correlated signals start diverging
    - [`EnergyEfficiencyEvents`](../energy/efficiency-tracking.md) - Correlate process variables with energy efficiency

---

## See Also

- [Statistics Guide](../../guides/statistics.md)
- [API Reference](../../reference/ts_shape/events/correlation/signal_correlation/)
