# timeseries-shaper

Timeseries-Shaper is a Python library for efficiently filtering and preprocessing time series data using pandas. It provides a set of tools to handle various data transformations, making data preparation tasks easier and more intuitive.

Besides that multiple engineering specific methods are utilized to make it fast and easy to work with time series data.

## Features | Structure

| **Directory**           | **Subdirectory/File**                  | **Description**                       |
|-------------------------|----------------------------------------|---------------------------------------|
| `timeseries_shaper`     | `base.py`                              | Core functionalities or base logic.  |
| `calculator`            | `numeric_calc.py`                      | Numeric calculations.                |
| `cycles`                | `cycle_processor.py`                   | Processes cycles in time series.     |
|                         | `cycles_extractor.py`                  | Extracts cycles from time series.    |
| `events`                | `outlier_detection.py`                 | Detects outliers in the data.        |
|                         | `statistical_process_control.py`       | Implements SPC for quality control.  |
|                         | `tolerance_deviation.py`               | Handles tolerance deviation checks.  |
|                         | `value_mapping.py`                     | Maps values for events.              |
| `filter`                | `boolean_filter.py`                    | Filters boolean data.                |
|                         | `custom_filter.py`                     | Filters using custom logic.          |
|                         | `datetime_filter.py`                   | Filters data based on datetime.      |
|                         | `numeric_filter.py`                    | Filters numeric data.                |
|                         | `string_filter.py`                     | Filters string data.                 |
| `functions`             | `lambda_func.py`                       | Contains reusable lambda functions.  |
| `loader`                | `metadata/metadata_api_loader.py`      | Loads metadata from API.             |
|                         | `metadata/metadata_json_loader.py`     | Loads metadata from JSON files.      |
|                         | `timeseries/parquet_loader.py`         | Loads time series data from Parquet. |
|                         | `timeseries/s3proxy_parquet_loader.py` | Loads data from S3 Parquet proxy.    |
|                         | `timeseries/timescale_loader.py`       | Loads data from TimescaleDB.         |
| `stats`                 | `boolean_stats.py`                     | Computes statistics for booleans.    |
|                         | `numeric_stats.py`                     | Computes statistics for numerics.    |
|                         | `string_stats.py`                      | Computes statistics for strings.     |
|                         | `timestamp_stats.py`                   | Computes statistics for timestamps.  |
| `time_stats`            | `time_stats_numeric.py`                | Computes time-based numeric stats.   |


## Installation

Install timeseries-shaper using pip:

```bash
pip install timeseries-shaper
```

## Useage

Here is a quick example to get you started:

```python
import pandas as pd
from timeseries_shaper.filters import IntegerFilter, StringFilter

# Sample DataFrame
data = {
    'value_integer': [1, 2, None, 4, 5],
    'value_string': ['apple', 'banana', None, 'cherry', 'date']
}
df = pd.DataFrame(data)

# Initialize the filter object
integer_filter = IntegerFilter(df)
string_filter = StringFilter(df)

# Apply filters
filtered_integers = integer_filter.filter_value_integer_not_match(2)
filtered_strings = string_filter.filter_value_string_not_match('banana')

print(filtered_integers)
print(filtered_strings)
```

## Documentation

For full documentation, visit GitHub Pages or check out the docstrings in the code.

## Contributing

Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please ensure to update tests as appropriate.

## License

Distributed under the MIT License. See LICENSE for more information.