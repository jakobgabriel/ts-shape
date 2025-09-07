"""Quality Events

Detectors for quality-related events: outliers, statistical process control,
and tolerance deviations over time series.

Classes:
- OutlierDetectionEvents: Detect and group outlier events in a time series.
  - detect_outliers_zscore: Detect outliers using Z-score thresholding and group nearby points.
  - detect_outliers_iqr: Detect outliers using IQR bounds and group nearby points.

- StatisticalProcessControlRuleBased: Apply Western Electric rules to actual values
  using tolerance context to flag control-limit violations.
  - calculate_control_limits: Compute mean and ±1/±2/±3 standard-deviation bands from tolerance rows.
  - process: Apply selected rules and emit event rows for violations.
  - rule_1: One point beyond the 3-sigma control limits.
  - rule_2: Nine consecutive points on one side of the mean.
  - rule_3: Six consecutive points steadily increasing or decreasing.
  - rule_4: Fourteen consecutive points alternating up and down.
  - rule_5: Two of three consecutive points near the control limit (between 2 and 3 sigma).
  - rule_6: Four of five consecutive points near the control limit (between 1 and 2 sigma).
  - rule_7: Fifteen consecutive points within 1 sigma of the mean.
  - rule_8: Eight consecutive points on both sides of the mean within 1 sigma.

- ToleranceDeviationEvents: Flag intervals where actual values cross/compare against
  tolerance settings and group them into start/end events.
  - process_and_group_data_with_events: Build grouped deviation events with event UUIDs.
"""
