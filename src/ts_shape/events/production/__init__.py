"""Production Events

Detectors for production events in long-form timeseries (uuid-per-signal).

Classes:
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
"""

from .machine_state import MachineStateEvents  # re-export
from .line_throughput import LineThroughputEvents  # re-export
from .changeover import ChangeoverEvents  # re-export
from .flow_constraints import FlowConstraintEvents  # re-export

__all__ = [
    "MachineStateEvents",
    "LineThroughputEvents",
    "ChangeoverEvents",
    "FlowConstraintEvents",
]
