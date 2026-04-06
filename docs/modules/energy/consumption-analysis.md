# EnergyConsumptionEvents

> Analyze energy consumption patterns from meter/sensor signals.

**Module:** `ts_shape.events.energy.consumption_analysis`
**Guide:** [Production Guide](../../guides/production.md)

---

## When to Use

Use for energy management and ISO 50001 compliance. Tracks consumption patterns, identifies peak demand periods, and calculates specific energy consumption per unit produced. Works with utility meter data, sub-meter readings, or any cumulative/instantaneous power signal.

---

## Quick Example

```python
from ts_shape.events.energy.consumption_analysis import EnergyConsumptionEvents

energy = EnergyConsumptionEvents(
    df=meter_df,
    timestamp_col="timestamp",
    value_col="power_kw"
)

# Aggregate consumption per shift
consumption = energy.consumption_by_window(window="8H", agg="sum")

# Find peak demand periods
peaks = energy.peak_demand_detection(window="15T", top_n=10)
print(f"Highest peak: {peaks.iloc[0]['peak_kw']:.1f} kW")

# Compare actual vs baseline consumption
deviations = energy.consumption_baseline_deviation(
    baseline_col="expected_kw", threshold_pct=15.0
)

# Energy per production unit (requires production count column)
epu = energy.energy_per_unit(production_col="units_produced", window="1D")
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `consumption_by_window()` | Aggregate consumption per time window | DataFrame with total/mean consumption per window |
| `peak_demand_detection()` | Identify peak demand periods | DataFrame of top-N peak demand windows |
| `consumption_baseline_deviation()` | Actual vs baseline comparison | DataFrame of periods exceeding deviation threshold |
| `energy_per_unit()` | Energy per production unit | DataFrame with specific energy consumption per window |

---

## Tips & Hints

!!! tip "Align windows with shift boundaries"
    Use window sizes that match your operational shifts (e.g., `"8H"` for 8-hour shifts). Misaligned windows split consumption across shifts and obscure real patterns.

!!! info "Related modules"
    - [`EnergyEfficiencyEvents`](efficiency-tracking.md) - Track efficiency trends and idle energy waste
    - [`InventoryMonitoringEvents`](../supplychain/inventory-monitoring.md) - Correlate energy use with production output
    - [`DemandPatternEvents`](../supplychain/demand-patterns.md) - Demand patterns that drive energy consumption

---

## See Also

- [Production Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/energy/consumption_analysis/)
