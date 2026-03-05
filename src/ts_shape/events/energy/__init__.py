"""Energy Events

Detectors for energy-related patterns: consumption analysis, efficiency
tracking, and peak demand detection on manufacturing/industrial IoT time
series data.

Classes:
- EnergyConsumptionEvents: Analyze energy consumption patterns.
  - consumption_by_window: Aggregate energy consumption per time window.
  - peak_demand_detection: Detect peak demand periods exceeding thresholds.
  - consumption_baseline_deviation: Compare actual vs baseline consumption.
  - energy_per_unit: Calculate energy consumption per production unit.

- EnergyEfficiencyEvents: Track energy efficiency metrics.
  - efficiency_trend: Rolling efficiency metric over time.
  - idle_energy_waste: Detect energy consumption during idle periods.
  - specific_energy_consumption: Energy per unit output over time.
  - efficiency_comparison: Compare efficiency across shifts or periods.
"""

from .consumption_analysis import EnergyConsumptionEvents
from .efficiency_tracking import EnergyEfficiencyEvents

__all__ = [
    "EnergyConsumptionEvents",
    "EnergyEfficiencyEvents",
]
