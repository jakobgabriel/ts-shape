"""Time Functions

Timestamp conversion and timezone operations.

Classes:
- TimestampConverter: Convert integer timestamps to tz-aware datetimes.
  - convert_to_datetime: Convert s/ms/us/ns to datetime in a timezone.

- TimezoneShift: Timezone localization/conversion helpers.
  - shift_timezone: Convert timezones in-place.
  - add_timezone_column: Add a converted timestamp column.
  - detect_timezone_awareness: Check tz-awareness of a column.
  - revert_to_original_timezone: Convert back to original tz.
  - calculate_time_difference: Difference between two timestamp columns.
"""
