# Tolerance Deviation Enhancements

## Overview
The `/home/user/ts-shape/src/ts_shape/events/quality/tolerance_deviation.py` file has been enhanced with advanced quality control features while maintaining full backward compatibility.

## New Features

### 1. Separate Upper and Lower Tolerances
**Parameters Added:**
- `upper_tolerance_uuid`: UUID for upper tolerance limit
- `lower_tolerance_uuid`: UUID for lower tolerance limit

**Usage:**
```python
# New way - separate tolerances
events = ToleranceDeviationEvents(
    dataframe=df,
    tolerance_column='tolerance',
    actual_column='measurement',
    actual_uuid='measurement-uuid',
    event_uuid='event-uuid',
    upper_tolerance_uuid='upper-tol-uuid',
    lower_tolerance_uuid='lower-tol-uuid'
)

# Old way - still works (backward compatibility)
events = ToleranceDeviationEvents(
    dataframe=df,
    tolerance_column='tolerance',
    actual_column='measurement',
    tolerance_uuid='tolerance-uuid',
    actual_uuid='measurement-uuid',
    event_uuid='event-uuid'
)
```

### 2. Warning Zones
**Parameter Added:**
- `warning_threshold`: float = 0.8 (default 80% of tolerance triggers warning)

Allows setting a configurable threshold for early warning detection before reaching full tolerance limits.

**Usage:**
```python
events = ToleranceDeviationEvents(
    dataframe=df,
    tolerance_column='tolerance',
    actual_column='measurement',
    tolerance_uuid='tolerance-uuid',
    actual_uuid='measurement-uuid',
    event_uuid='event-uuid',
    warning_threshold=0.75  # 75% threshold for warnings
)
```

### 3. Deviation Magnitude Tracking
**Columns Added to Output:**
- `deviation_abs`: Absolute deviation from tolerance boundary
- `deviation_pct`: Percentage deviation relative to tolerance range

These columns are automatically added to the output DataFrame, providing quantitative measures of how far measurements deviate from acceptable limits.

### 4. Severity Level Classification
**Severity Column Added:**
A new `severity` column is added to the output with three levels:

- **'minor'**: Within warning threshold (≤ 80% of tolerance by default)
- **'major'**: Beyond tolerance but not critical (< 2x tolerance range)
- **'critical'**: Way beyond tolerance (≥ 2x tolerance range)

The severity calculation is handled by the `_calculate_severity()` method.

### 5. Process Capability Indices
**New Method:** `compute_capability_indices(target_value: Optional[float] = None)`

Calculates industry-standard process capability metrics:

- **Cp**: Process capability (potential capability)
- **Cpk**: Process capability index (accounts for centering)
- **Pp**: Process performance (overall variability)
- **Ppk**: Process performance index (accounts for centering)

**Returns:**
```python
{
    'Cp': 1.45,
    'Cpk': 1.33,
    'Pp': 1.45,
    'Ppk': 1.33,
    'mean': 10.05,
    'std': 0.15,
    'usl': 10.5,  # Upper Specification Limit
    'lsl': 9.5,   # Lower Specification Limit
    'target': 10.0
}
```

**Interpretation:**
- Values > 1.33: Acceptable process
- Values > 1.67: Good process
- Values < 1.0: Process needs improvement

**Usage:**
```python
events = ToleranceDeviationEvents(...)
capability = events.compute_capability_indices(target_value=10.0)
print(f"Process Capability (Cpk): {capability['Cpk']}")
```

### 6. Time-Lagged Tolerance
**Parameter Added:**
- `tolerance_lag`: str = '0s' (default no lag)

Allows delayed application of tolerance values, useful for processes where tolerance changes need time to take effect.

**Usage:**
```python
events = ToleranceDeviationEvents(
    dataframe=df,
    tolerance_column='tolerance',
    actual_column='measurement',
    tolerance_uuid='tolerance-uuid',
    actual_uuid='measurement-uuid',
    event_uuid='event-uuid',
    tolerance_lag='5min'  # Apply tolerance after 5-minute delay
)
```

### 7. Backward Compatibility
All existing code continues to work without modification:

```python
# This still works exactly as before
events = ToleranceDeviationEvents(
    dataframe=df,
    tolerance_column='tolerance',
    actual_column='measurement',
    tolerance_uuid='tolerance-uuid',
    actual_uuid='measurement-uuid',
    event_uuid='event-uuid',
    compare_func=operator.ge,
    time_threshold='5min'
)

result = events.process_and_group_data_with_events()
```

## Implementation Details

### Architecture Changes
The enhancement maintains a clean separation between:

1. **Single tolerance mode** (`_process_single_tolerance()`) - for backward compatibility
2. **Separate tolerances mode** (`_process_separate_tolerances()`) - for new functionality

The class automatically selects the appropriate processing mode based on initialization parameters.

### Helper Methods
- `_apply_tolerance_lag()`: Handles time-lagged tolerance application
- `_calculate_severity()`: Computes severity levels based on deviation magnitude

### Output Enhancements
The `process_and_group_data_with_events()` method now returns DataFrames with additional columns:
- `deviation_abs`: Absolute deviation value
- `deviation_pct`: Percentage deviation
- `severity`: Classification level (minor/major/critical)

## Example Usage

```python
import pandas as pd
from ts_shape.events.quality.tolerance_deviation import ToleranceDeviationEvents

# Create sample data
df = pd.DataFrame({
    'systime': pd.date_range('2024-01-01', periods=100, freq='1min'),
    'uuid': ['measurement-uuid'] * 100,
    'measurement': np.random.normal(10, 0.2, 100),
    'tolerance': [10.5] * 100,
    'is_delta': [True] * 100
})

# Initialize with enhanced features
events = ToleranceDeviationEvents(
    dataframe=df,
    tolerance_column='tolerance',
    actual_column='measurement',
    upper_tolerance_uuid='upper-tol-uuid',
    lower_tolerance_uuid='lower-tol-uuid',
    actual_uuid='measurement-uuid',
    event_uuid='deviation-event-uuid',
    warning_threshold=0.8,
    tolerance_lag='2min'
)

# Process events with enhanced metrics
result = events.process_and_group_data_with_events()

# Calculate capability indices
capability = events.compute_capability_indices(target_value=10.0)
print(f"Cpk: {capability['Cpk']}")
print(f"Process Mean: {capability['mean']}")

# Analyze results
print(f"Events with major severity: {len(result[result['severity'] == 'major'])}")
print(f"Events with critical severity: {len(result[result['severity'] == 'critical'])}")
print(f"Average deviation: {result['deviation_pct'].mean():.2f}%")
```

## Benefits

1. **Enhanced Quality Control**: Multiple severity levels and warning zones enable proactive quality management
2. **Better Analytics**: Deviation tracking provides quantitative insights into process performance
3. **Industry Standards**: Capability indices align with Six Sigma and statistical process control practices
4. **Flexibility**: Separate tolerances and time lags accommodate complex manufacturing scenarios
5. **Backward Compatible**: Existing code requires no changes
6. **Comprehensive Metrics**: Full suite of quality metrics in a single analysis

## Technical Notes

- All numeric outputs are rounded to 4 decimal places for consistency
- The class handles edge cases (division by zero, missing data) gracefully
- Time lag uses pandas timedelta for precise time-based calculations
- Severity calculation accounts for both warning thresholds and critical deviations
- Capability indices follow standard Six Sigma formulas (6σ for Cp, 3σ for Cpk)
