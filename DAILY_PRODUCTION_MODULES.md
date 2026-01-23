# Daily Production Tracking Modules ✅

**Date:** 2026-01-22
**Status:** Implemented and Ready to Use

---

## Overview

Three new modules specifically designed for **daily manufacturing operations**. Simple, practical tools that answer the questions every plant manager asks every day.

### The Daily Questions These Answer:

1. ✅ **"How many parts did we make today?"** → `PartProductionTracking`
2. ✅ **"What's the cycle time for part X?"** → `CycleTimeTracking`
3. ✅ **"How did shift 1 perform vs shift 2?"** → `ShiftReporting`

---

## 1. Part Production Tracking

**File:** `src/ts_shape/production/part_tracking.py`

### What It Does
Tracks production quantities by part number using two simple signals:
- One UUID for **part number** (string)
- One UUID for **production counter** (integer)

### Methods

#### `production_by_part(part_id_uuid, counter_uuid, window='1h')`
Production quantity per time window

```python
from ts_shape.production import PartProductionTracking

tracker = PartProductionTracking(df)
hourly = tracker.production_by_part(
    part_id_uuid='part_number_signal',
    counter_uuid='production_counter',
    window='1h'
)
```

**Returns:**
```
    window_start         part_number  quantity  first_count  last_count
0   2024-01-01 08:00:00  PART_A       150       1000        1150
1   2024-01-01 09:00:00  PART_A       145       1150        1295
2   2024-01-01 10:00:00  PART_B       98        1295        1393
```

#### `daily_production_summary(part_id_uuid, counter_uuid)`
Daily totals by part

**Returns:**
```
    date        part_number  total_quantity  hours_active
0   2024-01-01  PART_A       1200           8
1   2024-01-01  PART_B       850            6
```

#### `production_totals(part_id_uuid, counter_uuid, start_date, end_date)`
Aggregate production over date range

**Returns:**
```
    part_number  total_quantity  days_produced
0   PART_A       8450           5
1   PART_B       6200           4
```

---

## 2. Cycle Time Tracking

**File:** `src/ts_shape/production/cycle_time_tracking.py`

### What It Does
Analyzes cycle times by part number using two signals:
- One UUID for **part number** (string)
- One UUID for **cycle trigger** (boolean or integer)

### Methods

#### `cycle_time_by_part(part_id_uuid, cycle_trigger_uuid)`
Individual cycle times

```python
from ts_shape.production import CycleTimeTracking

tracker = CycleTimeTracking(df)
cycles = tracker.cycle_time_by_part(
    part_id_uuid='part_number_signal',
    cycle_trigger_uuid='cycle_complete_signal'
)
```

**Returns:**
```
    systime              part_number  cycle_time_seconds
0   2024-01-01 08:05:30  PART_A       45.2
1   2024-01-01 08:06:18  PART_A       48.0
2   2024-01-01 08:07:05  PART_A       47.1
```

#### `cycle_time_statistics(part_id_uuid, cycle_trigger_uuid)`
Statistics by part

**Returns:**
```
    part_number  count  min_seconds  avg_seconds  max_seconds  std_seconds  median_seconds
0   PART_A       450    42.1         47.5         58.2         3.2          47.1
1   PART_B       320    55.0         62.8         78.5         5.1          61.9
```

#### `detect_slow_cycles(part_id_uuid, cycle_trigger_uuid, threshold_factor=1.5)`
Find cycles slower than expected

**Returns:**
```
    systime              part_number  cycle_time_seconds  median_seconds  deviation_factor  is_slow
0   2024-01-01 10:15:30  PART_A       75.2               47.1            1.60              True
1   2024-01-01 14:22:18  PART_A       82.5               47.1            1.75              True
```

#### `cycle_time_trend(part_id_uuid, cycle_trigger_uuid, part_number, window_size=20)`
Trend analysis for specific part

**Returns:**
```
    systime              cycle_time_seconds  moving_avg  trend
0   2024-01-01 08:05:30  45.2               47.1        improving
1   2024-01-01 08:06:18  48.0               47.2        stable
2   2024-01-01 08:07:05  47.1               47.1        stable
```

#### `hourly_cycle_time_summary(part_id_uuid, cycle_trigger_uuid)`
Hourly statistics

**Returns:**
```
    hour                 part_number  cycles_completed  avg_cycle_time  min_cycle_time  max_cycle_time
0   2024-01-01 08:00:00  PART_A       75               47.2            42.1            55.8
1   2024-01-01 09:00:00  PART_A       78               46.8            43.0            52.3
```

---

## 3. Shift Reporting

**File:** `src/ts_shape/production/shift_reporting.py`

### What It Does
Shift-based production analysis with configurable shift times.

### Configuration

```python
from ts_shape.production import ShiftReporting

reporter = ShiftReporting(df, shift_definitions={
    "day": ("06:00", "14:00"),
    "afternoon": ("14:00", "22:00"),
    "night": ("22:00", "06:00"),
})
```

### Methods

#### `shift_production(counter_uuid, part_id_uuid=None, date=None)`
Production by shift

```python
shift_prod = reporter.shift_production(
    counter_uuid='production_counter',
    part_id_uuid='part_number_signal'
)
```

**Returns:**
```
    date        shift      part_number  quantity
0   2024-01-01  day        PART_A       450
1   2024-01-01  afternoon  PART_A       425
2   2024-01-01  night      PART_A       380
```

#### `shift_comparison(counter_uuid, days=7)`
Compare shifts over recent days

**Returns:**
```
    shift      avg_quantity  min_quantity  max_quantity  std_quantity  days_count
0   day        445           420           465           15.2          7
1   afternoon  430           405           450           12.8          7
2   night      385           360           410           18.5          7
```

#### `shift_targets(counter_uuid, targets)`
Actual vs target comparison

```python
results = reporter.shift_targets(
    counter_uuid='production_counter',
    targets={'day': 450, 'afternoon': 450, 'night': 400}
)
```

**Returns:**
```
    date        shift      actual  target  variance  achievement_pct
0   2024-01-01  day        445     450     -5        98.9
1   2024-01-01  afternoon  465     450     15        103.3
2   2024-01-01  night      390     400     -10       97.5
```

#### `best_and_worst_shifts(counter_uuid, days=30)`
Identify top/bottom performers

**Returns dictionary with:**
- `'best'`: Top 5 best shifts
- `'worst'`: Top 5 worst shifts

---

## Complete Usage Example

```python
import pandas as pd
from ts_shape.production import (
    PartProductionTracking,
    CycleTimeTracking,
    ShiftReporting
)

# Load your data
df = pd.read_parquet('production_data.parquet')

# 1. PRODUCTION TRACKING
tracker = PartProductionTracking(df)

# Daily summary
daily = tracker.daily_production_summary(
    part_id_uuid='part_number',
    counter_uuid='production_counter'
)
print("Daily Production:")
print(daily)

# 2. CYCLE TIME ANALYSIS
cycle_tracker = CycleTimeTracking(df)

# Statistics by part
stats = cycle_tracker.cycle_time_statistics(
    part_id_uuid='part_number',
    cycle_trigger_uuid='cycle_complete'
)
print("\nCycle Time Statistics:")
print(stats)

# Find slow cycles
slow = cycle_tracker.detect_slow_cycles(
    part_id_uuid='part_number',
    cycle_trigger_uuid='cycle_complete',
    threshold_factor=1.5  # 50% slower than median
)
print(f"\nFound {len(slow)} slow cycles")

# 3. SHIFT REPORTING
shift_reporter = ShiftReporting(df, shift_definitions={
    "day": ("06:00", "14:00"),
    "swing": ("14:00", "22:00"),
    "night": ("22:00", "06:00"),
})

# Compare shifts
comparison = shift_reporter.shift_comparison(
    counter_uuid='production_counter',
    days=7
)
print("\nShift Comparison (Last 7 Days):")
print(comparison)

# Target performance
targets = {'day': 500, 'swing': 500, 'night': 450}
performance = shift_reporter.shift_targets(
    counter_uuid='production_counter',
    targets=targets
)
print("\nToday's Performance vs Targets:")
print(performance)
```

---

## Data Structure Requirements

### Input DataFrame Schema
Your DataFrame must have the standard ts-shape structure:

| Column | Type | Description |
|--------|------|-------------|
| `systime` | datetime64 | Timestamp |
| `uuid` | string | Signal identifier |
| `value_string` | string | String values (part numbers) |
| `value_integer` | int | Integer values (counters) |
| `value_bool` | bool | Boolean values (cycle triggers) |
| `is_delta` | bool | Delta vs continuous flag |

### Example Signal Mapping

**For Part Production:**
- Part Number UUID: `"machine_01_part_id"` → uses `value_string`
- Counter UUID: `"machine_01_counter"` → uses `value_integer`

**For Cycle Time:**
- Part Number UUID: `"machine_01_part_id"` → uses `value_string`
- Cycle Trigger UUID: `"machine_01_cycle_complete"` → uses `value_bool`

---

## Key Benefits

### 1. **Simple to Use**
One signal = one UUID. No complex joins or configurations.

### 2. **Daily Operations**
Answers the questions managers ask every single day.

### 3. **Flexible Windows**
- Hourly: `window='1h'`
- Shift: `window='8h'`
- Daily: `window='1d'`
- Custom: `window='4h'`

### 4. **Part-Specific Analysis**
Everything is tracked by part number for detailed insights.

### 5. **Trend Detection**
Identify degradation before it becomes a problem.

---

## Real-World Use Cases

### Morning Production Meeting
```python
# "What did we produce yesterday?"
yesterday = tracker.daily_production_summary(
    part_id_uuid='part_id',
    counter_uuid='counter'
)

# "How did the shifts perform?"
shift_perf = reporter.shift_production(
    counter_uuid='counter',
    date='2024-01-22'
)

# "Were there any slow cycles?"
slow_cycles = cycle_tracker.detect_slow_cycles(
    part_id_uuid='part_id',
    cycle_trigger_uuid='cycle_trigger',
    threshold_factor=1.3
)
```

### Weekly Review
```python
# "Production totals this week"
weekly = tracker.production_totals(
    part_id_uuid='part_id',
    counter_uuid='counter',
    start_date='2024-01-15',
    end_date='2024-01-21'
)

# "Shift performance trends"
shift_trends = reporter.shift_comparison(
    counter_uuid='counter',
    days=7
)

# "Cycle time trends"
cycle_stats = cycle_tracker.cycle_time_statistics(
    part_id_uuid='part_id',
    cycle_trigger_uuid='cycle_trigger'
)
```

### Problem Investigation
```python
# "When did cycle times start increasing for PART_A?"
trend = cycle_tracker.cycle_time_trend(
    part_id_uuid='part_id',
    cycle_trigger_uuid='cycle_trigger',
    part_number='PART_A',
    window_size=50
)

# "Which shifts had the most slow cycles?"
hourly = cycle_tracker.hourly_cycle_time_summary(
    part_id_uuid='part_id',
    cycle_trigger_uuid='cycle_trigger'
)
```

---

## Installation

The modules are already installed in your ts-shape package:

```python
from ts_shape.production import (
    PartProductionTracking,
    CycleTimeTracking,
    ShiftReporting,
)
```

---

## Next Steps

These modules provide the foundation for daily operations. Additional modules that could be built on this foundation:

1. **Downtime Tracking** - Track downtime by reason code
2. **Quality Metrics** - Scrap/rework rates by part
3. **Line Balancing** - Multi-station throughput analysis
4. **Predictive Alerts** - Automated alerts for anomalies

---

**Status:** ✅ Ready for immediate use
**Location:** `src/ts_shape/production/`
**Commit:** b29dbe7

All modules follow ts-shape patterns, use simple one-UUID-per-signal design, and return easy-to-use pandas DataFrames.
