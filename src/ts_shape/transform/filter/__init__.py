"""Filters

Row-level predicates for common column types.

Classes:
- IntegerFilter: Equality/inequality/range filters for integer columns.
  - filter_value_integer_match: Select rows equal to a value.
  - filter_value_integer_not_match: Select rows not equal to a value.
  - filter_value_integer_between: Select rows within [min, max].

- DoubleFilter: NaN removal and numeric ranges for floating-point columns.
  - filter_nan_value_double: Drop rows with NaN in the column.
  - filter_value_double_between: Select rows within [min, max].

- StringFilter: Equality, contains, regex cleaning, and change detection.
  - filter_na_value_string: Drop rows with NA values.
  - filter_value_string_match: Select rows equal to a string.
  - filter_value_string_not_match: Select rows not equal to a string.
  - filter_string_contains: Select rows containing a substring.
  - regex_clean_value_string: Regex-based cleaning or replacement.
  - detect_changes_in_string: Detect row-to-row changes in a string column.

- BooleanFilter: Detect raising/falling edges of boolean states.
  - filter_falling_value_bool: True→False transitions.
  - filter_raising_value_bool: False→True transitions.

- IsDeltaFilter: Select rows by the is_delta flag.
  - filter_is_delta_true: Only True.
  - filter_is_delta_false: Only False.

- DateTimeFilter: Before/after/between filters for timestamps.
  - filter_after_date: After a given date.
  - filter_before_date: Before a given date.
  - filter_between_dates: Between start and end dates.
  - filter_after_datetime: After a given datetime.
  - filter_before_datetime: Before a given datetime.
  - filter_between_datetimes: Between start and end datetimes.

- CustomFilter: Free-form DataFrame.query string conditions.
  - filter_custom_conditions: Apply a query string to filter rows.
"""
