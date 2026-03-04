#!/usr/bin/env python3
"""
Demonstration of maintenance event detection in ts-shape.

This script shows how to use:
1. DegradationDetectionEvents (trend degradation, variance increase, level shift, health score)
2. FailurePredictionEvents (remaining useful life, exceedance patterns)
3. VibrationAnalysisEvents (RMS exceedance, amplitude growth, bearing health)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import ts_shape
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ts_shape.events.maintenance.degradation_detection import DegradationDetectionEvents
from ts_shape.events.maintenance.failure_prediction import FailurePredictionEvents
from ts_shape.events.maintenance.vibration_analysis import VibrationAnalysisEvents


def create_degradation_data():
    """Create synthetic signal that degrades over time."""
    np.random.seed(42)
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    n_points = 500

    timestamps = [start_time + timedelta(minutes=i * 5) for i in range(n_points)]

    # Healthy baseline for first 200 points, then gradual degradation
    values = np.zeros(n_points)
    for i in range(n_points):
        noise = np.random.normal(0, 0.5)
        if i < 200:
            values[i] = 100.0 + noise
        elif i < 350:
            # Gradual decrease (trend degradation)
            values[i] = 100.0 - (i - 200) * 0.05 + noise
        else:
            # Faster degradation with increased variance
            values[i] = 100.0 - (i - 200) * 0.08 + np.random.normal(0, 2.0)

    # Inject a level shift at point 150
    values[150:] += -3.0

    rows = []
    for i in range(n_points):
        rows.append({
            'systime': timestamps[i],
            'uuid': 'bearing_temp',
            'value_double': values[i],
            'is_delta': True,
        })

    return pd.DataFrame(rows)


def create_failure_prediction_data():
    """Create synthetic signal approaching failure threshold."""
    np.random.seed(88)
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    n_points = 300

    timestamps = [start_time + timedelta(minutes=i * 10) for i in range(n_points)]

    # Signal gradually increasing toward failure threshold (200)
    values = np.zeros(n_points)
    for i in range(n_points):
        base = 100.0 + i * 0.25
        noise = np.random.normal(0, 2.0)
        # Occasional warning-level exceedances
        if i > 200 and np.random.random() > 0.9:
            noise += 15.0
        values[i] = base + noise

    rows = []
    for i in range(n_points):
        rows.append({
            'systime': timestamps[i],
            'uuid': 'motor_vibration',
            'value_double': values[i],
            'is_delta': True,
        })

    return pd.DataFrame(rows)


def create_vibration_data():
    """Create synthetic vibration signal with growing amplitude."""
    np.random.seed(55)
    start_time = datetime(2024, 1, 1, 0, 0, 0)
    n_points = 600

    timestamps = [start_time + timedelta(seconds=i * 10) for i in range(n_points)]

    # Vibration signal: sinusoidal with growing amplitude
    values = np.zeros(n_points)
    for i in range(n_points):
        # Base vibration
        amplitude = 1.0 + (i / n_points) * 3.0  # amplitude grows from 1 to 4
        freq = 0.1  # Hz
        values[i] = amplitude * np.sin(2 * np.pi * freq * i * 10) + np.random.normal(0, 0.3)

    rows = []
    for i in range(n_points):
        rows.append({
            'systime': timestamps[i],
            'uuid': 'accel_sensor_x',
            'value_double': values[i],
            'is_delta': True,
        })

    return pd.DataFrame(rows)


def demo_degradation_detection():
    """Demo 1: Degradation detection (trend, variance, level shift, health score)."""
    print("\n" + "=" * 70)
    print("DEMO 1: Degradation Detection Events")
    print("=" * 70)

    df = create_degradation_data()
    print(f"\nDataset: {len(df)} data points over ~{len(df)*5/60:.0f} hours")

    detector = DegradationDetectionEvents(
        dataframe=df,
        signal_uuid='bearing_temp',
        event_uuid='maint:degradation',
        value_column='value_double',
    )

    # Trend degradation
    print("\n--- Trend Degradation (decreasing, window=2h) ---")
    trends = detector.detect_trend_degradation(
        window='2h',
        min_slope=0.0001,
        direction='decreasing',
    )
    print(f"  Degradation intervals found: {len(trends)}")
    if not trends.empty:
        print(trends[['start', 'end', 'avg_slope', 'total_change', 'duration_seconds']].to_string())

    # Variance increase
    print("\n--- Variance Increase (threshold_factor=2.0) ---")
    variance_events = detector.detect_variance_increase(
        window='2h',
        threshold_factor=2.0,
    )
    print(f"  Variance increase intervals: {len(variance_events)}")
    if not variance_events.empty:
        print(variance_events[['start', 'end', 'baseline_variance', 'current_variance', 'ratio']].to_string())

    # Level shift
    print("\n--- Level Shift Detection (min_shift=2.0) ---")
    shifts = detector.detect_level_shift(min_shift=2.0, hold='10m')
    print(f"  Level shifts detected: {len(shifts)}")
    if not shifts.empty:
        print(shifts[['systime', 'shift_magnitude', 'prev_mean', 'new_mean']].to_string())

    # Health score
    print("\n--- Health Score (rolling 2h window) ---")
    health = detector.health_score(window='2h', baseline_window='6h')
    if not health.empty:
        print(f"  Data points: {len(health)}")
        print(f"  Initial health: {health['health_score'].iloc[:10].mean():.1f}")
        print(f"  Final health:   {health['health_score'].iloc[-10:].mean():.1f}")
        print(f"  Min health:     {health['health_score'].min():.1f}")
        print("\n  Last 5 health readings:")
        print(health[['systime', 'health_score', 'mean_drift_pct', 'variance_ratio']].tail().to_string())


def demo_failure_prediction():
    """Demo 2: Failure prediction (RUL, exceedance patterns)."""
    print("\n" + "=" * 70)
    print("DEMO 2: Failure Prediction Events")
    print("=" * 70)

    df = create_failure_prediction_data()
    print(f"\nDataset: {len(df)} data points, signal increasing toward failure")

    predictor = FailurePredictionEvents(
        dataframe=df,
        signal_uuid='motor_vibration',
        event_uuid='maint:failure_pred',
        value_column='value_double',
    )

    # Remaining useful life
    print("\n--- Remaining Useful Life (failure_threshold=200) ---")
    rul = predictor.remaining_useful_life(
        degradation_rate=0.0005,
        failure_threshold=200.0,
    )
    if not rul.empty:
        print(f"  RUL estimates: {len(rul)}")
        # Show RUL at beginning, middle, and end
        indices = [0, len(rul) // 4, len(rul) // 2, 3 * len(rul) // 4, len(rul) - 1]
        sample = rul.iloc[indices]
        print(sample[['systime', 'current_value', 'rul_hours', 'confidence']].to_string())

        print(f"\n  Initial RUL: {rul['rul_hours'].iloc[0]:.1f} hours")
        last_valid = rul[rul['rul_hours'].notna()].iloc[-1]
        print(f"  Final RUL:   {last_valid['rul_hours']:.1f} hours")

    # Exceedance patterns
    print("\n--- Exceedance Pattern Detection ---")
    exceedances = predictor.detect_exceedance_pattern(
        warning_threshold=150.0,
        critical_threshold=180.0,
        window='4h',
    )
    if not exceedances.empty:
        print(f"  Windows analyzed: {len(exceedances)}")
        escalating = exceedances[exceedances['escalation_detected']]
        print(f"  Escalation windows: {len(escalating)}")
        print(exceedances[['window_start', 'warning_count', 'critical_count',
                           'escalation_detected']].tail(10).to_string())

    # Time to threshold
    print("\n--- Time to Threshold (threshold=180) ---")
    ttt = predictor.time_to_threshold(threshold=180.0, direction='increasing')
    if not ttt.empty:
        valid_ttt = ttt[ttt['estimated_time_seconds'].notna()]
        if not valid_ttt.empty:
            last_estimate = valid_ttt.iloc[-1]
            print(f"  Latest estimate: {last_estimate['estimated_time_seconds']/3600:.1f} hours "
                  f"(current value: {last_estimate['current_value']:.1f})")
            print(f"  Rate of change: {last_estimate['rate_of_change']:.6f} per second")


def demo_vibration_analysis():
    """Demo 3: Vibration analysis (RMS, amplitude, bearing health)."""
    print("\n" + "=" * 70)
    print("DEMO 3: Vibration Analysis Events")
    print("=" * 70)

    df = create_vibration_data()
    print(f"\nDataset: {len(df)} vibration samples")

    analyzer = VibrationAnalysisEvents(
        dataframe=df,
        signal_uuid='accel_sensor_x',
        event_uuid='maint:vibration',
        value_column='value_double',
    )

    # RMS exceedance
    print("\n--- RMS Exceedance (baseline_rms=1.0, threshold=1.5x) ---")
    rms_events = analyzer.detect_rms_exceedance(
        baseline_rms=1.0,
        threshold_factor=1.5,
        window='2min',
    )
    print(f"  RMS exceedance intervals: {len(rms_events)}")
    if not rms_events.empty:
        print(rms_events[['start', 'end', 'rms_value', 'ratio', 'duration_seconds']].to_string())

    # Amplitude growth
    print("\n--- Amplitude Growth (10-minute windows) ---")
    amp_growth = analyzer.detect_amplitude_growth(
        window='10min',
        growth_threshold=0.2,
    )
    if not amp_growth.empty:
        print(f"  Windows analyzed: {len(amp_growth)}")
        growing = amp_growth[amp_growth['growth_pct'] > 0.2]
        print(f"  Windows with significant growth (>20%): {len(growing)}")
        print(amp_growth[['window_start', 'amplitude', 'baseline_amplitude',
                          'growth_pct']].tail(8).to_string())

    # Bearing health indicators
    print("\n--- Bearing Health Indicators (5-minute windows) ---")
    health = analyzer.bearing_health_indicators(window='5min')
    if not health.empty:
        print(f"  Windows: {len(health)}")
        print(health[['window_start', 'rms', 'peak', 'crest_factor', 'kurtosis']].to_string())

        print(f"\n  Initial RMS: {health['rms'].iloc[0]:.4f}")
        print(f"  Final RMS:   {health['rms'].iloc[-1]:.4f}")
        print(f"  RMS growth:  {(health['rms'].iloc[-1] / health['rms'].iloc[0] - 1) * 100:.1f}%")

        # Kurtosis trend (high kurtosis indicates impulsive impacts, bearing defects)
        print(f"\n  Initial kurtosis: {health['kurtosis'].iloc[0]:.4f}")
        print(f"  Final kurtosis:   {health['kurtosis'].iloc[-1]:.4f}")
        print("  (Normal ~3.0; elevated kurtosis suggests developing bearing defects)")


def main():
    """Run all maintenance event demonstrations."""
    print("\n" + "=" * 70)
    print("Maintenance Events Demonstration")
    print("=" * 70)

    try:
        demo_degradation_detection()
        demo_failure_prediction()
        demo_vibration_analysis()

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
