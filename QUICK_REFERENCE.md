# SetpointChangeEvents - Quick Reference Card

## Import

```python
from ts_shape.events.engineering.setpoint_events import SetpointChangeEvents
```

## Initialization

```python
spe = SetpointChangeEvents(
    dataframe=df,
    setpoint_uuid='SP_TEMP_001',
    event_uuid='setpoint_change_event',  # optional
    value_column='value_double',          # optional
    time_column='systime'                 # optional
)
```

## Change Detection

### Detect Steps (with noise filtering)

```python
# Original
steps = spe.detect_setpoint_steps(min_delta=1.0, min_hold='5s')

# With noise filtering (NEW)
steps = spe.detect_setpoint_steps(
    min_delta=1.0,
    min_hold='5s',
    filter_noise=True,
    noise_threshold=0.1
)
```

### Detect Ramps

```python
ramps = spe.detect_setpoint_ramps(min_rate=0.5, min_duration='10s')
```

### Detect All Changes

```python
changes = spe.detect_setpoint_changes(
    min_delta=1.0,
    min_rate=0.5,
    min_hold='5s',
    min_duration='10s'
)
```

## Settling Analysis

### Error-Based Settling (with % tolerance)

```python
# Original - absolute tolerance
settle = spe.time_to_settle('PV_001', tol=2.0, hold='30s', lookahead='10m')

# NEW - percentage tolerance (better for varying step sizes)
settle = spe.time_to_settle('PV_001', settle_pct=0.02, hold='30s', lookahead='10m')
```

### Derivative-Based Settling (NEW)

```python
settle_deriv = spe.time_to_settle_derivative(
    'PV_001',
    rate_threshold=0.01,
    lookahead='10m',
    hold='1m'
)
```

## Transient Response

### Overshoot Metrics (enhanced with undershoot & oscillations)

```python
overshoot = spe.overshoot_metrics('PV_001', window='10m')

# Returns:
# - overshoot_abs, overshoot_pct, t_peak_seconds
# - undershoot_abs, undershoot_pct, t_undershoot_seconds (NEW)
# - oscillation_count, oscillation_amplitude (NEW)
```

### Rise Time (NEW)

```python
rise = spe.rise_time(
    'PV_001',
    start_pct=0.1,   # 10%
    end_pct=0.9,     # 90%
    lookahead='10m'
)
```

## System Dynamics

### Decay Rate (NEW)

```python
decay = spe.decay_rate('PV_001', lookahead='10m', min_points=5)

# Returns:
# - decay_rate_lambda (exponential decay constant)
# - fit_quality_r2 (goodness of fit)
```

### Oscillation Frequency (NEW)

```python
freq = spe.oscillation_frequency('PV_001', window='10m', min_oscillations=2)

# Returns:
# - oscillation_freq_hz
# - period_seconds
```

## Comprehensive Analysis

### All-in-One Quality Metrics (NEW)

```python
quality = spe.control_quality_metrics(
    'PV_001',
    tol=2.0,              # Absolute tolerance (fallback)
    settle_pct=0.02,      # Percentage tolerance (takes priority)
    hold='30s',
    lookahead='10m',
    rate_threshold=0.01
)

# Returns DataFrame with 17 columns:
# - Settling metrics (error & derivative-based)
# - Rise time
# - Overshoot & undershoot
# - Oscillation metrics
# - Decay rate
# - Steady-state error
```

## Common Patterns

### Pattern 1: Quick Quality Check

```python
spe = SetpointChangeEvents(df, setpoint_uuid='SP_001')
quality = spe.control_quality_metrics('PV_001', settle_pct=0.02, lookahead='15m')

# Check for problems
problems = quality[
    (quality['overshoot_pct'] > 0.2) |
    (quality['oscillation_count'] > 5) |
    (quality['t_settle_seconds'] > 300)
]
```

### Pattern 2: Compare Before/After Tuning

```python
# Before tuning
quality_before = spe_before.control_quality_metrics('PV_001', settle_pct=0.02)

# After tuning
quality_after = spe_after.control_quality_metrics('PV_001', settle_pct=0.02)

# Calculate improvements
improvement = quality_before['overshoot_pct'].mean() - quality_after['overshoot_pct'].mean()
```

### Pattern 3: System Characterization

```python
# Get complete system dynamics
rise = spe.rise_time('PV_001')
decay = spe.decay_rate('PV_001')
freq = spe.oscillation_frequency('PV_001')

# Analyze
damping_ratio = estimate_damping(decay['decay_rate_lambda'], freq['oscillation_freq_hz'])
```

### Pattern 4: Batch Loop Analysis

```python
results = []
for sp_uuid in setpoint_list:
    pv_uuid = sp_uuid.replace('SP_', 'PV_')
    spe = SetpointChangeEvents(df, setpoint_uuid=sp_uuid)
    quality = spe.control_quality_metrics(pv_uuid, settle_pct=0.02)
    results.append(quality)

report = pd.concat(results, ignore_index=True)
```

## Performance Tips

1. **Use caching**: Multiple method calls with same `actual_uuid` automatically reuse cached data
2. **Use `control_quality_metrics`**: When you need multiple metrics, this is faster than calling methods individually
3. **Adjust `lookahead`**: Longer windows give more data but take longer to compute
4. **Use `settle_pct`**: More meaningful than absolute tolerance for varying step sizes

## Return Value Quick Reference

| Method | Key Return Columns |
|--------|-------------------|
| `detect_setpoint_steps` | start, end, magnitude, prev_level, new_level |
| `time_to_settle` | start, t_settle_seconds, settled |
| `time_to_settle_derivative` | start, t_settle_seconds, settled, final_rate |
| `overshoot_metrics` | overshoot_abs/pct, undershoot_abs/pct, oscillation_count |
| `rise_time` | rise_time_seconds, reached_end |
| `decay_rate` | decay_rate_lambda, fit_quality_r2 |
| `oscillation_frequency` | oscillation_freq_hz, period_seconds |
| `control_quality_metrics` | All of the above (17 columns) |

## Parameter Defaults

- `filter_noise`: False (disabled by default)
- `noise_threshold`: 0.01
- `settle_pct`: None (uses `tol` if not specified)
- `rate_threshold`: 0.01
- `hold`: '0s'
- `lookahead`: '10m'
- `window`: '10m'
- `start_pct`: 0.1
- `end_pct`: 0.9
- `min_points`: 5
- `min_oscillations`: 2

## Backward Compatibility

All enhancements are **100% backward compatible**. Existing code will continue to work without any changes.

```python
# This old code still works perfectly
spe = SetpointChangeEvents(df, setpoint_uuid='SP_001')
steps = spe.detect_setpoint_steps(min_delta=1.0)
settle = spe.time_to_settle('PV_001', tol=2.0)
overshoot = spe.overshoot_metrics('PV_001')
```

## Need More Help?

- Full documentation: `SETPOINT_EVENTS_ENHANCEMENTS.md`
- Examples: `examples/setpoint_events_advanced_usage.py`
- Visual guide: `ENHANCEMENTS_VISUAL_GUIDE.txt`
