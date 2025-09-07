"""Features

Feature extraction and summarization utilities for shaped timeseries.

Classes:
- NumericStatistics: Compute descriptive statistics for numeric columns.
  - column_mean: Mean of a column.
  - column_median: Median of a column.
  - column_std: Standard deviation of a column.
  - column_variance: Variance of a column.
  - column_min: Minimum value.
  - column_max: Maximum value.
  - column_sum: Sum of values.
  - column_kurtosis: Kurtosis of values.
  - column_skewness: Skewness of values.
  - column_quantile: Quantile of a column.
  - column_iqr: Interquartile range.
  - column_range: Range (max - min).
  - column_mad: Mean absolute deviation.
  - coefficient_of_variation: Standard deviation divided by mean (guarded).
  - standard_error_mean: Standard error of the mean.
  - describe: Pandas describe wrapper.
  - summary_as_dict: Comprehensive numeric summary as dict.
  - summary_as_dataframe: Comprehensive numeric summary as DataFrame.

- StringStatistics: String-based statistics for categorical/text columns.
  - count_unique: Number of unique strings.
  - most_frequent: Most frequent string.
  - count_most_frequent: Count of the most frequent string.
  - count_null: Number of nulls.
  - average_string_length: Average length of non-null strings.
  - longest_string: Longest string.
  - shortest_string: Shortest string.
  - string_length_summary: Summary of lengths.
  - most_common_n_strings: Top-N most frequent strings.
  - contains_substring_count: Count of strings containing a substring.
  - starts_with_count: Count of strings starting with a prefix.
  - ends_with_count: Count of strings ending with a suffix.
  - uppercase_percentage: Percentage of uppercase strings.
  - lowercase_percentage: Percentage of lowercase strings.
  - contains_digit_count: Count of strings containing digits.
  - summary_as_dict: Comprehensive string summary as dict.
  - summary_as_dataframe: Comprehensive string summary as DataFrame.

- BooleanStatistics: Boolean column statistics.
  - count_true: Count of True values.
  - count_false: Count of False values.
  - count_null: Count of nulls.
  - count_not_null: Count of non-nulls.
  - true_percentage: Percentage True.
  - false_percentage: Percentage False.
  - mode: Most common boolean value.
  - is_balanced: Whether distribution is 50/50.
  - summary_as_dict: Summary as dict.
  - summary_as_dataframe: Summary as DataFrame.

- TimestampStatistics: Timestamp distributions and ranges.
  - count_null: Count of null timestamps.
  - count_not_null: Count of non-null timestamps.
  - earliest_timestamp: Earliest timestamp.
  - latest_timestamp: Latest timestamp.
  - timestamp_range: Time range (latest - earliest).
  - most_frequent_timestamp: Most frequent timestamp.
  - count_most_frequent_timestamp: Count of the modal timestamp.
  - year_distribution: Distribution by year.
  - month_distribution: Distribution by month.
  - weekday_distribution: Distribution by weekday.
  - hour_distribution: Distribution by hour.
  - most_frequent_day: Most frequent weekday.
  - most_frequent_hour: Most frequent hour.
  - average_time_gap: Average gap between consecutive timestamps.
  - median_timestamp: Median timestamp.
  - standard_deviation_timestamps: Standard deviation of consecutive differences.
  - timestamp_quartiles: 25th/50th/75th percentiles.
  - days_with_most_activity: Top-N active days.

- TimeGroupedStatistics: Time-windowed aggregations for numeric series.
  - calculate_statistic: Single aggregation per window (mean/sum/min/max/diff/range).
  - calculate_statistics: Multiple aggregations merged.
  - calculate_custom_func: Apply a custom aggregation per window.

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
