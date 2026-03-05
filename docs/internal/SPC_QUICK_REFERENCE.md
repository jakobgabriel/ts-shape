# SPC Enhancement Quick Reference

## New Methods Available

### 1. Dynamic Control Limits
```python
# Moving range method (rolling window)
limits = spc.calculate_dynamic_control_limits(method='moving_range', window=20)

# EWMA method (exponentially weighted)
limits = spc.calculate_dynamic_control_limits(method='ewma', window=20)
```

### 2. Vectorized Rule Processing (Faster!)
```python
# Process all rules with automatic severity
violations = spc.apply_rules_vectorized()

# Process specific rules
violations = spc.apply_rules_vectorized(selected_rules=['rule_1', 'rule_2'])
```

### 3. CUSUM Shift Detection
```python
# Default parameters
shifts = spc.detect_cusum_shifts()

# Custom sensitivity
shifts = spc.detect_cusum_shifts(target=100, k=0.5, h=4.5)
```

### 4. Interpret Violations
```python
# Get violations
violations = spc.apply_rules_vectorized()

# Add human-readable interpretations
interpreted = spc.interpret_violations(violations)

# View recommendations
print(interpreted[['rule', 'severity', 'interpretation', 'recommendation']])
```

### 5. Enhanced Process Method
```python
# Backward compatible (unchanged behavior)
violations = spc.process(selected_rules=['rule_1'])

# With severity scoring
violations = spc.process(selected_rules=['rule_1'], include_severity=True)
```

## Severity Levels

| Level | Rules | Action Required |
|-------|-------|-----------------|
| **Critical** | rule_1 | Immediate investigation |
| **High** | rule_5 | Urgent attention |
| **Medium** | rule_2, rule_3, rule_4, rule_6 | Timely investigation |
| **Low** | rule_7, rule_8 | Monitor and document |

## Complete Workflow Example

```python
from ts_shape.events.quality.statistical_process_control import StatisticalProcessControlRuleBased

# Initialize
spc = StatisticalProcessControlRuleBased(
    dataframe=df,
    value_column='measurement',
    tolerance_uuid='tolerance',
    actual_uuid='actual',
    event_uuid='event'
)

# Step 1: Check for rule violations (fast vectorized method)
violations = spc.apply_rules_vectorized()

# Step 2: Check for CUSUM shifts (sensitive to small changes)
cusum_shifts = spc.detect_cusum_shifts(k=0.5, h=5.0)

# Step 3: Add interpretations and recommendations
if not violations.empty:
    interpreted = spc.interpret_violations(violations)

    # Focus on critical/high severity issues
    urgent = interpreted[interpreted['severity'].isin(['critical', 'high'])]

    print(f"Total violations: {len(violations)}")
    print(f"Urgent issues: {len(urgent)}")
    print(f"CUSUM shifts: {len(cusum_shifts)}")

    # Print urgent issues with recommendations
    for _, row in urgent.iterrows():
        print(f"\n{'='*60}")
        print(f"Time: {row['systime']}")
        print(f"Value: {row['value']}")
        print(f"Severity: {row['severity'].upper()}")
        print(f"Issue: {row['interpretation']}")
        print(f"What it means: {row['meaning']}")
        print(f"Recommended action: {row['recommendation']}")

# Step 4: Calculate dynamic limits for trending
dynamic_limits = spc.calculate_dynamic_control_limits(method='ewma', window=30)
```

## Performance Tips

1. **Use `apply_rules_vectorized()`** instead of `process()` for better performance
2. **Select specific rules** if you don't need all eight rules
3. **Use CUSUM** for detecting small, gradual shifts
4. **Use EWMA limits** for non-stationary processes
5. **Filter by severity** to prioritize critical issues

## Migration from Old Code

```python
# OLD: Original process method
violations = spc.process(selected_rules=['rule_1', 'rule_2'])
# Returns: [systime, value, uuid]

# NEW: Same behavior (backward compatible)
violations = spc.process(selected_rules=['rule_1', 'rule_2'])
# Returns: [systime, value, uuid]

# NEW: With severity info
violations = spc.process(selected_rules=['rule_1', 'rule_2'], include_severity=True)
# Returns: [systime, value, uuid, triggered_rule, severity]

# NEW: Faster vectorized method with severity
violations = spc.apply_rules_vectorized(selected_rules=['rule_1', 'rule_2'])
# Returns: [systime, value, rule, severity, uuid]
```

## Rule Interpretations Summary

| Rule | Pattern | Severity | Meaning |
|------|---------|----------|---------|
| rule_1 | 1 point beyond 3σ | Critical | Special cause event |
| rule_2 | 9 consecutive on one side | Medium | Process mean shifted |
| rule_3 | 6 consecutive trend | Medium | Systematic drift |
| rule_4 | 14 alternating | Medium | Oscillating causes |
| rule_5 | 2 of 3 beyond 2σ | High | Variation increasing |
| rule_6 | 4 of 5 beyond 1σ | Medium | Process capability issue |
| rule_7 | 15 within 1σ | Low | Unusually low variation |
| rule_8 | 8 beyond 1σ both sides | Low | Higher variation |

## CUSUM Parameters Guide

### k (Reference Value)
- **0.25-0.5**: Very sensitive, detects small shifts (0.5-1σ)
- **0.5-0.75**: Balanced sensitivity (1-1.5σ)
- **0.75-1.0**: Less sensitive, detects larger shifts (1.5-2σ)

### h (Decision Interval)
- **3-4**: Fast detection, more false alarms
- **4-5**: Balanced (recommended)
- **5-6**: Slower detection, fewer false alarms

### Example Use Cases
```python
# Detect small shifts quickly (high sensitivity)
shifts = spc.detect_cusum_shifts(k=0.3, h=4.0)

# Balanced detection (recommended)
shifts = spc.detect_cusum_shifts(k=0.5, h=5.0)

# Detect only significant shifts (low false alarms)
shifts = spc.detect_cusum_shifts(k=0.75, h=6.0)
```

## Common Patterns

### Pattern 1: Real-time Monitoring
```python
# Fast vectorized detection
violations = spc.apply_rules_vectorized()

if not violations.empty:
    critical = violations[violations['severity'] == 'critical']
    if not critical.empty:
        # Trigger immediate alerts
        send_alert(critical)
```

### Pattern 2: Batch Analysis
```python
# Comprehensive analysis
violations = spc.apply_rules_vectorized()
interpreted = spc.interpret_violations(violations)
cusum = spc.detect_cusum_shifts()

# Generate report
generate_quality_report(interpreted, cusum)
```

### Pattern 3: Process Monitoring
```python
# Track changing process
dynamic_limits = spc.calculate_dynamic_control_limits(method='ewma', window=50)

# Compare actual vs dynamic limits
plot_control_chart(actual_values, dynamic_limits)
```

## Testing Backward Compatibility

```python
# This existing test should still pass
def test_backward_compatibility():
    spc = StatisticalProcessControlRuleBased(df, 'value', 'tol', 'act', 'evt')

    # Original methods unchanged
    limits = spc.calculate_control_limits()
    assert 'mean' in limits.columns

    violations = spc.process(selected_rules=['rule_1'])
    assert 'uuid' in violations.columns
    assert 'systime' in violations.columns

    print("✓ All original functionality preserved")
```

## Key Advantages

1. **Faster Processing**: Vectorized operations, optimized rule calculations
2. **Better Insights**: Severity scoring, interpretations, recommendations
3. **More Sensitive**: CUSUM for detecting small shifts
4. **Adaptive**: Dynamic control limits for non-stationary processes
5. **Backward Compatible**: Existing code works without changes
6. **Production Ready**: Type hints, comprehensive docstrings, error handling

## Files Modified

- `/home/user/ts-shape/src/ts_shape/events/quality/statistical_process_control.py`

## Next Steps

1. Review the implementation in the source file
2. Run existing tests to verify backward compatibility
3. Try the new methods with your data
4. Refer to `SPC_ENHANCEMENTS_SUMMARY.md` for detailed documentation
