# Quick Start Guide

Get up and running with ts-shape production modules in 5 minutes!

## 1. Installation

```bash
pip install ts-shape
```

## 2. Prepare Your Data

ts-shape works with timeseries DataFrames in this format:

| Column | Type | Description |
|--------|------|-------------|
| uuid | string | Signal identifier |
| systime | datetime | Timestamp |
| value_string | string | String values (part numbers, states, reasons) |
| value_integer | int | Integer values (counters) |
| value_double | float | Numeric values |
| value_bool | bool | Boolean values (triggers) |
| is_delta | bool | Delta vs absolute value |

Example:
```python
import pandas as pd

df = pd.DataFrame({
    'uuid': ['part_number', 'part_number', 'counter', 'counter'],
    'systime': pd.date_range('2024-01-01', periods=4, freq='1h'),
    'value_string': ['PART_A', 'PART_A', None, None],
    'value_integer': [None, None, 100, 150],
    'is_delta': [False, False, True, True],
})
```

## 3. Basic Production Tracking

### Track Production Quantities

```python
from ts_shape.events.production import PartProductionTracking

tracker = PartProductionTracking(df)

# Daily production by part number
daily = tracker.daily_production_summary(
    part_id_uuid='part_number_signal',
    counter_uuid='production_counter'
)

print(daily)
# Output:
#     date        part_number  total_quantity  hours_active
# 0   2024-01-01  PART_A       1200           8
# 1   2024-01-01  PART_B       850            6
```

### Analyze Cycle Times

```python
from ts_shape.events.production import CycleTimeTracking

tracker = CycleTimeTracking(df)

# Cycle time statistics by part
stats = tracker.cycle_time_statistics(
    part_id_uuid='part_number_signal',
    cycle_trigger_uuid='cycle_complete_signal'
)

print(stats)
# Output:
#     part_number  count  avg_seconds  min_seconds  max_seconds
# 0   PART_A       450    47.5        42.1         58.2
# 1   PART_B       320    62.8        55.0         78.5
```

## 4. Shift Analysis

### Production by Shift

```python
from ts_shape.events.production import ShiftReporting

reporter = ShiftReporting(df)

# Production per shift
shifts = reporter.shift_production(
    counter_uuid='production_counter'
)

print(shifts)
# Output:
#     date        shift    quantity
# 0   2024-01-01  shift_1  450
# 1   2024-01-01  shift_2  425
# 2   2024-01-01  shift_3  380
```

## 5. Downtime Analysis

### Calculate Availability

```python
from ts_shape.events.production import DowntimeTracking

tracker = DowntimeTracking(df)

# Downtime and availability by shift
downtime = tracker.downtime_by_shift(
    state_uuid='machine_state',
    running_value='Running'
)

print(downtime)
# Output:
#     date        shift    downtime_minutes  availability_pct
# 0   2024-01-01  shift_1  45.2             90.6
# 1   2024-01-01  shift_2  67.5             85.9
# 2   2024-01-01  shift_3  92.0             80.8
```

### Find Top Downtime Reasons

```python
# Pareto analysis - focus on the vital few
top_reasons = tracker.top_downtime_reasons(
    state_uuid='machine_state',
    reason_uuid='downtime_reason',
    top_n=5
)

print(top_reasons)
# Output:
#     reason              total_minutes  cumulative_pct
# 0   Material_Shortage   145.5         35.2
# 1   Tool_Change         98.2          59.0
# 2   Quality_Issue       76.0          77.4
```

## 6. Quality Tracking

### NOK (Defective Parts) Analysis

```python
from ts_shape.events.production import QualityTracking

tracker = QualityTracking(df)

# NOK rate and First Pass Yield by shift
quality = tracker.nok_by_shift(
    ok_counter_uuid='good_parts_counter',
    nok_counter_uuid='bad_parts_counter'
)

print(quality)
# Output:
#     date        shift    nok_parts  nok_rate_pct  first_pass_yield_pct
# 0   2024-01-01  shift_1  12         2.6           97.4
# 1   2024-01-01  shift_2  18         4.1           95.9
# 2   2024-01-01  shift_3  25         6.2           93.8
```

### Find Top Defect Types

```python
# Pareto analysis of defects
defects = tracker.nok_by_reason(
    nok_counter_uuid='bad_parts_counter',
    defect_reason_uuid='defect_reason'
)

print(defects)
# Output:
#     reason              nok_parts  pct_of_total
# 0   Dimension_Error     45         40.5
# 1   Surface_Defect      28         25.2
# 2   Wrong_Color         22         19.8
```

## 7. Complete Daily Dashboard

Combine all modules for a complete performance picture:

```python
from ts_shape.events.production import *

# 1. QUANTITY: How many parts?
production = PartProductionTracking(df)
daily_prod = production.daily_production_summary('part_id', 'counter')
print(f"Total production: {daily_prod['total_quantity'].sum()} parts")

# 2. SPEED: How fast?
cycles = CycleTimeTracking(df)
cycle_stats = cycles.cycle_time_statistics('part_id', 'cycle_trigger')
print(f"Average cycle time: {cycle_stats['avg_seconds'].mean():.1f} seconds")

# 3. AVAILABILITY: How much uptime?
downtime = DowntimeTracking(df)
availability = downtime.downtime_by_shift('state', running_value='Running')
avg_avail = availability['availability_pct'].mean()
print(f"Average availability: {avg_avail:.1f}%")

# 4. QUALITY: How good?
quality = QualityTracking(df)
quality_metrics = quality.nok_by_shift('ok_counter', 'nok_counter')
avg_fpy = quality_metrics['first_pass_yield_pct'].mean()
print(f"Average FPY: {avg_fpy:.1f}%")

# 5. OEE (simplified)
oee = (avg_avail * avg_fpy) / 100
print(f"\nSimplified OEE: {oee:.1f}%")
```

Output:
```
Total production: 1,255 parts
Average cycle time: 47.3 seconds
Average availability: 89.2%
Average FPY: 96.5%

Simplified OEE: 86.1%  ← World-class!
```

## 8. Custom Shift Definitions

All shift-based modules support custom shifts:

```python
# 2-shift operation
custom_shifts = {
    'day': ('06:00', '18:00'),
    'night': ('18:00', '06:00'),
}

# Use with any shift-based module
reporter = ShiftReporting(df, shift_definitions=custom_shifts)
downtime = DowntimeTracking(df, shift_definitions=custom_shifts)
quality = QualityTracking(df, shift_definitions=custom_shifts)
```

## Next Steps

- [Daily Production Modules Guide](../production/daily_production.md) - Complete PartProductionTracking, CycleTimeTracking, ShiftReporting docs
- [Downtime & Quality Guide](../production/downtime_quality.md) - Complete DowntimeTracking and QualityTracking docs
- [Complete Module Summary](../production/complete_guide.md) - All 5 modules overview with examples
- [API Reference](../reference/ts_shape/events/production/) - Detailed API documentation

## Common Questions

**Q: What if I don't have all the signals?**
A: Each module works independently. Use only the modules for which you have data.

**Q: Can I use custom time windows?**
A: Yes! Most methods accept a `window` parameter (e.g., '1h', '15min', '1D').

**Q: What if my data structure is different?**
A: Use the `value_column_*` parameters to specify which columns contain your data.

**Q: How do I handle multiple machines?**
A: Filter your DataFrame before passing to the tracker: `df[df['machine_id'] == 'M001']`

**Q: Can I export results?**
A: Yes! All methods return pandas DataFrames. Use `.to_csv()`, `.to_excel()`, etc.

## Need Help?

- Check the [complete documentation](../production/complete_guide.md)
- Review [API reference](../reference/ts_shape/events/production/)
- See [future features](../production/future_features.md) for upcoming additions
- Report issues on GitHub
