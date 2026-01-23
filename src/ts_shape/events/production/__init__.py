"""Production Events and Tracking

This module contains both event detection and daily tracking tools for production:

Event Detection Classes:
- MachineStateEvents: Run/idle intervals and transition points from a boolean state signal.
  - detect_run_idle: Intervalize run/idle with optional min duration.
  - transition_events: Point events on idle→run and run→idle changes.

- LineThroughputEvents: Throughput metrics and takt adherence.
  - count_parts: Parts per fixed window from a counter uuid.
  - takt_adherence: Cycle time violations vs. a takt time.

- ChangeoverEvents: Product/recipe changes and end-of-changeover derivation.
  - detect_changeover: Point events at product value changes.
  - changeover_window: End via fixed window or stable band metrics.

- FlowConstraintEvents: Blocked/starved intervals between upstream/downstream run signals.
  - blocked_events: Upstream running while downstream not consuming.
  - starved_events: Downstream running while upstream not supplying.

Daily Production Tracking Classes:
- PartProductionTracking: Track production quantities by part number.
  - production_by_part: Production quantity per time window.
  - daily_production_summary: Daily totals by part.
  - production_totals: Totals over date ranges.

- CycleTimeTracking: Analyze cycle times by part number.
  - cycle_time_by_part: Calculate cycle times.
  - cycle_time_statistics: Statistical analysis (min/avg/max/std).
  - detect_slow_cycles: Anomaly detection.
  - cycle_time_trend: Trend analysis.

- ShiftReporting: Shift-based performance analysis.
  - shift_production: Production per shift.
  - shift_comparison: Compare shift performance.
  - shift_targets: Target vs actual analysis.
  - best_and_worst_shifts: Performance ranking.

- DowntimeTracking: Machine availability and downtime analysis.
  - downtime_by_shift: Downtime and availability per shift.
  - downtime_by_reason: Root cause analysis.
  - top_downtime_reasons: Pareto analysis (80/20 rule).
  - availability_trend: Track availability over time.

- QualityTracking: NOK (defective parts) and quality metrics.
  - nok_by_shift: NOK parts and First Pass Yield per shift.
  - quality_by_part: Quality metrics by part number.
  - nok_by_reason: Defect type analysis.
  - daily_quality_summary: Daily quality rollup.
"""

# Event Detection Classes
from .machine_state import MachineStateEvents
from .line_throughput import LineThroughputEvents
from .changeover import ChangeoverEvents
from .flow_constraints import FlowConstraintEvents

# Daily Production Tracking Classes
from .part_tracking import PartProductionTracking
from .cycle_time_tracking import CycleTimeTracking
from .shift_reporting import ShiftReporting
from .downtime_tracking import DowntimeTracking
from .quality_tracking import QualityTracking

__all__ = [
    # Event Detection
    "MachineStateEvents",
    "LineThroughputEvents",
    "ChangeoverEvents",
    "FlowConstraintEvents",
    # Daily Production Tracking
    "PartProductionTracking",
    "CycleTimeTracking",
    "ShiftReporting",
    "DowntimeTracking",
    "QualityTracking",
]
