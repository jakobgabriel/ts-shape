# timeseries-shaper

Timeseries-Shaper is a Python library for efficiently filtering and preprocessing time series data using pandas. It provides a set of tools to handle various data transformations, making data preparation tasks easier and more intuitive.

## Features

### Load 

- **Load Parquet**: Load parquet files for further processing


### Transform



#### Filter

- **Filter Missing Values**: Quickly filter out or fill missing values in your time series data.
- **Boolean Filters**: Apply boolean logic to filter data based on specific conditions.
- **Integer and Double Filters**: Perform numeric operations and filters specific to integer and double data types.
- **String Filters**: Manipulate and filter data based on string operations.


#### Calculation 

- 


#### Descriptive Statistics

- **Boolean Stats**: 
- **Numeric Stats**: 
- **String Stats**: 
- **Timeseries Stats**: 


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


## Development 

- Generate new pdocs: `.\generate_docs.sh`
- Install package locally: `pip install -e .`
- Run tests locally with pytest: `pytest /tests`

- Build package for upload: `python setup.py sdist bdist_wheel`
- Upload build package to pypi: `twine upload dist/* --verbose --skip-existing`