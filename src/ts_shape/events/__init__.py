"""Events

Extract events from shaped timeseries across quality, maintenance, and
production domains.

Classes:
- OutlierDetectionEvents: Detect and group outlier events in a time series.
  - detect_outliers_zscore: Detect outliers using Z-score thresholding and group nearby points.
  - detect_outliers_iqr: Detect outliers using IQR bounds and group nearby points.

- StatisticalProcessControlRuleBased: Apply Western Electric rules to flag
  control-limit violations on actual values using tolerance context.
  - calculate_control_limits: Compute mean and ±1/±2/±3 standard-deviation bands from tolerance rows.
  - process: Apply selected rules and emit event rows for violations.

- ToleranceDeviationEvents: Flag intervals where actual values cross configured
  tolerance and group them into start/end events.
  - process_and_group_data_with_events: Build grouped deviation events with event UUIDs.
"""
