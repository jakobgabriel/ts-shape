"""Daily production tracking and reporting modules.

Simple, practical tools for everyday manufacturing needs:
- Production tracking by part number
- Cycle time analysis by part number
- Shift-based reporting
- Downtime tracking and availability
- Quality and NOK (defective parts) tracking

Example usage:
    from ts_shape.production import (
        PartProductionTracking,
        CycleTimeTracking,
        ShiftReporting,
        DowntimeTracking,
        QualityTracking,
    )

    # Track production by part
    tracker = PartProductionTracking(df)
    hourly_prod = tracker.production_by_part('part_id_uuid', 'counter_uuid', window='1h')

    # Analyze cycle times
    cycle_tracker = CycleTimeTracking(df)
    stats = cycle_tracker.cycle_time_statistics('part_id_uuid', 'cycle_trigger_uuid')

    # Shift reports
    shift_reporter = ShiftReporting(df)
    shift_prod = shift_reporter.shift_production('counter_uuid')

    # Downtime analysis
    downtime_tracker = DowntimeTracking(df)
    shift_downtime = downtime_tracker.downtime_by_shift('state_uuid', running_value='Running')

    # Quality tracking
    quality_tracker = QualityTracking(df)
    nok_by_shift = quality_tracker.nok_by_shift('ok_counter', 'nok_counter')
"""

from ts_shape.production.part_tracking import PartProductionTracking
from ts_shape.production.cycle_time_tracking import CycleTimeTracking
from ts_shape.production.shift_reporting import ShiftReporting
from ts_shape.production.downtime_tracking import DowntimeTracking
from ts_shape.production.quality_tracking import QualityTracking

__all__ = [
    "PartProductionTracking",
    "CycleTimeTracking",
    "ShiftReporting",
    "DowntimeTracking",
    "QualityTracking",
]
