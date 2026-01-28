# Quick Start

Get started with ts-shape in 5 minutes.

## Installation

```bash
pip install ts-shape
```

## Basic Example

```python
import pandas as pd
from ts_shape.transform.filter.numeric_filter import NumericFilter
from ts_shape.features.stats.numeric_stats import NumericStatistics

# Load your data
df = pd.read_parquet("sensors.parquet")

# Filter to valid range
clean = NumericFilter.filter_value_in_range(df, "value_double", 0, 100)

# Compute statistics
stats = NumericStatistics(clean, "value_double")
print(f"Mean: {stats.mean():.2f}")
print(f"Std: {stats.std():.2f}")
```

## Data Format

ts-shape expects DataFrames with these columns:

| Column | Type | Description |
|--------|------|-------------|
| `uuid` | string | Signal identifier |
| `systime` | datetime | Timestamp |
| `value_double` | float | Numeric values |
| `value_integer` | int | Integer values |
| `value_string` | string | String values |
| `value_bool` | bool | Boolean values |

Not all columns are required - use only what you need.

## Common Operations

### Filter by Time Range

```python
from ts_shape.transform.filter.datetime_filter import DateTimeFilter

df = DateTimeFilter.filter_between(df, "systime", "2024-01-01", "2024-03-31")
```

### Detect Outliers

```python
from ts_shape.events.quality.outlier_detection import OutlierDetection

outliers = OutlierDetection.detect_zscore_outliers(df, "value_double", threshold=3.0)
clean = df[~df.index.isin(outliers.index)]
```

### Load from Multiple Sources

```python
from ts_shape.loader.timeseries.parquet_loader import ParquetLoader
from ts_shape.loader.metadata.metadata_json_loader import MetadataLoader
from ts_shape.loader.combine.integrator import DataIntegratorHybrid

# Load timeseries and metadata
ts_df = ParquetLoader.load_all_files("data/")
meta_df = MetadataLoader("config/signals.json").to_df()

# Combine them
df = DataIntegratorHybrid.combine_data(
    timeseries_sources=[ts_df],
    metadata_sources=[meta_df],
    join_key="uuid"
)
```

## Next Steps

- [Usage Examples](../usage/index.md) - More detailed examples
- [Concept Guide](../concept.md) - Architecture overview
- [API Reference](../reference/) - Complete API docs
