# Usage Examples

Practical examples for common timeseries data tasks.

## Loading Data

### From Parquet Files

```python
from ts_shape.loader.timeseries.parquet_loader import ParquetLoader

# Load all parquet files from a directory
df = ParquetLoader.load_all_files("data/sensors/")

# Preview the data
print(df.head())
#          uuid                   systime  value_double
# 0  temperature  2024-01-01 00:00:00+00:00         23.5
# 1  temperature  2024-01-01 00:01:00+00:00         23.7
# 2     pressure  2024-01-01 00:00:00+00:00       1013.2
```

### From Azure Blob Storage

```python
from ts_shape.loader.timeseries.azure_blob_loader import AzureBlobLoader

loader = AzureBlobLoader(
    connection_string="DefaultEndpointsProtocol=https;...",
    container_name="timeseries",
    base_path="sensors/"
)

df = loader.fetch_data_as_dataframe(
    start_date="2024-01-01",
    end_date="2024-01-31"
)
```

### From S3-Compatible Storage

```python
from ts_shape.loader.timeseries.s3proxy_parquet_loader import S3ProxyParquetLoader

loader = S3ProxyParquetLoader(
    endpoint_url="https://s3.example.com",
    bucket="data-lake",
    prefix="timeseries/"
)

df = loader.fetch_data_as_dataframe()
```

### Loading Metadata

```python
from ts_shape.loader.metadata.metadata_json_loader import MetadataLoader

# Load signal metadata from JSON
meta = MetadataLoader("config/signals.json").to_df()

print(meta)
#          uuid         label    unit
# 0  temperature  Temperature  Celsius
# 1     pressure     Pressure     hPa
```

---

## Combining Data

### Merge Timeseries with Metadata

```python
from ts_shape.loader.combine.integrator import DataIntegratorHybrid

# Combine timeseries with signal metadata
combined = DataIntegratorHybrid.combine_data(
    timeseries_sources=[ts_df],
    metadata_sources=[meta_df],
    join_key="uuid",
    merge_how="left"
)

print(combined.head())
#          uuid                   systime  value_double        label     unit
# 0  temperature  2024-01-01 00:00:00+00:00         23.5  Temperature  Celsius
```

### Filter by Specific Signals

```python
# Only load specific UUIDs
combined = DataIntegratorHybrid.combine_data(
    timeseries_sources=[ts_df],
    metadata_sources=[meta_df],
    uuids=["temperature", "humidity"],
    join_key="uuid"
)
```

---

## Filtering Data

### By Numeric Range

```python
from ts_shape.transform.filter.numeric_filter import NumericFilter

# Keep values between 0 and 100
df = NumericFilter.filter_value_in_range(df, "value_double", min_value=0, max_value=100)

# Remove null values
df = NumericFilter.filter_not_null(df, "value_double")

# Keep values above threshold
df = NumericFilter.filter_greater_than(df, "value_double", threshold=50)
```

### By Time Range

```python
from ts_shape.transform.filter.datetime_filter import DateTimeFilter

# Filter to specific date range
df = DateTimeFilter.filter_between(
    df,
    column="systime",
    start_date="2024-01-01",
    end_date="2024-01-31"
)

# Keep only data after a date
df = DateTimeFilter.filter_after(df, "systime", "2024-06-01")

# Filter by hour of day (e.g., business hours)
df = DateTimeFilter.filter_by_hour_range(df, "systime", start_hour=9, end_hour=17)
```

### By String Pattern

```python
from ts_shape.transform.filter.string_filter import StringFilter

# Filter by exact match
df = StringFilter.filter_equals(df, "uuid", "temperature")

# Filter by pattern
df = StringFilter.filter_contains(df, "uuid", "sensor_")

# Filter by list of values
df = StringFilter.filter_in_list(df, "uuid", ["temp_1", "temp_2", "temp_3"])
```

### By Boolean Flag

```python
from ts_shape.transform.filter.boolean_filter import IsDeltaFilter

# Keep only delta values
df = IsDeltaFilter.filter_is_delta_true(df)

# Keep only absolute values
df = IsDeltaFilter.filter_is_delta_false(df)
```

---

## Transforming Data

### Timezone Conversion

```python
from ts_shape.transform.time_functions.timezone_shift import TimezoneShift
from ts_shape.transform.time_functions.timestamp_converter import TimestampConverter

# Convert Unix timestamps to datetime
df = TimestampConverter.convert_to_datetime(
    df,
    columns=["systime"],
    unit="ns",
    timezone="UTC"
)

# Shift to local timezone
df = TimezoneShift.shift_timezone(
    df,
    time_column="systime",
    input_timezone="UTC",
    target_timezone="Europe/Berlin"
)
```

### Numeric Calculations

```python
from ts_shape.transform.calculator.numeric_calc import NumericCalc

# Add rolling average
df = NumericCalc.add_rolling_mean(df, "value_double", window=10)

# Add difference from previous value
df = NumericCalc.add_diff(df, "value_double")

# Normalize values (0-1 scale)
df = NumericCalc.normalize(df, "value_double")
```

---

## Computing Statistics

### Numeric Statistics

```python
from ts_shape.features.stats.numeric_stats import NumericStatistics

stats = NumericStatistics(df, "value_double")

print(f"Count: {stats.count()}")
print(f"Mean: {stats.mean():.2f}")
print(f"Std: {stats.std():.2f}")
print(f"Min: {stats.min():.2f}")
print(f"Max: {stats.max():.2f}")
print(f"Median: {stats.median():.2f}")

# Get percentiles
print(f"P95: {stats.percentile(95):.2f}")
print(f"P99: {stats.percentile(99):.2f}")
```

### Time Coverage Statistics

```python
from ts_shape.features.stats.timestamp_stats import TimestampStatistics

time_stats = TimestampStatistics(df, "systime")

print(f"First: {time_stats.first()}")
print(f"Last: {time_stats.last()}")
print(f"Duration: {time_stats.duration()}")
print(f"Count: {time_stats.count()}")
```

### String Value Counts

```python
from ts_shape.features.stats.string_stats import StringStatistics

str_stats = StringStatistics(df, "uuid")

# Get value frequency
print(str_stats.value_counts())
#          uuid  count
# 0  temperature   1440
# 1     pressure   1440
# 2     humidity   1440
```

---

## Detecting Events

### Outlier Detection

```python
from ts_shape.events.quality.outlier_detection import OutlierDetection

# Z-score based outliers (values > 3 std from mean)
outliers = OutlierDetection.detect_zscore_outliers(
    df,
    column="value_double",
    threshold=3.0
)

print(f"Found {len(outliers)} outliers")

# IQR-based outliers
outliers = OutlierDetection.detect_iqr_outliers(
    df,
    column="value_double",
    multiplier=1.5
)
```

### Statistical Process Control

```python
from ts_shape.events.quality.statistical_process_control import StatisticalProcessControl

spc = StatisticalProcessControl(df, value_column="value_double")

# Detect control limit violations
violations = spc.detect_control_violations(
    ucl=100,  # Upper control limit
    lcl=0     # Lower control limit
)

# Detect Western Electric rules violations
we_violations = spc.detect_western_electric_rules()
```

### Tolerance Deviations

```python
from ts_shape.events.quality.tolerance_deviation import ToleranceDeviation

# Find values outside specification limits
deviations = ToleranceDeviation.detect_out_of_tolerance(
    df,
    column="value_double",
    upper_limit=100,
    lower_limit=0
)
```

---

## Complete Pipeline Example

```python
import pandas as pd
from ts_shape.loader.timeseries.parquet_loader import ParquetLoader
from ts_shape.loader.metadata.metadata_json_loader import MetadataLoader
from ts_shape.loader.combine.integrator import DataIntegratorHybrid
from ts_shape.transform.filter.datetime_filter import DateTimeFilter
from ts_shape.transform.filter.numeric_filter import NumericFilter
from ts_shape.features.stats.numeric_stats import NumericStatistics
from ts_shape.events.quality.outlier_detection import OutlierDetection

# 1. Load data
print("Loading data...")
ts_df = ParquetLoader.load_all_files("data/sensors/")
meta_df = MetadataLoader("config/signals.json").to_df()

# 2. Combine with metadata
print("Combining with metadata...")
df = DataIntegratorHybrid.combine_data(
    timeseries_sources=[ts_df],
    metadata_sources=[meta_df],
    join_key="uuid"
)
print(f"  Total records: {len(df)}")

# 3. Filter to analysis period
print("Filtering...")
df = DateTimeFilter.filter_between(df, "systime", "2024-01-01", "2024-03-31")
df = NumericFilter.filter_not_null(df, "value_double")
print(f"  After filtering: {len(df)}")

# 4. Detect and remove outliers
print("Detecting outliers...")
outliers = OutlierDetection.detect_zscore_outliers(df, "value_double", threshold=3.0)
clean_df = df[~df.index.isin(outliers.index)]
print(f"  Outliers removed: {len(outliers)}")

# 5. Compute statistics per signal
print("\nStatistics by signal:")
for uuid in clean_df["uuid"].unique():
    signal_df = clean_df[clean_df["uuid"] == uuid]
    stats = NumericStatistics(signal_df, "value_double")
    print(f"  {uuid}:")
    print(f"    Count: {stats.count()}")
    print(f"    Mean: {stats.mean():.2f}")
    print(f"    Std: {stats.std():.2f}")
    print(f"    Range: [{stats.min():.2f}, {stats.max():.2f}]")

# 6. Export results
clean_df.to_parquet("output/clean_data.parquet")
print("\nExported to output/clean_data.parquet")
```

Output:
```
Loading data...
Combining with metadata...
  Total records: 125000
Filtering...
  After filtering: 98500
Detecting outliers...
  Outliers removed: 127

Statistics by signal:
  temperature:
    Count: 32850
    Mean: 23.45
    Std: 2.31
    Range: [18.20, 28.70]
  pressure:
    Count: 32800
    Mean: 1013.25
    Std: 5.67
    Range: [995.00, 1030.00]
  humidity:
    Count: 32723
    Mean: 65.30
    Std: 12.45
    Range: [35.00, 95.00]

Exported to output/clean_data.parquet
```

---

## Next Steps

- [Concept Guide](../concept.md) - Understand the architecture
- [API Reference](../reference/) - Full API documentation
- [Contributing](../contributing.md) - Contribute to ts-shape
