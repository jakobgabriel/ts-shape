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

OEE and Advanced Analytics:
- OEECalculator: Overall Equipment Effectiveness (Availability x Performance x Quality).
  - calculate_availability: Availability % from run/idle intervals.
  - calculate_performance: Actual vs ideal throughput.
  - calculate_quality: Good parts / total parts.
  - calculate_oee: Combined daily OEE metric.

- AlarmManagementEvents: ISA-18.2 style alarm analysis.
  - alarm_frequency: Alarm activations per time window.
  - alarm_duration_stats: Min/avg/max/total duration of alarm ON states.
  - chattering_detection: Detect nuisance chattering alarms.
  - standing_alarms: Identify alarms that stay active too long.

- BatchTrackingEvents: Batch/recipe production tracking.
  - detect_batches: Detect batch start/end from value changes.
  - batch_duration_stats: Duration statistics per batch type.
  - batch_yield: Production quantity per batch.
  - batch_transition_matrix: Batch-to-batch transition frequencies.

- BottleneckDetectionEvents: Identify production line bottlenecks.
  - station_utilization: Per-station uptime percentage per window.
  - detect_bottleneck: Identify bottleneck station per window.
  - shifting_bottleneck: Track when the bottleneck moves.
  - throughput_constraint_summary: Summary statistics.

- MicroStopEvents: Detect brief idle intervals that accumulate into losses.
  - detect_micro_stops: Find idle intervals shorter than max_duration.
  - micro_stop_frequency: Count micro-stops per window.
  - micro_stop_impact: Time lost to micro-stops per window.
  - micro_stop_patterns: Group micro-stops by hour-of-day.

- DutyCycleEvents: Analyze on/off patterns from boolean signals.
  - duty_cycle_per_window: On-time percentage per window.
  - on_off_intervals: List every on/off interval with duration.
  - cycle_count: Transition counts per window.
  - excessive_cycling: Flag windows with too many transitions.
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

# OEE and Advanced Analytics
from .oee_calculator import OEECalculator
from .alarm_management import AlarmManagementEvents
from .batch_tracking import BatchTrackingEvents
from .bottleneck_detection import BottleneckDetectionEvents
from .micro_stop_detection import MicroStopEvents
from .duty_cycle import DutyCycleEvents

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
    # OEE and Advanced Analytics
    "OEECalculator",
    "AlarmManagementEvents",
    "BatchTrackingEvents",
    # Bottleneck, Micro-Stop, and Duty Cycle Analysis
    "BottleneckDetectionEvents",
    "MicroStopEvents",
    "DutyCycleEvents",
]
