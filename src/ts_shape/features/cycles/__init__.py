"""Cycles

Utilities to detect and process cycles in timeseries.

Classes:
- CycleExtractor: Build cycles from state/step/value changes.
  - process_persistent_cycle: True stretches define cycles.
  - process_trigger_cycle: True-to-False transition defines a cycle end.
  - process_separate_start_end_cycle: Separate starts and ends signals.
  - process_step_sequence: Start/end steps in integer values.
  - process_state_change_cycle: Sequential rows define boundaries.
  - process_value_change_cycle: Any value change defines a boundary.

- CycleDataProcessor: Split/merge/group by cycle windows.
  - split_by_cycle: Split values by cycle ranges.
  - merge_dataframes_by_cycle: Annotate values with cycle UUIDs.
  - group_by_cycle_uuid: Group values by cycle key.
  - split_dataframes_by_group: Further split by column groupings.
"""
