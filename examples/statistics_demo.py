#!/usr/bin/env python3
"""
Demonstration of statistics features in ts-shape.

This script shows how to use:
1. NumericStatistics (comprehensive numeric column statistics)
2. StringStatistics (string column analysis)
3. BooleanStatistics (boolean column analysis)
4. TimestampStatistics (timestamp column analysis)
5. TimeGroupedStatistics (time-windowed aggregations)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import ts_shape
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ts_shape.features.stats.numeric_stats import NumericStatistics
from ts_shape.features.stats.string_stats import StringStatistics
from ts_shape.features.stats.boolean_stats import BooleanStatistics
from ts_shape.features.stats.timestamp_stats import TimestampStatistics
from ts_shape.features.time_stats.time_stats_numeric import TimeGroupedStatistics


def create_sample_dataframe():
    """Create a synthetic DataFrame with multiple column types."""
    np.random.seed(42)
    n = 200

    start_time = datetime(2024, 1, 1, 8, 0, 0)
    timestamps = [start_time + timedelta(minutes=i * 5) for i in range(n)]

    df = pd.DataFrame({
        'systime': pd.to_datetime(timestamps),
        'value_double': np.random.normal(100.0, 15.0, n),
        'value_integer': np.random.randint(0, 50, n),
        'value_string': np.random.choice(
            ['PRODUCT_A', 'PRODUCT_B', 'PRODUCT_C', 'PRODUCT_D', None],
            n, p=[0.35, 0.30, 0.20, 0.10, 0.05],
        ),
        'value_bool': np.random.choice(
            [True, False, None],
            n, p=[0.6, 0.35, 0.05],
        ),
    })

    return df


def demo_numeric_statistics():
    """Demo 1: Numeric column statistics."""
    print("\n" + "=" * 70)
    print("DEMO 1: Numeric Statistics")
    print("=" * 70)

    df = create_sample_dataframe()
    col = 'value_double'
    print(f"\nAnalyzing column '{col}' ({len(df)} rows)")

    # Individual statistics
    print("\n--- Individual Statistics ---")
    print(f"  Mean:     {NumericStatistics.column_mean(df, col):.4f}")
    print(f"  Median:   {NumericStatistics.column_median(df, col):.4f}")
    print(f"  Std Dev:  {NumericStatistics.column_std(df, col):.4f}")
    print(f"  Variance: {NumericStatistics.column_variance(df, col):.4f}")
    print(f"  Min:      {NumericStatistics.column_min(df, col):.4f}")
    print(f"  Max:      {NumericStatistics.column_max(df, col):.4f}")
    print(f"  Range:    {NumericStatistics.column_range(df, col):.4f}")
    print(f"  IQR:      {NumericStatistics.column_iqr(df, col):.4f}")
    print(f"  Skewness: {NumericStatistics.column_skewness(df, col):.4f}")
    print(f"  Kurtosis: {NumericStatistics.column_kurtosis(df, col):.4f}")

    # Quantiles
    print("\n--- Quantiles ---")
    print(f"  Q1 (25%): {NumericStatistics.column_quantile(df, col, 0.25):.4f}")
    print(f"  Q2 (50%): {NumericStatistics.column_quantile(df, col, 0.50):.4f}")
    print(f"  Q3 (75%): {NumericStatistics.column_quantile(df, col, 0.75):.4f}")
    print(f"  P90:      {NumericStatistics.column_quantile(df, col, 0.90):.4f}")

    # Derived measures
    print("\n--- Derived Measures ---")
    cv = NumericStatistics.coefficient_of_variation(df, col)
    print(f"  Coefficient of Variation: {cv:.4f}" if cv else "  Coefficient of Variation: N/A")
    print(f"  Standard Error of Mean:   {NumericStatistics.standard_error_mean(df, col):.4f}")

    # Summary as DataFrame
    print("\n--- Full Summary (as DataFrame) ---")
    try:
        summary_df = NumericStatistics.summary_as_dataframe(df, col)
        for col_name in summary_df.columns:
            val = summary_df[col_name].iloc[0]
            if isinstance(val, float):
                print(f"  {col_name}: {val:.4f}")
            else:
                print(f"  {col_name}: {val}")
    except AttributeError as e:
        # pandas >= 2.0 removed Series.mad(); skip gracefully
        print(f"  (Skipped: {e} -- use individual methods instead)")

    # Built-in describe
    print("\n--- pandas describe() ---")
    desc = NumericStatistics.describe(df[['value_double', 'value_integer']])
    print(desc.to_string())


def demo_string_statistics():
    """Demo 2: String column statistics."""
    print("\n" + "=" * 70)
    print("DEMO 2: String Statistics")
    print("=" * 70)

    df = create_sample_dataframe()
    col = 'value_string'
    print(f"\nAnalyzing column '{col}' ({len(df)} rows)")

    print("\n--- Basic String Statistics ---")
    print(f"  Unique values:   {StringStatistics.count_unique(df, col)}")
    print(f"  Most frequent:   {StringStatistics.most_frequent(df, col)}")
    print(f"  Count of most frequent: {StringStatistics.count_most_frequent(df, col)}")
    print(f"  Null count:      {StringStatistics.count_null(df, col)}")
    print(f"  Avg string length: {StringStatistics.average_string_length(df, col):.1f}")
    print(f"  Longest string:  {StringStatistics.longest_string(df, col)}")
    print(f"  Shortest string: {StringStatistics.shortest_string(df, col)}")

    print("\n--- Top 3 Most Common Strings ---")
    top3 = StringStatistics.most_common_n_strings(df, 3, col)
    print(top3.to_string())

    print("\n--- Pattern Matching ---")
    print(f"  Contains 'PRODUCT': {StringStatistics.contains_substring_count(df, 'PRODUCT', col)}")
    print(f"  Starts with 'P':    {StringStatistics.starts_with_count(df, 'P', col)}")
    print(f"  Contains digits:    {StringStatistics.contains_digit_count(df, col)}")
    print(f"  Uppercase pct:      {StringStatistics.uppercase_percentage(df, col):.1f}%")

    print("\n--- String Length Summary ---")
    length_summary = StringStatistics.string_length_summary(df, col)
    print(length_summary.to_string(index=False))

    # Full summary
    print("\n--- Full Summary ---")
    summary = StringStatistics.summary_as_dict(df, col)
    for key, value in summary.items():
        print(f"  {key}: {value}")


def demo_boolean_statistics():
    """Demo 3: Boolean column statistics."""
    print("\n" + "=" * 70)
    print("DEMO 3: Boolean Statistics")
    print("=" * 70)

    df = create_sample_dataframe()
    col = 'value_bool'
    print(f"\nAnalyzing column '{col}' ({len(df)} rows)")

    print("\n--- Boolean Statistics ---")
    print(f"  True count:      {BooleanStatistics.count_true(df, col)}")
    print(f"  False count:     {BooleanStatistics.count_false(df, col)}")
    print(f"  Null count:      {BooleanStatistics.count_null(df, col)}")
    print(f"  Not-null count:  {BooleanStatistics.count_not_null(df, col)}")
    print(f"  True percentage: {BooleanStatistics.true_percentage(df, col):.1f}%")
    print(f"  False percentage:{BooleanStatistics.false_percentage(df, col):.1f}%")
    print(f"  Mode:            {BooleanStatistics.mode(df, col)}")
    print(f"  Is balanced:     {BooleanStatistics.is_balanced(df, col)}")

    # Full summary as DataFrame
    print("\n--- Full Summary ---")
    summary_df = BooleanStatistics.summary_as_dataframe(df, col)
    print(summary_df.to_string(index=False))


def demo_timestamp_statistics():
    """Demo 4: Timestamp column statistics."""
    print("\n" + "=" * 70)
    print("DEMO 4: Timestamp Statistics")
    print("=" * 70)

    df = create_sample_dataframe()
    col = 'systime'
    print(f"\nAnalyzing column '{col}' ({len(df)} rows)")

    print("\n--- Timestamp Range ---")
    print(f"  Earliest:         {TimestampStatistics.earliest_timestamp(df, col)}")
    print(f"  Latest:           {TimestampStatistics.latest_timestamp(df, col)}")
    print(f"  Time range:       {TimestampStatistics.timestamp_range(df, col)}")
    print(f"  Median timestamp: {TimestampStatistics.median_timestamp(df, col)}")

    print("\n--- Time Gap Analysis ---")
    print(f"  Average time gap: {TimestampStatistics.average_time_gap(df, col)}")
    print(f"  Std dev of gaps:  {TimestampStatistics.standard_deviation_timestamps(df, col)}")

    print("\n--- Distribution ---")
    print(f"  Most frequent hour: {TimestampStatistics.most_frequent_hour(df, col)}")
    print(f"  Most frequent day:  {TimestampStatistics.most_frequent_day(df, col)}")
    print(f"  Null timestamps:    {TimestampStatistics.count_null(df, col)}")
    print(f"  Valid timestamps:   {TimestampStatistics.count_not_null(df, col)}")

    print("\n--- Hour Distribution ---")
    hour_dist = TimestampStatistics.hour_distribution(df, col)
    print(hour_dist.sort_index().to_string())

    print("\n--- Top Activity Days ---")
    top_days = TimestampStatistics.days_with_most_activity(df, col, n=3)
    print(top_days.to_string())


def demo_time_grouped_statistics():
    """Demo 5: Time-grouped statistics."""
    print("\n" + "=" * 70)
    print("DEMO 5: Time-Grouped Statistics")
    print("=" * 70)

    df = create_sample_dataframe()
    print(f"\nDataset: {len(df)} rows, grouped by 1-hour windows")

    # Single statistic
    print("\n--- Hourly Mean ---")
    hourly_mean = TimeGroupedStatistics.calculate_statistic(
        df, 'systime', 'value_double', '1h', 'mean',
    )
    print(hourly_mean.head(10).to_string())

    # Multiple statistics
    print("\n--- Hourly Statistics (mean, min, max, range) ---")
    multi_stats = TimeGroupedStatistics.calculate_statistics(
        df, 'systime', 'value_double', '1h', ['mean', 'min', 'max', 'range'],
    )
    print(multi_stats.head(10).to_string())

    # Diff statistic (last - first in window)
    print("\n--- Hourly Difference (last - first) ---")
    hourly_diff = TimeGroupedStatistics.calculate_statistic(
        df, 'systime', 'value_double', '1h', 'diff',
    )
    print(hourly_diff.head(10).to_string())

    # Custom function
    print("\n--- Custom Aggregation (coefficient of variation per hour) ---")
    cv_func = lambda x: x.std() / x.mean() if x.mean() != 0 else 0
    custom = TimeGroupedStatistics.calculate_custom_func(
        df, 'systime', 'value_double', '1h', cv_func,
    )
    print(custom.head(10).to_string())


def main():
    """Run all statistics demonstrations."""
    print("\n" + "=" * 70)
    print("Statistics Features Demonstration")
    print("=" * 70)

    try:
        demo_numeric_statistics()
        demo_string_statistics()
        demo_boolean_statistics()
        demo_timestamp_statistics()
        demo_time_grouped_statistics()

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
