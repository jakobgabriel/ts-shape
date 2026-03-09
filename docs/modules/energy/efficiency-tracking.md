# EnergyEfficiencyEvents

> Track energy efficiency metrics against production and machine state.

**Module:** `ts_shape.events.energy.efficiency_tracking`
**Guide:** [Production Guide](../../guides/production.md)

---

## When to Use

Use to track energy efficiency over time and identify waste. Detects energy consumed during idle periods and compares efficiency across shifts or production runs. Essential for continuous improvement programs targeting energy reduction.

---

## Quick Example

```python
from ts_shape.events.energy.efficiency_tracking import EnergyEfficiencyEvents

tracker = EnergyEfficiencyEvents(
    df=production_df,
    timestamp_col="timestamp",
    value_col="power_kw"
)

# Rolling energy efficiency (output per kWh)
trend = tracker.efficiency_trend(
    production_col="units_produced", window="1D"
)

# Detect energy waste during idle periods
waste = tracker.idle_energy_waste(
    state_col="machine_state", idle_value="IDLE", window="1H"
)
print(f"Total idle waste: {waste['waste_kwh'].sum():.1f} kWh")

# Specific energy consumption per period
sec = tracker.specific_energy_consumption(
    production_col="units_produced", window="1D"
)

# Compare efficiency across shifts
comparison = tracker.efficiency_comparison(
    group_col="shift", production_col="units_produced"
)
```

---

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `efficiency_trend()` | Rolling energy efficiency over time | DataFrame with efficiency (units/kWh) per window |
| `idle_energy_waste()` | Energy consumed during idle periods | DataFrame of idle intervals with wasted energy |
| `specific_energy_consumption()` | SEC (kWh per unit) per period | DataFrame with SEC per window |
| `efficiency_comparison()` | Compare efficiency across groups | DataFrame with efficiency stats per group |

---

## Tips & Notes

!!! tip "Track idle waste to find quick wins"
    `idle_energy_waste()` often reveals the lowest-hanging fruit for energy savings. Machines left running during breaks or changeovers can account for 10-20% of total consumption.

!!! info "Related modules"
    - [`EnergyConsumptionEvents`](consumption-analysis.md) - Raw consumption analysis and peak demand detection
    - [`SignalCorrelationEvents`](../correlation/signal-correlation.md) - Correlate efficiency changes with process variables

---

## See Also

- [Production Guide](../../guides/production.md)
- [API Reference](../../reference/ts_shape/events/energy/efficiency_tracking/)
