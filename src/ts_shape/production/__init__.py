"""Daily production tracking and reporting modules.

Simple, practical tools for everyday manufacturing needs:
- Production tracking by part number
- Cycle time analysis by part number
- Shift-based reporting

Example usage:
    from ts_shape.production import PartProductionTracking, CycleTimeTracking, ShiftReporting

    # Track production by part
    tracker = PartProductionTracking(df)
    hourly_prod = tracker.production_by_part('part_id_uuid', 'counter_uuid', window='1h')

    # Analyze cycle times
    cycle_tracker = CycleTimeTracking(df)
    stats = cycle_tracker.cycle_time_statistics('part_id_uuid', 'cycle_trigger_uuid')

    # Shift reports
    shift_reporter = ShiftReporting(df)
    shift_prod = shift_reporter.shift_production('counter_uuid')
"""

from ts_shape.production.part_tracking import PartProductionTracking
from ts_shape.production.cycle_time_tracking import CycleTimeTracking
from ts_shape.production.shift_reporting import ShiftReporting

__all__ = [
    "PartProductionTracking",
    "CycleTimeTracking",
    "ShiftReporting",
]
