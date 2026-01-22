"""
Test script to verify the enhancements to statistical_process_control.py
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.ts_shape.events.quality.statistical_process_control import StatisticalProcessControlRuleBased

# Create sample data
np.random.seed(42)
base_time = datetime.now()

# Tolerance data (for control limits)
tolerance_data = pd.DataFrame({
    'systime': [base_time + timedelta(hours=i) for i in range(30)],
    'value': np.random.normal(100, 5, 30),
    'uuid': ['tolerance'] * 30
})

# Actual data with some violations
actual_data = pd.DataFrame({
    'systime': [base_time + timedelta(hours=i) for i in range(50)],
    'value': np.concatenate([
        np.random.normal(100, 5, 10),  # Normal
        np.random.normal(120, 5, 5),   # Shift up (rule 1)
        np.random.normal(105, 5, 9),   # Shift above mean (rule 2)
        np.random.normal(100, 5, 10),  # Normal
        np.arange(100, 106),           # Trend (rule 3)
        np.random.normal(100, 5, 10)   # Normal
    ]),
    'uuid': ['actual'] * 50
})

# Combine data
df = pd.concat([tolerance_data, actual_data], ignore_index=True)

# Initialize SPC monitor
spc = StatisticalProcessControlRuleBased(
    dataframe=df,
    value_column='value',
    tolerance_uuid='tolerance',
    actual_uuid='actual',
    event_uuid='event'
)

print("=" * 80)
print("SPC ENHANCEMENTS TEST")
print("=" * 80)

# Test 1: Original process method (backward compatibility)
print("\n1. Testing original process() method (backward compatibility):")
print("-" * 80)
violations = spc.process(selected_rules=['rule_1', 'rule_2', 'rule_3'])
print(f"Found {len(violations)} violations")
print(f"Columns: {violations.columns.tolist()}")
print(violations.head())

# Test 2: Enhanced process with severity
print("\n2. Testing process() with severity scoring:")
print("-" * 80)
violations_with_severity = spc.process(selected_rules=['rule_1', 'rule_2', 'rule_3'], include_severity=True)
print(f"Found {len(violations_with_severity)} violations")
print(f"Columns: {violations_with_severity.columns.tolist()}")
print(violations_with_severity.head())

# Test 3: Dynamic control limits - moving range
print("\n3. Testing calculate_dynamic_control_limits() - moving_range method:")
print("-" * 80)
dynamic_limits_mr = spc.calculate_dynamic_control_limits(method='moving_range', window=10)
print(f"Dynamic limits shape: {dynamic_limits_mr.shape}")
print(f"Columns: {dynamic_limits_mr.columns.tolist()}")
print(dynamic_limits_mr.head())

# Test 4: Dynamic control limits - EWMA
print("\n4. Testing calculate_dynamic_control_limits() - ewma method:")
print("-" * 80)
dynamic_limits_ewma = spc.calculate_dynamic_control_limits(method='ewma', window=10)
print(f"Dynamic limits shape: {dynamic_limits_ewma.shape}")
print(f"Columns: {dynamic_limits_ewma.columns.tolist()}")
print(dynamic_limits_ewma.head())

# Test 5: Vectorized rule application
print("\n5. Testing apply_rules_vectorized():")
print("-" * 80)
violations_vectorized = spc.apply_rules_vectorized(selected_rules=['rule_1', 'rule_2', 'rule_3'])
print(f"Found {len(violations_vectorized)} violations")
print(f"Columns: {violations_vectorized.columns.tolist()}")
if len(violations_vectorized) > 0:
    print(violations_vectorized.head())
    print(f"\nSeverity distribution:")
    print(violations_vectorized['severity'].value_counts())

# Test 6: CUSUM detection
print("\n6. Testing detect_cusum_shifts():")
print("-" * 80)
cusum_shifts = spc.detect_cusum_shifts(target=None, k=0.5, h=5.0)
print(f"Found {len(cusum_shifts)} CUSUM shifts")
print(f"Columns: {cusum_shifts.columns.tolist()}")
if len(cusum_shifts) > 0:
    print(cusum_shifts.head())
    print(f"\nShift directions:")
    print(cusum_shifts['shift_direction'].value_counts())

# Test 7: Interpretation of violations
print("\n7. Testing interpret_violations():")
print("-" * 80)
if len(violations_vectorized) > 0:
    interpreted = spc.interpret_violations(violations_vectorized)
    print(f"Interpreted violations shape: {interpreted.shape}")
    print(f"Columns: {interpreted.columns.tolist()}")
    print("\nFirst violation details:")
    first_violation = interpreted.iloc[0]
    print(f"  Rule: {first_violation['rule']}")
    print(f"  Severity: {first_violation['severity']}")
    print(f"  Interpretation: {first_violation['interpretation']}")
    print(f"  Meaning: {first_violation['meaning']}")
    print(f"  Recommendation: {first_violation['recommendation'][:80]}...")
else:
    print("No violations to interpret")

# Test 8: Optimized rule calculation
print("\n8. Testing optimized rule 2, 7, 8 calculation:")
print("-" * 80)
limits = spc.calculate_control_limits()
test_df = df[df['uuid'] == 'actual'].copy()
rule_2, rule_7, rule_8 = spc._calculate_rule_2_7_8_optimized(test_df, limits)
print(f"Rule 2 violations: {rule_2.sum()}")
print(f"Rule 7 violations: {rule_7.sum()}")
print(f"Rule 8 violations: {rule_8.sum()}")

print("\n" + "=" * 80)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 80)
