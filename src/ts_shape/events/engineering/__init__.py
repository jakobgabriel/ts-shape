"""Engineering Events

Detectors for engineering-related patterns over shaped timeseries.

Classes:
- SetpointChangeEvents: Detect setpoint changes and compute response KPIs.
  - detect_setpoint_steps: Point events where |Δsetpoint| ≥ min_delta and holds for min_hold.
  - detect_setpoint_ramps: Intervals where |dS/dt| ≥ min_rate for at least min_duration.
  - detect_setpoint_changes: Unified table of steps and ramps with standardized columns.
  - time_to_settle: Time until |actual − setpoint| ≤ tol for a hold duration within a window.
  - overshoot_metrics: Peak overshoot magnitude/percent and time-to-peak after a change.

- StartupDetectionEvents: Detect startup intervals from thresholds or slope.
  - detect_startup_by_threshold: Rising threshold crossing with minimum dwell above threshold.
  - detect_startup_by_slope: Intervals with sustained positive slope ≥ min_slope for min_duration.

- ThresholdMonitoringEvents: Multi-level threshold monitoring with hysteresis.
  - multi_level_threshold: Intervals exceeding warning/alarm/critical levels.
  - threshold_with_hysteresis: Alarm entry/exit with separate high/low thresholds.
  - time_above_threshold: Time and percentage above threshold per window.
  - threshold_exceedance_trend: Track exceedance frequency over time.

- RateOfChangeEvents: Detect rapid changes and step jumps.
  - detect_rapid_change: Flag intervals where rate exceeds threshold.
  - rate_statistics: Per-window rate of change statistics.
  - detect_step_changes: Sudden value jumps within a short duration.
"""

from .setpoint_events import SetpointChangeEvents  # re-export
from .startup_events import StartupDetectionEvents  # re-export
from .threshold_monitoring import ThresholdMonitoringEvents  # re-export
from .rate_of_change import RateOfChangeEvents  # re-export

__all__ = [
    "SetpointChangeEvents",
    "StartupDetectionEvents",
    "ThresholdMonitoringEvents",
    "RateOfChangeEvents",
]
