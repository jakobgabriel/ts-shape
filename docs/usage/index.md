# Quick Start Guide

This guide walks you through a simple usage example of the `ts-shape` library to load, transform, and analyze time series data.

## Installation

You can install the library via pip:

```bash
pip install ts-shape
```

## Example Workflow

### 1. Import Modules

```python
from ts_shape.loader.timeseries import parquet_loader
from ts_shape.transform.filter import boolean_filter
from ts_shape.transform.time_functions import timestamp_converter, timezone_shift
from ts_shape.features.stats import string_stats
```

### 2. Load Time Series Data

Load all parquet files from a given directory:

```python
base_path = 'path/to/your/parquet/files'
df_all = parquet_loader.ParquetLoader.load_all_files(base_path)
```

### 3. Filter Data

Filter rows where the column `is_delta` is `True`:

```python
df_is_delta = boolean_filter.IsDeltaFilter.filter_is_delta_true(df_all)
```

### 4. Convert Timestamps

Convert Unix nanosecond timestamps to timezone-aware datetime objects:

```python
df_timestamp = timestamp_converter.TimestampConverter.convert_to_datetime(
    dataframe=df_is_delta,
    columns=['systime', 'plctime'],
    unit='ns',
    timezone='UTC'
)
```

### 5. Shift Timezone

Convert timestamps from UTC to local time (e.g., Europe/Berlin):

```python
df_timestamp_shift = timezone_shift.TimezoneShift.shift_timezone(
    dataframe=df_timestamp,
    time_column='systime',
    input_timezone='UTC',
    target_timezone='Europe/Berlin'
)
```

---

## Next Steps

- Explore feature extraction with `ts_shape.features`.
- Chain multiple transformations into a pipeline.