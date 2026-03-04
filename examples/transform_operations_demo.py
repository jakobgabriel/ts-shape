#!/usr/bin/env python3
"""
Demonstration of transform operations in ts-shape.

This script shows how to use:
1. IntegerFilter, DoubleFilter (numeric filtering)
2. StringFilter (string filtering and change detection)
3. BooleanFilter, IsDeltaFilter (boolean edge detection)
4. IntegerCalc (arithmetic operations on columns)
5. TimestampConverter (epoch to datetime conversion)
6. TimezoneShift (timezone conversion)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import ts_shape
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ts_shape.transform.filter.numeric_filter import IntegerFilter, DoubleFilter
from ts_shape.transform.filter.string_filter import StringFilter
from ts_shape.transform.filter.boolean_filter import BooleanFilter, IsDeltaFilter
from ts_shape.transform.calculator.numeric_calc import IntegerCalc
from ts_shape.transform.time_functions.timestamp_converter import TimestampConverter
from ts_shape.transform.time_functions.timezone_shift import TimezoneShift


def create_sample_data():
    """Create synthetic timeseries data for transformation demonstrations."""
    np.random.seed(42)
    n = 50

    start_time = datetime(2024, 1, 1, 8, 0, 0)
    timestamps = [start_time + timedelta(minutes=i * 10) for i in range(n)]

    df = pd.DataFrame({
        'systime': pd.to_datetime(timestamps),
        'uuid': np.random.choice(['sensor_a', 'sensor_b', 'sensor_c'], n),
        'value_integer': np.random.randint(0, 100, n),
        'value_double': np.random.normal(50.0, 10.0, n),
        'value_string': np.random.choice(
            ['RUNNING', 'STOPPED', 'IDLE', 'MAINTENANCE', None],
            n, p=[0.5, 0.2, 0.15, 0.1, 0.05],
        ),
        'value_bool': [True, False] * 15 + [True] * 10 + [False] * 10,
        'is_delta': [True] * 45 + [False] * 5,
    })

    # Inject some NaN values in value_double
    nan_indices = np.random.choice(n, 5, replace=False)
    df.loc[nan_indices, 'value_double'] = np.nan

    return df


def create_epoch_data():
    """Create data with epoch timestamps for conversion demo."""
    base_epoch_ns = int(datetime(2024, 1, 1, 12, 0, 0).timestamp() * 1e9)
    n = 10

    df = pd.DataFrame({
        'timestamp_ns': [base_epoch_ns + i * int(60e9) for i in range(n)],
        'value': np.random.normal(25.0, 3.0, n),
    })

    return df


def demo_integer_filter():
    """Demo 1: Integer column filtering."""
    print("\n" + "=" * 70)
    print("DEMO 1: Integer Filter")
    print("=" * 70)

    df = create_sample_data()
    print(f"\nOriginal: {len(df)} rows, value_integer range: "
          f"[{df['value_integer'].min()}, {df['value_integer'].max()}]")

    # Exact match
    print("\n--- Filter: value_integer == 50 ---")
    matched = IntegerFilter.filter_value_integer_match(df, 'value_integer', 50)
    print(f"  Rows matching: {len(matched)}")

    # Not match
    print("\n--- Filter: value_integer != 0 ---")
    not_zero = IntegerFilter.filter_value_integer_not_match(df, 'value_integer', 0)
    print(f"  Rows not zero: {len(not_zero)}")

    # Between
    print("\n--- Filter: 20 <= value_integer <= 60 ---")
    between = IntegerFilter.filter_value_integer_between(df, 'value_integer', 20, 60)
    print(f"  Rows in range: {len(between)}")
    print(between[['systime', 'value_integer']].head().to_string())


def demo_double_filter():
    """Demo 2: Double (floating-point) column filtering."""
    print("\n" + "=" * 70)
    print("DEMO 2: Double Filter")
    print("=" * 70)

    df = create_sample_data()
    nan_count = df['value_double'].isna().sum()
    print(f"\nOriginal: {len(df)} rows, {nan_count} NaN values in value_double")

    # Filter out NaN
    print("\n--- Filter: Remove NaN from value_double ---")
    no_nan = DoubleFilter.filter_nan_value_double(df, 'value_double')
    print(f"  Rows after removing NaN: {len(no_nan)}")

    # Between range
    print("\n--- Filter: 40.0 <= value_double <= 60.0 ---")
    in_range = DoubleFilter.filter_value_double_between(df, 'value_double', 40.0, 60.0)
    print(f"  Rows in range: {len(in_range)}")
    if not in_range.empty:
        print(in_range[['systime', 'value_double']].head().to_string())


def demo_string_filter():
    """Demo 3: String column filtering and change detection."""
    print("\n" + "=" * 70)
    print("DEMO 3: String Filter")
    print("=" * 70)

    df = create_sample_data()
    print(f"\nOriginal: {len(df)} rows")
    print(f"  String values distribution:")
    print(df['value_string'].value_counts(dropna=False).to_string())

    # Filter NA
    print("\n--- Filter: Remove NA strings ---")
    no_na = StringFilter.filter_na_value_string(df, 'value_string')
    print(f"  Rows after removing NA: {len(no_na)}")

    # Exact match
    print("\n--- Filter: value_string == 'RUNNING' ---")
    running = StringFilter.filter_value_string_match(df, 'RUNNING', 'value_string')
    print(f"  Rows matching 'RUNNING': {len(running)}")

    # Not match
    print("\n--- Filter: value_string != 'RUNNING' ---")
    not_running = StringFilter.filter_value_string_not_match(df, 'RUNNING', 'value_string')
    print(f"  Rows not 'RUNNING': {len(not_running)}")

    # Contains substring
    print("\n--- Filter: value_string contains 'STOP' ---")
    has_stop = StringFilter.filter_string_contains(df, 'STOP', 'value_string')
    print(f"  Rows containing 'STOP': {len(has_stop)}")

    # Detect changes
    print("\n--- Detect String Value Changes ---")
    changes = StringFilter.detect_changes_in_string(df, 'value_string')
    print(f"  Rows where value changed: {len(changes)}")
    if not changes.empty:
        print(changes[['systime', 'value_string']].head(10).to_string())


def demo_boolean_filter():
    """Demo 4: Boolean filtering and edge detection."""
    print("\n" + "=" * 70)
    print("DEMO 4: Boolean Filter & IsDelta Filter")
    print("=" * 70)

    df = create_sample_data()
    print(f"\nOriginal: {len(df)} rows")

    # Rising edge (False -> True)
    print("\n--- Rising Edge: value_bool False -> True ---")
    rising = BooleanFilter.filter_raising_value_bool(df.copy(), 'value_bool')
    print(f"  Rising edges detected: {len(rising)}")
    if not rising.empty:
        print(rising[['systime', 'value_bool']].head().to_string())

    # Falling edge (True -> False)
    print("\n--- Falling Edge: value_bool True -> False ---")
    falling = BooleanFilter.filter_falling_value_bool(df.copy(), 'value_bool')
    print(f"  Falling edges detected: {len(falling)}")
    if not falling.empty:
        print(falling[['systime', 'value_bool']].head().to_string())

    # IsDelta filter
    print("\n--- IsDelta Filter ---")
    delta_true = IsDeltaFilter.filter_is_delta_true(df, 'is_delta')
    delta_false = IsDeltaFilter.filter_is_delta_false(df, 'is_delta')
    print(f"  is_delta=True:  {len(delta_true)} rows")
    print(f"  is_delta=False: {len(delta_false)} rows")


def demo_integer_calc():
    """Demo 5: Arithmetic operations on integer columns."""
    print("\n" + "=" * 70)
    print("DEMO 5: Integer Calculator")
    print("=" * 70)

    df = create_sample_data()
    col = 'value_integer'
    print(f"\nOriginal values (first 5): {df[col].head().tolist()}")

    # Scale
    scaled = IntegerCalc.scale_column(df.copy(), col, factor=2.0)
    print(f"\n--- Scale by 2.0 ---")
    print(f"  Result: {scaled[col].head().tolist()}")

    # Offset
    offset = IntegerCalc.offset_column(df.copy(), col, offset_value=100)
    print(f"\n--- Offset by +100 ---")
    print(f"  Result: {offset[col].head().tolist()}")

    # Divide
    divided = IntegerCalc.divide_column(df.copy(), col, divisor=10)
    print(f"\n--- Divide by 10 ---")
    print(f"  Result: {divided[col].head().tolist()}")

    # Subtract
    subtracted = IntegerCalc.subtract_column(df.copy(), col, subtract_value=25)
    print(f"\n--- Subtract 25 ---")
    print(f"  Result: {subtracted[col].head().tolist()}")

    # Combined: multiply then add
    combined = IntegerCalc.calculate_with_fixed_factors(df.copy(), col, multiply_factor=1.8, add_factor=32)
    print(f"\n--- Linear transform: value * 1.8 + 32 (Celsius to Fahrenheit) ---")
    print(f"  Result: {combined[col].head().tolist()}")

    # Modulo
    modulo = IntegerCalc.mod_column(df.copy(), col, mod_value=10)
    print(f"\n--- Modulo 10 ---")
    print(f"  Result: {modulo[col].head().tolist()}")

    # Power
    powered = IntegerCalc.power_column(df.copy(), col, power_value=2)
    print(f"\n--- Power of 2 ---")
    print(f"  Result: {powered[col].head().tolist()}")


def demo_timestamp_converter():
    """Demo 6: Epoch timestamp conversion."""
    print("\n" + "=" * 70)
    print("DEMO 6: Timestamp Converter")
    print("=" * 70)

    df = create_epoch_data()
    print(f"\nOriginal epoch timestamps (nanoseconds):")
    print(df[['timestamp_ns', 'value']].to_string(index=False))

    # Convert nanosecond timestamps to UTC datetime
    print("\n--- Convert ns epochs to UTC datetime ---")
    converted = TimestampConverter.convert_to_datetime(
        df, columns=['timestamp_ns'], unit='ns', timezone='UTC',
    )
    print(converted[['timestamp_ns', 'value']].to_string(index=False))

    # Convert to specific timezone
    print("\n--- Convert ns epochs to US/Eastern ---")
    eastern = TimestampConverter.convert_to_datetime(
        df, columns=['timestamp_ns'], unit='ns', timezone='US/Eastern',
    )
    print(eastern[['timestamp_ns', 'value']].to_string(index=False))


def demo_timezone_shift():
    """Demo 7: Timezone shifting operations."""
    print("\n" + "=" * 70)
    print("DEMO 7: Timezone Shift")
    print("=" * 70)

    # Create data with naive timestamps
    n = 5
    start_time = datetime(2024, 1, 1, 12, 0, 0)
    df = pd.DataFrame({
        'systime': pd.to_datetime([start_time + timedelta(hours=i) for i in range(n)]),
        'value': range(n),
    })
    print(f"\nOriginal (naive timestamps):")
    print(df.to_string(index=False))

    # Check timezone awareness
    print(f"\n  Timezone-aware: {TimezoneShift.detect_timezone_awareness(df, 'systime')}")

    # Shift from UTC to US/Eastern
    print("\n--- Shift UTC -> US/Eastern ---")
    shifted = TimezoneShift.shift_timezone(df.copy(), 'systime', 'UTC', 'US/Eastern')
    print(shifted.to_string(index=False))
    print(f"  Timezone-aware: {TimezoneShift.detect_timezone_awareness(shifted, 'systime')}")

    # Add a timezone column without modifying the original
    print("\n--- Add Europe/Berlin Column ---")
    df_naive = pd.DataFrame({
        'systime': pd.to_datetime([start_time + timedelta(hours=i) for i in range(n)]),
        'value': range(n),
    })
    with_tz = TimezoneShift.add_timezone_column(
        df_naive, 'systime', 'UTC', 'Europe/Berlin',
    )
    print(with_tz.to_string(index=False))

    # Revert timezone
    print("\n--- Revert US/Eastern -> UTC ---")
    reverted = TimezoneShift.revert_to_original_timezone(shifted, 'systime', 'UTC')
    print(reverted.to_string(index=False))

    # Calculate time difference
    print("\n--- Time Difference Between Columns ---")
    df_two_times = pd.DataFrame({
        'start_time': pd.to_datetime([
            datetime(2024, 1, 1, 8, 0), datetime(2024, 1, 1, 9, 30),
        ]),
        'end_time': pd.to_datetime([
            datetime(2024, 1, 1, 10, 15), datetime(2024, 1, 1, 12, 0),
        ]),
    })
    time_diff = TimezoneShift.calculate_time_difference(df_two_times, 'start_time', 'end_time')
    print(f"  Time differences (seconds): {time_diff.tolist()}")


def main():
    """Run all transform operation demonstrations."""
    print("\n" + "=" * 70)
    print("Transform Operations Demonstration")
    print("=" * 70)

    try:
        demo_integer_filter()
        demo_double_filter()
        demo_string_filter()
        demo_boolean_filter()
        demo_integer_calc()
        demo_timestamp_converter()
        demo_timezone_shift()

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
