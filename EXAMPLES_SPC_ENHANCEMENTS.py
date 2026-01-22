"""
Practical Examples for Enhanced SPC Module

These examples demonstrate all new features in the enhanced
statistical_process_control.py module.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Assuming the module is installed or in path
from ts_shape.events.quality.statistical_process_control import StatisticalProcessControlRuleBased


def create_sample_data():
    """Create sample manufacturing data with known violations."""
    np.random.seed(42)
    base_time = datetime(2024, 1, 1)

    # Tolerance/baseline data
    tolerance_data = pd.DataFrame({
        'systime': [base_time + timedelta(hours=i) for i in range(50)],
        'value': np.random.normal(100, 3, 50),
        'uuid': ['tolerance'] * 50
    })

    # Actual data with engineered violations
    actual_values = []

    # Period 1: Normal operation (no violations)
    actual_values.extend(np.random.normal(100, 3, 20))

    # Period 2: Outlier (rule 1 - critical)
    actual_values.append(120)  # Beyond 3-sigma

    # Period 3: Mean shift up (rule 2 - medium)
    actual_values.extend(np.random.normal(106, 3, 10))

    # Period 4: Upward trend (rule 3 - medium)
    actual_values.extend(np.linspace(100, 108, 6))

    # Period 5: High variation points (rule 5 - high)
    actual_values.extend([108, 110, 109])

    # Period 6: Return to normal
    actual_values.extend(np.random.normal(100, 3, 10))

    actual_data = pd.DataFrame({
        'systime': [base_time + timedelta(hours=i) for i in range(len(actual_values))],
        'value': actual_values,
        'uuid': ['actual'] * len(actual_values)
    })

    return pd.concat([tolerance_data, actual_data], ignore_index=True)


# =============================================================================
# EXAMPLE 1: Backward Compatibility
# =============================================================================
def example_1_backward_compatibility():
    """Show that existing code still works unchanged."""
    print("=" * 80)
    print("EXAMPLE 1: Backward Compatibility")
    print("=" * 80)

    df = create_sample_data()
    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value',
        tolerance_uuid='tolerance',
        actual_uuid='actual',
        event_uuid='quality_event'
    )

    # Original method - works exactly as before
    violations = spc.process(selected_rules=['rule_1', 'rule_2', 'rule_3'])

    print(f"\nViolations detected: {len(violations)}")
    print(f"Columns (original format): {violations.columns.tolist()}")
    print("\nFirst few violations:")
    print(violations.head())

    # Verify expected columns
    assert 'systime' in violations.columns
    assert 'value' in violations.columns
    assert 'uuid' in violations.columns
    print("\n✓ Backward compatibility verified!")


# =============================================================================
# EXAMPLE 2: Enhanced Process with Severity
# =============================================================================
def example_2_process_with_severity():
    """Use the enhanced process method with severity scoring."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Enhanced Process Method with Severity")
    print("=" * 80)

    df = create_sample_data()
    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value',
        tolerance_uuid='tolerance',
        actual_uuid='actual',
        event_uuid='quality_event'
    )

    # Use enhanced process method
    violations = spc.process(selected_rules=['rule_1', 'rule_2', 'rule_3'], include_severity=True)

    print(f"\nViolations detected: {len(violations)}")
    print(f"Columns (with severity): {violations.columns.tolist()}")

    if not violations.empty:
        print("\nSeverity breakdown:")
        print(violations['severity'].value_counts())

        print("\nRule breakdown:")
        print(violations['triggered_rule'].value_counts())

        print("\nCritical violations:")
        critical = violations[violations['severity'] == 'critical']
        print(critical[['systime', 'value', 'triggered_rule', 'severity']])


# =============================================================================
# EXAMPLE 3: Vectorized Rule Processing (Best Performance)
# =============================================================================
def example_3_vectorized_processing():
    """Use vectorized method for better performance."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Vectorized Rule Processing")
    print("=" * 80)

    df = create_sample_data()
    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value',
        tolerance_uuid='tolerance',
        actual_uuid='actual',
        event_uuid='quality_event'
    )

    # Use vectorized method (faster!)
    violations = spc.apply_rules_vectorized()

    print(f"\nTotal violations: {len(violations)}")

    if not violations.empty:
        print("\nViolations by severity:")
        severity_counts = violations.groupby('severity').size().to_dict()
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_counts.get(severity, 0)
            print(f"  {severity.upper()}: {count}")

        print("\nSample violations:")
        print(violations[['systime', 'value', 'rule', 'severity']].head(10))

        # Filter by severity
        urgent = violations[violations['severity'].isin(['critical', 'high'])]
        print(f"\n⚠️  Urgent issues requiring attention: {len(urgent)}")


# =============================================================================
# EXAMPLE 4: Dynamic Control Limits
# =============================================================================
def example_4_dynamic_control_limits():
    """Calculate and use dynamic control limits."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Dynamic Control Limits")
    print("=" * 80)

    df = create_sample_data()
    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value',
        tolerance_uuid='tolerance',
        actual_uuid='actual',
        event_uuid='quality_event'
    )

    # Method 1: Moving Range
    print("\n--- Moving Range Method ---")
    dynamic_mr = spc.calculate_dynamic_control_limits(method='moving_range', window=20)
    print(f"Shape: {dynamic_mr.shape}")
    print(f"Columns: {dynamic_mr.columns.tolist()}")
    print("\nFirst few rows:")
    print(dynamic_mr[['systime', 'mean', '3sigma_upper', '3sigma_lower']].head())

    # Method 2: EWMA
    print("\n--- EWMA Method ---")
    dynamic_ewma = spc.calculate_dynamic_control_limits(method='ewma', window=20)
    print(f"Shape: {dynamic_ewma.shape}")
    print("\nLast few rows:")
    print(dynamic_ewma[['systime', 'mean', '3sigma_upper', '3sigma_lower']].tail())

    # Compare static vs dynamic
    static_limits = spc.calculate_control_limits()
    print(f"\nStatic limits (constant):")
    print(f"  Mean: {static_limits['mean'].values[0]:.2f}")
    print(f"  3σ upper: {static_limits['3sigma_upper'].values[0]:.2f}")

    print(f"\nDynamic limits (EWMA, last value):")
    print(f"  Mean: {dynamic_ewma['mean'].iloc[-1]:.2f}")
    print(f"  3σ upper: {dynamic_ewma['3sigma_upper'].iloc[-1]:.2f}")


# =============================================================================
# EXAMPLE 5: CUSUM Shift Detection
# =============================================================================
def example_5_cusum_detection():
    """Detect process shifts using CUSUM charts."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: CUSUM Shift Detection")
    print("=" * 80)

    df = create_sample_data()
    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value',
        tolerance_uuid='tolerance',
        actual_uuid='actual',
        event_uuid='quality_event'
    )

    # Default parameters (balanced sensitivity)
    print("\n--- Default Parameters (k=0.5, h=5.0) ---")
    cusum_default = spc.detect_cusum_shifts()
    print(f"Shifts detected: {len(cusum_default)}")

    if not cusum_default.empty:
        print("\nDetected shifts:")
        print(cusum_default[['systime', 'value', 'shift_direction', 'severity']])

        print("\nShift direction summary:")
        print(cusum_default['shift_direction'].value_counts())

    # High sensitivity (detects smaller shifts)
    print("\n--- High Sensitivity (k=0.3, h=4.0) ---")
    cusum_sensitive = spc.detect_cusum_shifts(k=0.3, h=4.0)
    print(f"Shifts detected: {len(cusum_sensitive)}")

    # Low sensitivity (only major shifts)
    print("\n--- Low Sensitivity (k=0.8, h=6.0) ---")
    cusum_conservative = spc.detect_cusum_shifts(k=0.8, h=6.0)
    print(f"Shifts detected: {len(cusum_conservative)}")


# =============================================================================
# EXAMPLE 6: Violation Interpretations
# =============================================================================
def example_6_interpretations():
    """Add human-readable interpretations to violations."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Violation Interpretations")
    print("=" * 80)

    df = create_sample_data()
    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value',
        tolerance_uuid='tolerance',
        actual_uuid='actual',
        event_uuid='quality_event'
    )

    # Get violations
    violations = spc.apply_rules_vectorized()

    if violations.empty:
        print("No violations detected in this dataset")
        return

    # Add interpretations
    interpreted = spc.interpret_violations(violations)

    print(f"\nTotal violations with interpretations: {len(interpreted)}")
    print(f"Columns: {interpreted.columns.tolist()}")

    # Show detailed information for each unique rule
    print("\n" + "=" * 80)
    print("DETAILED VIOLATION ANALYSIS")
    print("=" * 80)

    for rule in interpreted['rule'].unique():
        rule_violations = interpreted[interpreted['rule'] == rule].iloc[0]

        print(f"\n{rule.upper()} ({rule_violations['severity'].upper()} severity)")
        print("-" * 80)
        print(f"Pattern: {rule_violations['interpretation']}")
        print(f"Meaning: {rule_violations['meaning']}")
        print(f"Recommendation: {rule_violations['recommendation']}")
        print(f"Occurrences: {len(interpreted[interpreted['rule'] == rule])}")


# =============================================================================
# EXAMPLE 7: Complete Quality Analysis Workflow
# =============================================================================
def example_7_complete_workflow():
    """Complete quality analysis using all features."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Complete Quality Analysis Workflow")
    print("=" * 80)

    df = create_sample_data()
    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value',
        tolerance_uuid='tolerance',
        actual_uuid='actual',
        event_uuid='quality_event'
    )

    print("\n📊 QUALITY CONTROL ANALYSIS REPORT")
    print("=" * 80)

    # Step 1: Calculate control limits
    limits = spc.calculate_control_limits()
    print(f"\n1. Control Limits:")
    print(f"   Mean: {limits['mean'].values[0]:.2f}")
    print(f"   3σ Upper: {limits['3sigma_upper'].values[0]:.2f}")
    print(f"   3σ Lower: {limits['3sigma_lower'].values[0]:.2f}")

    # Step 2: Detect violations (vectorized)
    violations = spc.apply_rules_vectorized()
    print(f"\n2. Western Electric Rules Analysis:")
    print(f"   Total violations: {len(violations)}")

    if not violations.empty:
        severity_summary = violations['severity'].value_counts().to_dict()
        print(f"   - Critical: {severity_summary.get('critical', 0)}")
        print(f"   - High: {severity_summary.get('high', 0)}")
        print(f"   - Medium: {severity_summary.get('medium', 0)}")
        print(f"   - Low: {severity_summary.get('low', 0)}")

    # Step 3: CUSUM analysis
    cusum = spc.detect_cusum_shifts(k=0.5, h=5.0)
    print(f"\n3. CUSUM Shift Detection:")
    print(f"   Process shifts detected: {len(cusum)}")

    if not cusum.empty:
        direction_summary = cusum['shift_direction'].value_counts().to_dict()
        print(f"   - Upward shifts: {direction_summary.get('upward', 0)}")
        print(f"   - Downward shifts: {direction_summary.get('downward', 0)}")

    # Step 4: Dynamic limits
    dynamic_limits = spc.calculate_dynamic_control_limits(method='ewma', window=20)
    current_mean = dynamic_limits['mean'].iloc[-1]
    target_mean = limits['mean'].values[0]
    drift = current_mean - target_mean

    print(f"\n4. Process Drift Analysis (EWMA):")
    print(f"   Target mean: {target_mean:.2f}")
    print(f"   Current mean: {current_mean:.2f}")
    print(f"   Drift: {drift:+.2f} ({abs(drift/target_mean)*100:.1f}%)")

    # Step 5: Recommendations
    print(f"\n5. Recommendations:")

    if not violations.empty:
        interpreted = spc.interpret_violations(violations)

        # Critical issues
        critical = interpreted[interpreted['severity'] == 'critical']
        if not critical.empty:
            print(f"\n   ⚠️  CRITICAL ISSUES (Immediate Action Required):")
            for _, issue in critical.iterrows():
                print(f"      - {issue['interpretation']}")
                print(f"        Action: {issue['recommendation'][:70]}...")

        # High priority issues
        high = interpreted[interpreted['severity'] == 'high']
        if not high.empty:
            print(f"\n   ⚡ HIGH PRIORITY (Urgent Attention):")
            for _, issue in high.iterrows():
                print(f"      - {issue['interpretation']}")

        # Medium issues
        medium = interpreted[interpreted['severity'] == 'medium']
        if not medium.empty:
            print(f"\n   📋 MEDIUM PRIORITY (Timely Investigation):")
            print(f"      {len(medium)} issues detected - review process parameters")

    else:
        print("   ✓ No violations detected - process is in statistical control")

    print("\n" + "=" * 80)
    print("END OF REPORT")
    print("=" * 80)


# =============================================================================
# EXAMPLE 8: Performance Comparison
# =============================================================================
def example_8_performance_comparison():
    """Compare performance of original vs vectorized methods."""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Performance Comparison")
    print("=" * 80)

    import time

    # Create larger dataset
    np.random.seed(42)
    base_time = datetime(2024, 1, 1)

    tolerance_data = pd.DataFrame({
        'systime': [base_time + timedelta(hours=i) for i in range(100)],
        'value': np.random.normal(100, 5, 100),
        'uuid': ['tolerance'] * 100
    })

    actual_data = pd.DataFrame({
        'systime': [base_time + timedelta(hours=i) for i in range(1000)],
        'value': np.random.normal(100, 5, 1000),
        'uuid': ['actual'] * 1000
    })

    df = pd.concat([tolerance_data, actual_data], ignore_index=True)

    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value',
        tolerance_uuid='tolerance',
        actual_uuid='actual',
        event_uuid='quality_event'
    )

    print(f"\nDataset size: {len(actual_data)} actual measurements")

    # Method 1: Original process
    print("\n--- Original process() method ---")
    start = time.time()
    violations_original = spc.process(selected_rules=['rule_1', 'rule_2', 'rule_3'])
    time_original = time.time() - start
    print(f"Time: {time_original:.4f} seconds")
    print(f"Violations: {len(violations_original)}")

    # Method 2: Vectorized
    print("\n--- Vectorized apply_rules_vectorized() method ---")
    start = time.time()
    violations_vectorized = spc.apply_rules_vectorized(selected_rules=['rule_1', 'rule_2', 'rule_3'])
    time_vectorized = time.time() - start
    print(f"Time: {time_vectorized:.4f} seconds")
    print(f"Violations: {len(violations_vectorized)}")

    if time_original > 0:
        speedup = time_original / time_vectorized
        print(f"\n⚡ Speedup: {speedup:.2f}x faster")
    else:
        print("\n(Dataset too small for meaningful comparison)")


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "SPC ENHANCEMENT EXAMPLES" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        example_1_backward_compatibility()
        example_2_process_with_severity()
        example_3_vectorized_processing()
        example_4_dynamic_control_limits()
        example_5_cusum_detection()
        example_6_interpretations()
        example_7_complete_workflow()
        example_8_performance_comparison()

        print("\n" + "=" * 80)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print("\nKey Takeaways:")
        print("1. All original functionality is preserved (backward compatible)")
        print("2. New vectorized method provides better performance")
        print("3. Severity scoring helps prioritize issues")
        print("4. Interpretations provide actionable insights")
        print("5. CUSUM detects subtle shifts traditional rules might miss")
        print("6. Dynamic limits adapt to changing process characteristics")
        print("\nRefer to SPC_ENHANCEMENTS_SUMMARY.md for detailed documentation")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
