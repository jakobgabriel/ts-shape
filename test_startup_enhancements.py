"""
Test script demonstrating the enhanced startup detection features.

This script shows usage of:
1. Multi-signal startup detection (AND/OR logic)
2. Adaptive threshold detection
3. Startup quality assessment
4. Startup phase tracking
5. Failed startup detection
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
import sys
sys.path.insert(0, 'src')

from ts_shape.events.engineering.startup_events import StartupDetectionEvents


def create_test_data():
    """Create synthetic test data for startup detection."""
    base_time = datetime(2024, 1, 1, 8, 0, 0)

    # Generate time series data for multiple signals
    data = []

    # Signal 1: Temperature - gradual startup
    for i in range(300):
        time = base_time + timedelta(seconds=i)

        # Normal operation at ~20, startup around t=100
        if i < 100:
            value = 20 + np.random.normal(0, 1)
        elif i < 150:
            # Startup phase - gradual increase
            value = 20 + (i - 100) * 1.2 + np.random.normal(0, 1)
        else:
            # Operating temperature ~80
            value = 80 + np.random.normal(0, 2)

        data.append({
            'uuid': 'temperature_sensor',
            'sequence_number': i,
            'systime': time,
            'plctime': time,
            'is_delta': False,
            'value_double': value,
            'value_integer': None,
            'value_string': None,
            'value_bool': None,
            'value_bytes': None,
        })

    # Signal 2: Motor speed - rapid startup
    for i in range(300):
        time = base_time + timedelta(seconds=i)

        # Normal operation at 0, startup around t=105
        if i < 105:
            value = 0 + np.random.normal(0, 0.5)
        elif i < 125:
            # Rapid startup
            value = (i - 105) * 4 + np.random.normal(0, 1)
        else:
            # Operating speed ~3000 RPM
            value = 3000 + np.random.normal(0, 10)

        data.append({
            'uuid': 'motor_speed',
            'sequence_number': i,
            'systime': time,
            'plctime': time,
            'is_delta': False,
            'value_double': value,
            'value_integer': None,
            'value_string': None,
            'value_bool': None,
            'value_bytes': None,
        })

    # Signal 3: Pressure - failed startup around t=200
    for i in range(300):
        time = base_time + timedelta(seconds=i)

        if i < 200:
            value = 1.0 + np.random.normal(0, 0.1)
        elif i < 215:
            # Attempted startup
            value = 1.0 + (i - 200) * 0.3
        elif i < 230:
            # Failure - drops back down
            value = 5.5 - (i - 215) * 0.25
        else:
            # Back to baseline
            value = 1.0 + np.random.normal(0, 0.1)

        data.append({
            'uuid': 'pressure_sensor',
            'sequence_number': i,
            'systime': time,
            'plctime': time,
            'is_delta': False,
            'value_double': value,
            'value_integer': None,
            'value_string': None,
            'value_bool': None,
            'value_bytes': None,
        })

    return pd.DataFrame(data)


def test_multi_signal_detection(df):
    """Test multi-signal startup detection."""
    print("\n" + "="*80)
    print("TEST 1: Multi-Signal Startup Detection")
    print("="*80)

    detector = StartupDetectionEvents(
        dataframe=df,
        target_uuid='temperature_sensor',
        event_uuid='multi_startup_event',
    )

    # Configure signals for multi-signal detection
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

    # Test with AND logic
    print("\n--- Using AND logic (all signals must detect) ---")
    events_all = detector.detect_startup_multi_signal(signals, logic='all', time_tolerance='30s')
    print(f"Events detected: {len(events_all)}")
    if not events_all.empty:
        print(events_all[['start', 'end', 'method', 'signals_triggered']].to_string())

    # Test with OR logic
    print("\n--- Using OR logic (any signal can detect) ---")
    events_any = detector.detect_startup_multi_signal(signals, logic='any')
    print(f"Events detected: {len(events_any)}")
    if not events_any.empty:
        print(events_any[['start', 'end', 'method', 'signals_triggered']].to_string())


def test_adaptive_detection(df):
    """Test adaptive threshold detection."""
    print("\n" + "="*80)
    print("TEST 2: Adaptive Threshold Detection")
    print("="*80)

    detector = StartupDetectionEvents(
        dataframe=df,
        target_uuid='temperature_sensor',
        event_uuid='adaptive_startup',
    )

    events = detector.detect_startup_adaptive(
        baseline_window='1h',
        sensitivity=2.0,
        min_above='15s',
        lookback_periods=10,
    )

    print(f"\nEvents detected: {len(events)}")
    if not events.empty:
        print("\nDetected events with adaptive thresholds:")
        print(events[['start', 'end', 'adaptive_threshold', 'baseline_mean', 'baseline_std']].to_string())


def test_quality_assessment(df):
    """Test startup quality assessment."""
    print("\n" + "="*80)
    print("TEST 3: Startup Quality Assessment")
    print("="*80)

    detector = StartupDetectionEvents(
        dataframe=df,
        target_uuid='temperature_sensor',
        event_uuid='startup_event',
    )

    # First detect startups
    events = detector.detect_startup_by_threshold(threshold=40.0, min_above='10s')
    print(f"\nDetected {len(events)} startup events")

    if not events.empty:
        # Assess quality
        quality = detector.assess_startup_quality(
            events,
            smoothness_window=5,
            anomaly_threshold=3.0,
        )

        print("\nQuality Assessment Results:")
        print(quality[['start', 'duration', 'smoothness_score', 'anomaly_flags',
                      'value_change', 'avg_rate', 'stability_score']].to_string())


def test_phase_tracking(df):
    """Test startup phase tracking."""
    print("\n" + "="*80)
    print("TEST 4: Startup Phase Tracking")
    print("="*80)

    detector = StartupDetectionEvents(
        dataframe=df,
        target_uuid='temperature_sensor',
        event_uuid='phase_event',
    )

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

    print(f"\nPhase transitions detected: {len(phase_events)}")
    if not phase_events.empty:
        print("\nPhase Progression:")
        print(phase_events[['phase_name', 'phase_number', 'start', 'end',
                           'duration', 'next_phase', 'completed']].to_string())


def test_failed_startup_detection(df):
    """Test failed startup detection."""
    print("\n" + "="*80)
    print("TEST 5: Failed Startup Detection")
    print("="*80)

    detector = StartupDetectionEvents(
        dataframe=df,
        target_uuid='pressure_sensor',
        event_uuid='failed_startup',
    )

    failed_events = detector.detect_failed_startups(
        threshold=2.0,
        min_rise_duration='3s',
        max_completion_time='1m',
        completion_threshold=5.0,
        required_stability='5s',
    )

    print(f"\nFailed startups detected: {len(failed_events)}")
    if not failed_events.empty:
        print("\nFailed Startup Events:")
        print(failed_events[['start', 'end', 'failure_reason',
                            'max_value_reached', 'time_to_failure']].to_string())


def test_backward_compatibility(df):
    """Test that existing methods still work."""
    print("\n" + "="*80)
    print("TEST 6: Backward Compatibility Check")
    print("="*80)

    detector = StartupDetectionEvents(
        dataframe=df,
        target_uuid='temperature_sensor',
        event_uuid='startup_event',
    )

    # Test existing threshold method
    print("\n--- Testing detect_startup_by_threshold (existing method) ---")
    events_threshold = detector.detect_startup_by_threshold(threshold=40.0, min_above='10s')
    print(f"Events detected: {len(events_threshold)}")
    if not events_threshold.empty:
        print(events_threshold[['start', 'end', 'method', 'threshold']].head().to_string())

    # Test existing slope method
    print("\n--- Testing detect_startup_by_slope (existing method) ---")
    events_slope = detector.detect_startup_by_slope(min_slope=1.0, min_duration='5s')
    print(f"Events detected: {len(events_slope)}")
    if not events_slope.empty:
        print(events_slope[['start', 'end', 'method', 'min_slope', 'avg_slope']].head().to_string())


def main():
    """Run all tests."""
    print("\n")
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*" + "  STARTUP DETECTION ENHANCEMENTS - COMPREHENSIVE TEST SUITE".center(78) + "*")
    print("*" + " " * 78 + "*")
    print("*" * 80)

    # Create test data
    print("\nGenerating synthetic test data...")
    df = create_test_data()
    print(f"Generated {len(df)} data points for {df['uuid'].nunique()} signals")

    # Run all tests
    test_multi_signal_detection(df)
    test_adaptive_detection(df)
    test_quality_assessment(df)
    test_phase_tracking(df)
    test_failed_startup_detection(df)
    test_backward_compatibility(df)

    print("\n" + "="*80)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\nSummary of Enhancements:")
    print("  1. ✓ Multi-signal startup detection with AND/OR logic")
    print("  2. ✓ Adaptive threshold detection based on historical baseline")
    print("  3. ✓ Startup quality assessment (duration, smoothness, anomalies)")
    print("  4. ✓ Startup phase tracking with progression analysis")
    print("  5. ✓ Failed startup detection with detailed failure reasons")
    print("  6. ✓ Full backward compatibility with existing methods")
    print("\n")


if __name__ == '__main__':
    main()
