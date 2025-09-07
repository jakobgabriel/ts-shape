"""Time-Grouped Statistics

Aggregations over fixed time windows (e.g., hourly/daily) for numeric values.

Classes:
- TimeGroupedStatistics: Time-windowed aggregations for numeric series.
  - calculate_statistic: Single aggregation per window (mean/sum/min/max/diff/range).
  - calculate_statistics: Multiple aggregations merged.
  - calculate_custom_func: Apply a custom aggregation per window.
"""
