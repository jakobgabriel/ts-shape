# Startup Detection Enhancements

This document describes the enhancements made to `/home/user/ts-shape/src/ts_shape/events/engineering/startup_events.py`.

## Overview

The `StartupDetectionEvents` class has been enhanced with five new powerful methods for advanced startup detection, quality assessment, and failure analysis while maintaining full backward compatibility with existing methods.

## New Features

### 1. Multi-Signal Startup Detection

**Method:** `detect_startup_multi_signal(signals: Dict[str, Dict], logic: str = 'all', time_tolerance: str = '30s')`

Detect startups based on multiple signals with configurable AND/OR logic.

#### Parameters:
- **signals**: Dict mapping uuid to detection config. Each config contains:
  - `method`: 'threshold' or 'slope'
  - For threshold: `threshold`, optional `hysteresis`, `min_above`
  - For slope: `min_slope`, optional `slope_window`, `min_duration`
- **logic**: 'all' (AND - all signals must detect) or 'any' (OR - at least one)
- **time_tolerance**: Maximum time difference between signals for 'all' logic

#### Returns:
DataFrame with columns: `start`, `end`, `uuid`, `is_delta`, `method`, `signals_triggered`, `signal_details`

#### Example:
```python
detector = StartupDetectionEvents(df, target_uuid='temp_sensor')

signals = {
    'temperature_sensor': {
        'method': 'threshold',
        'threshold': 40.0,
        'min_above': '10s',
    },
    'motor_speed': {
        'method': 'threshold',
        'threshold': 50.0,
        'min_above': '5s',
    },
}

# All signals must detect (AND logic)
events = detector.detect_startup_multi_signal(signals, logic='all', time_tolerance='30s')

# Any signal can detect (OR logic)
events = detector.detect_startup_multi_signal(signals, logic='any')
```

#### Use Cases:
- Correlating multiple sensor readings for robust startup detection
- Requiring unanimous agreement from sensors (safety-critical applications)
- Detecting startups from any of several redundant sensors

---

### 2. Adaptive Threshold Detection

**Method:** `detect_startup_adaptive(baseline_window: str = '1h', sensitivity: float = 2.0, min_above: str = '10s', lookback_periods: int = 5)`

Detect startups using adaptive thresholds calculated from historical baseline data.

#### Parameters:
- **baseline_window**: Window size for calculating baseline statistics
- **sensitivity**: Multiplier for standard deviation (threshold = mean + sensitivity × std)
- **min_above**: Minimum time the value must stay above threshold
- **lookback_periods**: Number of baseline periods to use for statistics

#### Returns:
DataFrame with columns: `start`, `end`, `uuid`, `is_delta`, `method`, `adaptive_threshold`, `baseline_mean`, `baseline_std`

#### Example:
```python
detector = StartupDetectionEvents(df, target_uuid='temperature_sensor')

events = detector.detect_startup_adaptive(
    baseline_window='1h',
    sensitivity=2.0,
    min_above='15s',
    lookback_periods=10,
)
```

#### How It Works:
1. Calculates rolling mean and standard deviation over lookback periods
2. Computes adaptive threshold: `threshold = mean + sensitivity × std`
3. Detects when signal crosses above this dynamic threshold
4. Validates by ensuring signal stays above threshold for `min_above` duration

#### Use Cases:
- Environments with varying baseline conditions (seasonal, time-of-day effects)
- Systems where fixed thresholds are impractical
- Automatic calibration to changing operational conditions
- Reducing false positives in noisy environments

---

### 3. Startup Quality Assessment

**Method:** `assess_startup_quality(startup_events: pd.DataFrame, smoothness_window: int = 5, anomaly_threshold: float = 3.0)`

Assess the quality of detected startup events.

#### Parameters:
- **startup_events**: DataFrame of detected startup events (must have 'start' and 'end' columns)
- **smoothness_window**: Window size for calculating smoothness metrics
- **anomaly_threshold**: Z-score threshold for detecting anomalies

#### Returns:
DataFrame with quality metrics:
- **duration**: Total duration of startup
- **smoothness_score**: Inverse of derivative variance (0-1, higher = smoother)
- **anomaly_flags**: Number of anomalous points detected
- **value_change**: Total change in value during startup
- **avg_rate**: Average rate of change
- **max_value**: Maximum value reached
- **stability_score**: Measure of final state stability (0-1, higher = more stable)

#### Example:
```python
detector = StartupDetectionEvents(df, target_uuid='temperature_sensor')

# First detect startups
events = detector.detect_startup_by_threshold(threshold=40.0, min_above='10s')

# Assess quality
quality = detector.assess_startup_quality(
    events,
    smoothness_window=5,
    anomaly_threshold=3.0,
)

# Identify high-quality startups
good_startups = quality[
    (quality['smoothness_score'] > 0.7) &
    (quality['anomaly_flags'] == 0) &
    (quality['stability_score'] > 0.8)
]
```

#### Quality Metrics Explained:

**Smoothness Score:**
- Calculated as: `1 / (1 + variance_of_derivatives)`
- Range: 0 to 1 (higher is better)
- Measures how smooth the startup transition is
- Low scores indicate jerky or unstable startups

**Stability Score:**
- Based on coefficient of variation in final 20% of startup
- Range: 0 to 1 (higher is better)
- Measures how stable the final operating state is
- Useful for identifying startups that reach but don't maintain target

**Anomaly Flags:**
- Count of data points exceeding anomaly_threshold standard deviations
- Identifies unusual spikes or dips during startup
- Zero anomalies indicates a clean, predictable startup

#### Use Cases:
- Maintenance prediction (degraded startup quality signals equipment issues)
- Process optimization (comparing startup profiles)
- Quality control and compliance reporting
- Training data curation for machine learning models

---

### 4. Startup Phase Tracking

**Method:** `track_startup_phases(phases: List[Dict], min_phase_duration: str = '5s')`

Track progression through defined startup phases.

#### Parameters:
- **phases**: List of phase definitions, each containing:
  - `name`: Phase name
  - `condition`: 'threshold', 'range', or 'slope'
  - For 'threshold': `min_value` (value must be >= min_value)
  - For 'range': `min_value` and `max_value` (value in range)
  - For 'slope': `min_slope` (slope must be >= min_slope)
- **min_phase_duration**: Minimum time to stay in phase to be considered valid

#### Returns:
DataFrame with phase transitions:
- **phase_name**: Name of the phase
- **phase_number**: Sequential phase number (0-indexed)
- **start**: Phase start time
- **end**: Phase end time
- **duration**: Time spent in phase
- **next_phase**: Name of the next phase (None for last phase)
- **completed**: Whether full startup sequence completed

#### Example:
```python
detector = StartupDetectionEvents(df, target_uuid='temperature_sensor')

# Define startup phases
phases = [
    {
        'name': 'Warmup',
        'condition': 'range',
        'min_value': 20,
        'max_value': 40,
    },
    {
        'name': 'Heating',
        'condition': 'range',
        'min_value': 40,
        'max_value': 70,
    },
    {
        'name': 'Operating',
        'condition': 'threshold',
        'min_value': 70,
    },
]

phase_events = detector.track_startup_phases(phases, min_phase_duration='5s')

# Analyze successful vs incomplete startups
complete_startups = phase_events[phase_events['completed'] == True]
incomplete_startups = phase_events[phase_events['completed'] == False]
```

#### Phase Condition Types:

**Threshold:**
- Value must be >= min_value
- Used for final operating states

**Range:**
- Value must be between min_value and max_value (inclusive)
- Used for intermediate phases

**Slope:**
- Rate of change must be >= min_slope
- Used for active transition phases

#### Use Cases:
- Detailed startup procedure validation
- Identifying which phase takes longest
- Detecting partial startups (stuck in intermediate phase)
- Process documentation and optimization
- SOP compliance verification

---

### 5. Failed Startup Detection

**Method:** `detect_failed_startups(threshold: float, min_rise_duration: str = '5s', max_completion_time: str = '5m', completion_threshold: Optional[float] = None, required_stability: str = '10s')`

Detect failed or aborted startup attempts.

#### Failure Detection Criteria:
A startup is considered failed when:
1. Value rises above threshold for at least `min_rise_duration`
2. But fails to reach `completion_threshold` within `max_completion_time`
3. Or drops back below threshold before achieving `required_stability`

#### Parameters:
- **threshold**: Initial threshold that must be crossed to begin startup
- **min_rise_duration**: Minimum time above threshold to consider it a startup attempt
- **max_completion_time**: Maximum time allowed to complete startup
- **completion_threshold**: Target threshold for successful completion (default: 2× threshold)
- **required_stability**: Time that must be maintained at completion level

#### Returns:
DataFrame with columns:
- **start**: Startup attempt start time
- **end**: Failure time
- **uuid**: Event UUID
- **is_delta**: Boolean flag
- **method**: 'failed_startup'
- **failure_reason**: Specific failure mode
- **max_value_reached**: Peak value before failure
- **time_to_failure**: Duration from start to failure (seconds)

#### Failure Reasons:
1. **dropped_below_threshold_before_completion**: Started but fell back before reaching target
2. **failed_to_reach_completion_threshold**: Never reached the completion threshold
3. **insufficient_stability_at_completion**: Reached target but couldn't maintain it

#### Example:
```python
detector = StartupDetectionEvents(df, target_uuid='pressure_sensor')

failed_events = detector.detect_failed_startups(
    threshold=2.0,
    min_rise_duration='3s',
    max_completion_time='1m',
    completion_threshold=5.0,
    required_stability='5s',
)

# Analyze failure patterns
for _, failure in failed_events.iterrows():
    print(f"Failure at {failure['start']}: {failure['failure_reason']}")
    print(f"  Max value reached: {failure['max_value_reached']}")
    print(f"  Time to failure: {failure['time_to_failure']}s")
```

#### Use Cases:
- Predictive maintenance (increasing failure frequency signals issues)
- Root cause analysis of startup problems
- Safety systems (detecting incomplete safety procedure execution)
- Energy efficiency (failed startups waste energy)
- Equipment diagnostics

---

## Backward Compatibility

All existing methods remain fully functional:

### Existing Methods (Unchanged)

**`detect_startup_by_threshold(threshold: float, hysteresis: tuple[float, float] | None = None, min_above: str = "0s")`**
- Original threshold-based detection
- All parameters and return values unchanged

**`detect_startup_by_slope(min_slope: float, slope_window: str = "0s", min_duration: str = "0s")`**
- Original slope-based detection
- All parameters and return values unchanged

## Integration Example

Complete example showing how to use all features together:

```python
import pandas as pd
from ts_shape.events.engineering.startup_events import StartupDetectionEvents

# Initialize detector
detector = StartupDetectionEvents(
    dataframe=df,
    target_uuid='main_temperature_sensor',
    event_uuid='startup_analysis',
)

# 1. Detect startups using multiple methods
threshold_events = detector.detect_startup_by_threshold(threshold=40.0, min_above='10s')
adaptive_events = detector.detect_startup_adaptive(sensitivity=2.5, min_above='15s')

# 2. Multi-signal confirmation
signals = {
    'main_temperature_sensor': {'method': 'threshold', 'threshold': 40.0},
    'backup_temperature_sensor': {'method': 'threshold', 'threshold': 38.0},
    'motor_current': {'method': 'threshold', 'threshold': 5.0},
}
confirmed_events = detector.detect_startup_multi_signal(signals, logic='all')

# 3. Assess quality of detected startups
quality_metrics = detector.assess_startup_quality(confirmed_events)
high_quality = quality_metrics[
    (quality_metrics['smoothness_score'] > 0.7) &
    (quality_metrics['stability_score'] > 0.8)
]

# 4. Track phases for detailed analysis
phases = [
    {'name': 'Preheat', 'condition': 'range', 'min_value': 20, 'max_value': 50},
    {'name': 'Ramp', 'condition': 'range', 'min_value': 50, 'max_value': 80},
    {'name': 'Stabilize', 'condition': 'threshold', 'min_value': 80},
]
phase_tracking = detector.track_startup_phases(phases)

# 5. Detect and analyze failures
failed_startups = detector.detect_failed_startups(
    threshold=30.0,
    completion_threshold=80.0,
    required_stability='20s',
)

# Generate comprehensive report
print(f"Total confirmed startups: {len(confirmed_events)}")
print(f"High quality startups: {len(high_quality)}")
print(f"Failed startup attempts: {len(failed_startups)}")
print(f"Complete phase sequences: {phase_tracking['completed'].sum()}")
```

## Performance Considerations

- **Multi-signal detection**: Performance scales linearly with number of signals
- **Adaptive detection**: Rolling statistics are efficient for reasonable lookback periods
- **Quality assessment**: Requires reading signal data for each event period
- **Phase tracking**: Single pass through data; efficient for most use cases
- **Failed startup detection**: Similar complexity to threshold detection

## Best Practices

1. **Start with existing methods**: Use `detect_startup_by_threshold()` or `detect_startup_by_slope()` first
2. **Add multi-signal for robustness**: Use when you have redundant sensors
3. **Use adaptive for dynamic environments**: When baseline conditions vary significantly
4. **Assess quality for monitoring**: Track quality trends over time for predictive maintenance
5. **Track phases for detailed analysis**: When startup procedure has well-defined stages
6. **Monitor failures**: Set up alerts for increasing failure rates

## Testing

Run the comprehensive test suite:

```bash
python3 test_startup_enhancements.py
```

This will validate all new features and backward compatibility.

## Migration Guide

Existing code will continue to work without changes:

```python
# This still works exactly as before
detector = StartupDetectionEvents(df, target_uuid='sensor1')
events = detector.detect_startup_by_threshold(threshold=50.0)
```

To use new features, simply call the new methods:

```python
# Add quality assessment
quality = detector.assess_startup_quality(events)

# Add failure detection
failures = detector.detect_failed_startups(threshold=50.0)
```

## Dependencies

No new external dependencies required. Uses existing:
- pandas
- numpy
- typing (standard library)

## Version Information

- **Enhanced Version**: 0.0.0.30+
- **Compatible with**: All previous versions
- **Breaking Changes**: None
