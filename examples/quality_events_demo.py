#!/usr/bin/env python3
"""
Demonstration of quality event detection in ts-shape.

This script shows how to use:
1. OutlierDetectionEvents (z-score, IQR, MAD methods)
2. StatisticalProcessControlRuleBased (Western Electric rules)
3. ToleranceDeviationEvents (tolerance violations)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import ts_shape
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ts_shape.events.quality.outlier_detection import OutlierDetectionEvents
from ts_shape.events.quality.statistical_process_control import StatisticalProcessControlRuleBased
from ts_shape.events.quality.tolerance_deviation import ToleranceDeviationEvents


def create_sensor_data_with_outliers():
    """Create synthetic sensor data with injected outliers."""
    np.random.seed(42)
    start_time = datetime(2024, 1, 1, 8, 0, 0)
    n_points = 200

    timestamps = [start_time + timedelta(seconds=i * 30) for i in range(n_points)]
    # Normal sensor readings around 50 with std ~2
    values = np.random.normal(50.0, 2.0, n_points)

    # Inject outliers at known positions
    outlier_indices = [25, 26, 80, 81, 82, 150]
    for idx in outlier_indices:
        values[idx] = 50.0 + np.random.choice([-1, 1]) * np.random.uniform(12, 18)

    df = pd.DataFrame({
        'systime': timestamps,
        'uuid': 'sensor_temperature',
        'value_double': values,
        'is_delta': True,
    })
    return df


def create_spc_data():
    """Create synthetic data with SPC violations for Western Electric rules."""
    np.random.seed(123)
    start_time = datetime(2024, 1, 1, 8, 0, 0)
    n_points = 150

    timestamps = [start_time + timedelta(seconds=i * 10) for i in range(n_points)]

    # Tolerance data (baseline for control limits)
    tolerance_values = np.random.normal(100.0, 3.0, 30)
    tolerance_rows = pd.DataFrame({
        'systime': timestamps[:30],
        'uuid': 'tolerance_ref',
        'value_double': tolerance_values,
        'is_delta': True,
    })

    # Actual values: mostly normal, with injected violations
    actual_values = np.random.normal(100.0, 3.0, n_points)

    # Rule 1 violation: point beyond 3-sigma (index 50)
    actual_values[50] = 115.0

    # Rule 3 violation: six consecutive increasing points (indices 90-95)
    for i in range(6):
        actual_values[90 + i] = 100.0 + i * 1.5

    actual_rows = pd.DataFrame({
        'systime': timestamps,
        'uuid': 'actual_measurement',
        'value_double': actual_values,
        'is_delta': True,
    })

    df = pd.concat([tolerance_rows, actual_rows], ignore_index=True)
    return df


def create_tolerance_data():
    """Create synthetic data for tolerance deviation detection."""
    start_time = datetime(2024, 1, 1, 8, 0, 0)
    n_points = 100
    timestamps = [start_time + timedelta(seconds=i * 15) for i in range(n_points)]

    rows = []

    # Upper tolerance setting rows
    for i in range(0, n_points, 20):
        rows.append({
            'systime': timestamps[i],
            'uuid': 'upper_tol',
            'value_double': 105.0,
            'is_delta': True,
        })

    # Lower tolerance setting rows
    for i in range(0, n_points, 20):
        rows.append({
            'systime': timestamps[i],
            'uuid': 'lower_tol',
            'value_double': 95.0,
            'is_delta': True,
        })

    # Actual measurement rows (some within tolerance, some outside)
    np.random.seed(99)
    for i in range(n_points):
        value = np.random.normal(100.0, 4.0)
        rows.append({
            'systime': timestamps[i],
            'uuid': 'actual_meas',
            'value_double': value,
            'is_delta': True,
        })

    df = pd.DataFrame(rows)
    return df


def demo_outlier_detection():
    """Demo 1: Outlier detection using z-score, IQR, and MAD methods."""
    print("\n" + "=" * 70)
    print("DEMO 1: Outlier Detection Events")
    print("=" * 70)

    df = create_sensor_data_with_outliers()
    print(f"\nDataset: {len(df)} sensor readings over {(df['systime'].max() - df['systime'].min())}")

    detector = OutlierDetectionEvents(
        dataframe=df,
        value_column='value_double',
        event_uuid='outlier_event',
        time_threshold='5min',
    )

    # Z-score method
    print("\n--- Z-Score Method (threshold=3.0) ---")
    zscore_outliers = detector.detect_outliers_zscore(threshold=3.0)
    print(f"  Outliers detected: {len(zscore_outliers)}")
    if not zscore_outliers.empty:
        print(f"  Severity scores: min={zscore_outliers['severity_score'].min():.2f}, "
              f"max={zscore_outliers['severity_score'].max():.2f}")
        print(zscore_outliers[['systime', 'value_double', 'severity_score']].head())

    # IQR method
    print("\n--- IQR Method (threshold=(1.5, 1.5)) ---")
    iqr_outliers = detector.detect_outliers_iqr(threshold=(1.5, 1.5))
    print(f"  Outliers detected: {len(iqr_outliers)}")
    if not iqr_outliers.empty:
        print(iqr_outliers[['systime', 'value_double', 'severity_score']].head())

    # MAD method
    print("\n--- MAD Method (threshold=3.5) ---")
    mad_outliers = detector.detect_outliers_mad(threshold=3.5)
    print(f"  Outliers detected: {len(mad_outliers)}")
    if not mad_outliers.empty:
        print(mad_outliers[['systime', 'value_double', 'severity_score']].head())

    # Compare methods
    print("\n--- Method Comparison ---")
    print(f"  Z-Score: {len(zscore_outliers)} outlier events")
    print(f"  IQR:     {len(iqr_outliers)} outlier events")
    print(f"  MAD:     {len(mad_outliers)} outlier events")


def demo_spc_rules():
    """Demo 2: Statistical Process Control with Western Electric Rules."""
    print("\n" + "=" * 70)
    print("DEMO 2: Statistical Process Control (Western Electric Rules)")
    print("=" * 70)

    df = create_spc_data()
    print(f"\nDataset: {len(df)} rows (tolerance + actual measurements)")

    spc = StatisticalProcessControlRuleBased(
        dataframe=df,
        value_column='value_double',
        tolerance_uuid='tolerance_ref',
        actual_uuid='actual_measurement',
        event_uuid='spc_violation',
    )

    # Calculate control limits
    print("\n--- Control Limits ---")
    limits = spc.calculate_control_limits()
    print(f"  Mean:       {limits['mean'].values[0]:.2f}")
    print(f"  1-sigma:    [{limits['1sigma_lower'].values[0]:.2f}, {limits['1sigma_upper'].values[0]:.2f}]")
    print(f"  2-sigma:    [{limits['2sigma_lower'].values[0]:.2f}, {limits['2sigma_upper'].values[0]:.2f}]")
    print(f"  3-sigma:    [{limits['3sigma_lower'].values[0]:.2f}, {limits['3sigma_upper'].values[0]:.2f}]")

    # Apply selected rules
    print("\n--- Applying Rules 1, 2, 3 ---")
    try:
        violations = spc.process(selected_rules=['rule_1', 'rule_2', 'rule_3'], include_severity=True)
        print(f"  Total violations: {len(violations)}")
        if not violations.empty:
            print("\n  Violations by rule:")
            print(violations.groupby('triggered_rule')['severity'].value_counts().to_string())
            print("\n  Sample violations:")
            print(violations.head())
    except (AttributeError, TypeError) as e:
        print(f"  (Skipped process() due to pandas compatibility: {e})")

    # Vectorized approach with all rules
    print("\n--- Vectorized Rule Application (all rules) ---")
    try:
        all_violations = spc.apply_rules_vectorized()
        print(f"  Total violations: {len(all_violations)}")
        if not all_violations.empty:
            print("\n  Violations by rule:")
            print(all_violations['rule'].value_counts().to_string())

        # Interpret violations
        if not all_violations.empty:
            print("\n--- Violation Interpretations ---")
            interpreted = spc.interpret_violations(all_violations)
            for _, row in interpreted.drop_duplicates(subset=['rule']).iterrows():
                print(f"\n  {row['rule']} ({row['severity']}):")
                print(f"    {row['interpretation']}")
                print(f"    Meaning: {row['meaning']}")
    except (AttributeError, TypeError) as e:
        print(f"  (Skipped vectorized rules due to pandas compatibility: {e})")

    # CUSUM shift detection
    print("\n--- CUSUM Shift Detection ---")
    shifts = spc.detect_cusum_shifts(k=0.5, h=5.0)
    print(f"  Shifts detected: {len(shifts)}")
    if not shifts.empty:
        print(shifts[['systime', 'value_double', 'shift_direction', 'severity']].head())


def demo_tolerance_deviation():
    """Demo 3: Tolerance deviation event detection."""
    print("\n" + "=" * 70)
    print("DEMO 3: Tolerance Deviation Events")
    print("=" * 70)

    df = create_tolerance_data()
    print(f"\nDataset: {len(df)} rows (upper tol + lower tol + actual measurements)")

    tol = ToleranceDeviationEvents(
        dataframe=df,
        tolerance_column='value_double',
        actual_column='value_double',
        actual_uuid='actual_meas',
        event_uuid='tol_violation',
        upper_tolerance_uuid='upper_tol',
        lower_tolerance_uuid='lower_tol',
        warning_threshold=0.8,
    )

    # Process tolerance deviations
    print("\n--- Processing Tolerance Deviations ---")
    events = tol.process_and_group_data_with_events()
    print(f"  Violation events found: {len(events)}")
    if not events.empty:
        print("\n  Event columns:", list(events.columns))
        if 'severity' in events.columns:
            print("\n  Severity breakdown:")
            print(events['severity'].value_counts().to_string())
        if 'deviation_abs' in events.columns:
            print(f"\n  Max absolute deviation: {events['deviation_abs'].max():.2f}")
        print("\n  Sample events:")
        print(events.head())

    # Process capability indices
    print("\n--- Process Capability Indices ---")
    try:
        indices = tol.compute_capability_indices()
        print(f"  Cp:  {indices['Cp']:.4f}")
        print(f"  Cpk: {indices['Cpk']:.4f}")
        print(f"  Pp:  {indices['Pp']:.4f}")
        print(f"  Ppk: {indices['Ppk']:.4f}")
        print(f"  Process Mean: {indices['mean']:.4f}")
        print(f"  Process Std:  {indices['std']:.4f}")
        print(f"  USL: {indices['usl']:.4f}, LSL: {indices['lsl']:.4f}")

        cpk = indices['Cpk']
        if cpk >= 1.67:
            assessment = "Excellent"
        elif cpk >= 1.33:
            assessment = "Acceptable"
        elif cpk >= 1.0:
            assessment = "Marginal"
        else:
            assessment = "Inadequate"
        print(f"\n  Assessment: {assessment} (Cpk={cpk:.4f})")
    except Exception as e:
        print(f"  Could not compute capability indices: {e}")


def main():
    """Run all quality event demonstrations."""
    print("\n" + "=" * 70)
    print("Quality Events Demonstration")
    print("=" * 70)

    try:
        demo_outlier_detection()
        demo_spc_rules()
        demo_tolerance_deviation()

        print("\n" + "=" * 70)
        print("All demonstrations completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
