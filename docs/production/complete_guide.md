# Production Modules Summary

Complete suite of **bread-and-butter** modules for daily plant management. Every module focuses on answering the essential questions that plant managers ask every single day.

---

## 📦 Complete Module Overview

### 5 Essential Modules for Daily Manufacturing

| Module | Purpose | Key Questions Answered |
|--------|---------|----------------------|
| **PartProductionTracking** | Production quantity tracking | How many parts did we make? |
| **CycleTimeTracking** | Cycle time analysis | How fast are we producing? |
| **ShiftReporting** | Shift-based summaries | How did each shift perform? |
| **DowntimeTracking** | Availability & downtime | How much uptime did we have? |
| **QualityTracking** | NOK parts & defects | What's our quality rate? |

---

## 🎯 The 4 Pillars of Manufacturing Performance

These modules give you complete visibility into the 4 critical dimensions:

```
┌─────────────────────────────────────────────────────┐
│                 PRODUCTION METRICS                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. QUANTITY (How Many?)                            │
│     ├─ PartProductionTracking                       │
│     └─ ShiftReporting                               │
│                                                      │
│  2. SPEED (How Fast?)                               │
│     ├─ CycleTimeTracking                            │
│     └─ ShiftReporting                               │
│                                                      │
│  3. AVAILABILITY (Uptime?)                          │
│     ├─ DowntimeTracking                             │
│     └─ ShiftReporting                               │
│                                                      │
│  4. QUALITY (How Good?)                             │
│     ├─ QualityTracking                              │
│     └─ ShiftReporting                               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Module Details

### 1. PartProductionTracking

**What**: Track how many parts were produced by part number

**Key Methods**:
- `production_by_part()` - Hourly/custom window production
- `daily_production_summary()` - Daily totals by part
- `production_totals()` - Totals over date range

**Typical Usage**:
```python
tracker = PartProductionTracking(df)
daily = tracker.daily_production_summary('part_id_uuid', 'counter_uuid')
# Returns: date, part_number, total_quantity, hours_active
```

**Answers**:
- How many PART_A did we make today?
- Which part number had the most production?
- Did we meet our daily target?

---

### 2. CycleTimeTracking

**What**: Analyze cycle times by part number

**Key Methods**:
- `cycle_time_by_part()` - Cycle time for each part
- `cycle_time_statistics()` - Min/avg/max/std by part
- `detect_slow_cycles()` - Identify abnormal cycles
- `cycle_time_trend()` - Detect degradation/improvement

**Typical Usage**:
```python
tracker = CycleTimeTracking(df)
stats = tracker.cycle_time_statistics('part_id_uuid', 'cycle_trigger_uuid')
# Returns: part_number, count, min/avg/max/std/median_seconds
```

**Answers**:
- What's the average cycle time for PART_B?
- Are cycle times getting slower?
- Which cycles were abnormally slow?

---

### 3. ShiftReporting

**What**: Shift-based production analysis

**Key Methods**:
- `shift_production()` - Production per shift
- `shift_comparison()` - Compare shift performance
- `shift_targets()` - Actual vs target
- `best_and_worst_shifts()` - Performance ranking

**Typical Usage**:
```python
reporter = ShiftReporting(df)
shifts = reporter.shift_production('counter_uuid')
# Returns: date, shift, quantity
```

**Answers**:
- How much did each shift produce?
- Which shift performed best?
- Are we meeting shift targets?

---

### 4. DowntimeTracking ⭐ NEW

**What**: Machine downtime and availability analysis

**Key Methods**:
- `downtime_by_shift()` - Downtime and availability per shift
- `downtime_by_reason()` - Root cause analysis
- `top_downtime_reasons()` - Pareto analysis (80/20)
- `availability_trend()` - Track availability over time

**Typical Usage**:
```python
tracker = DowntimeTracking(df)
shift_dt = tracker.downtime_by_shift('state_uuid', running_value='Running')
# Returns: date, shift, total_minutes, downtime_minutes, uptime_minutes, availability_pct

top_reasons = tracker.top_downtime_reasons('state_uuid', 'reason_uuid', top_n=5)
# Returns: reason, total_minutes, pct_of_total, cumulative_pct
```

**Answers**:
- What was our availability yesterday?
- How much downtime per shift?
- What are the top 3 downtime reasons?
- Is availability improving or degrading?

**Key Metrics**:
- Availability % = (Uptime / Total Time) × 100
- Target: >85% good, >90% excellent, >95% world-class

---

### 5. QualityTracking ⭐ NEW

**What**: NOK (defective parts) and quality metrics

**Key Methods**:
- `nok_by_shift()` - NOK parts and FPY per shift
- `quality_by_part()` - Quality metrics by part number
- `nok_by_reason()` - Defect type analysis
- `daily_quality_summary()` - Daily quality rollup

**Typical Usage**:
```python
tracker = QualityTracking(df)
shift_quality = tracker.nok_by_shift('ok_counter_uuid', 'nok_counter_uuid')
# Returns: date, shift, ok_parts, nok_parts, total_parts, nok_rate_pct, first_pass_yield_pct

by_part = tracker.quality_by_part('ok_counter', 'nok_counter', 'part_id')
# Returns: part_number, ok_parts, nok_parts, total_parts, nok_rate_pct, first_pass_yield_pct
```

**Answers**:
- What's our NOK rate per shift?
- Which part number has quality issues?
- What are the most common defects?
- What's our First Pass Yield?

**Key Metrics**:
- NOK Rate % = (Defective Parts / Total Parts) × 100
- First Pass Yield % = (Good Parts / Total Parts) × 100
- Target: FPY >95% good, >98% excellent, >99% world-class

---

## 🚀 Complete Daily Dashboard Example

Combine all modules for a complete daily performance picture:

```python
from ts_shape.events.production import (
    PartProductionTracking,
    CycleTimeTracking,
    ShiftReporting,
    DowntimeTracking,
    QualityTracking,
)

# === QUANTITY: How many parts? ===
production = PartProductionTracking(df)
daily_prod = production.daily_production_summary('part_id', 'counter')
print(f"Total production: {daily_prod['total_quantity'].sum()} parts")

# === SPEED: How fast? ===
cycles = CycleTimeTracking(df)
cycle_stats = cycles.cycle_time_statistics('part_id', 'cycle_trigger')
print(f"Average cycle time: {cycle_stats['avg_seconds'].mean():.1f} seconds")

# === AVAILABILITY: How much uptime? ===
downtime = DowntimeTracking(df)
availability = downtime.downtime_by_shift('state', running_value='Running')
avg_avail = availability['availability_pct'].mean()
print(f"Average availability: {avg_avail:.1f}%")

# === QUALITY: How good? ===
quality = QualityTracking(df)
quality_metrics = quality.nok_by_shift('ok_counter', 'nok_counter')
avg_fpy = quality_metrics['first_pass_yield_pct'].mean()
print(f"Average FPY: {avg_fpy:.1f}%")

# === OVERALL EQUIPMENT EFFECTIVENESS (OEE) ===
# Simplified OEE = Availability × Quality
oee = (avg_avail * avg_fpy) / 100
print(f"\nSimplified OEE: {oee:.1f}%")
```

**Output Example**:
```
Total production: 1,255 parts
Average cycle time: 47.3 seconds
Average availability: 89.2%
Average FPY: 96.5%

Simplified OEE: 86.1%  ← World-class performance!
```

---

## 📋 Daily Manager Questions → Module Mapping

### Morning Production Meeting Questions

| Question | Module(s) | Method |
|----------|-----------|--------|
| "How many parts yesterday?" | PartProductionTracking | `daily_production_summary()` |
| "What were cycle times?" | CycleTimeTracking | `cycle_time_statistics()` |
| "Which shift produced most?" | ShiftReporting | `shift_production()` |
| "What was availability?" | DowntimeTracking | `downtime_by_shift()` |
| "What was NOK rate?" | QualityTracking | `nok_by_shift()` |
| "Top downtime reasons?" | DowntimeTracking | `top_downtime_reasons()` |
| "Top defect types?" | QualityTracking | `nok_by_reason()` |

### Performance Analysis Questions

| Question | Module(s) | Method |
|----------|-----------|--------|
| "Which part has quality issues?" | QualityTracking | `quality_by_part()` |
| "Are cycle times degrading?" | CycleTimeTracking | `cycle_time_trend()` |
| "Is availability improving?" | DowntimeTracking | `availability_trend()` |
| "Did we meet shift targets?" | ShiftReporting | `shift_targets()` |
| "Which shift performs best?" | ShiftReporting | `best_and_worst_shifts()` |

### Root Cause Analysis Questions

| Question | Module(s) | Method |
|----------|-----------|--------|
| "Why low production?" | DowntimeTracking | `downtime_by_reason()` |
| "What causes most downtime?" | DowntimeTracking | `top_downtime_reasons()` |
| "What are main defects?" | QualityTracking | `nok_by_reason()` |
| "Which cycles were slow?" | CycleTimeTracking | `detect_slow_cycles()` |

---

## 🎓 Design Principles

All modules follow these principles:

### 1. One UUID Per Signal
```python
# Each UUID represents exactly one signal
part_id_uuid = 'part_number_signal'       # Current part number
counter_uuid = 'production_counter'       # Production count
state_uuid = 'machine_state'              # Running/Stopped
reason_uuid = 'downtime_reason'           # Why stopped
ok_counter_uuid = 'good_parts_counter'    # OK parts
nok_counter_uuid = 'bad_parts_counter'    # NOK parts
```

### 2. Simple DataFrame Returns
All methods return pandas DataFrames - no complex objects

### 3. Shift-Based Analysis
Most modules support shift analysis (default 3-shift or custom)

### 4. Practical, Daily Questions
Every method answers a real question plant managers ask daily

### 5. No Over-Engineering
Simple implementations focused on getting the job done

---

## 📈 Key Performance Indicators (KPIs)

### World-Class Manufacturing Benchmarks

| Metric | Formula | Good | Excellent | World-Class |
|--------|---------|------|-----------|-------------|
| **Availability** | Uptime / Total Time | >85% | >90% | >95% |
| **Performance** | Actual / Ideal Speed | >90% | >95% | >98% |
| **Quality (FPY)** | Good Parts / Total | >95% | >98% | >99% |
| **OEE** | Avail × Perf × Quality | >60% | >75% | >85% |
| **NOK Rate** | Bad Parts / Total | <5% | <2% | <1% |

### Using These Modules for KPI Tracking

```python
# Availability
avail_tracker = DowntimeTracking(df)
availability = avail_tracker.downtime_by_shift('state', running_value='Running')
print(f"Availability: {availability['availability_pct'].mean():.1f}%")

# Quality (FPY)
quality_tracker = QualityTracking(df)
quality = quality_tracker.nok_by_shift('ok_counter', 'nok_counter')
print(f"FPY: {quality['first_pass_yield_pct'].mean():.1f}%")

# Performance (simplified - using cycle time)
cycle_tracker = CycleTimeTracking(df)
stats = cycle_tracker.cycle_time_statistics('part_id', 'cycle_trigger')
target_cycle_time = 45.0  # seconds
actual_avg = stats['avg_seconds'].mean()
performance = (target_cycle_time / actual_avg) * 100
print(f"Performance: {performance:.1f}%")

# OEE
oee = (availability['availability_pct'].mean() *
       quality['first_pass_yield_pct'].mean() *
       performance) / 10000
print(f"OEE: {oee:.1f}%")
```

---

## 🔍 Common Use Cases

### Use Case 1: Why Did We Miss Production Target?

```python
# 1. Check production
prod = PartProductionTracking(df).daily_production_summary('part_id', 'counter')
print(f"Actual: {prod['total_quantity'].sum()}, Target: 1500")

# 2. Check downtime
downtime = DowntimeTracking(df).downtime_by_shift('state', running_value='Running')
print(f"Total downtime: {downtime['downtime_minutes'].sum():.0f} minutes")

# 3. Find root cause
reasons = DowntimeTracking(df).top_downtime_reasons('state', 'reason', top_n=3)
print("Top reasons:")
print(reasons)

# 4. Check if quality issues
quality = QualityTracking(df).nok_by_shift('ok_counter', 'nok_counter')
print(f"NOK rate: {quality['nok_rate_pct'].mean():.1f}%")
```

### Use Case 2: Quality Investigation

```python
# 1. Which part has issues?
by_part = QualityTracking(df).quality_by_part('ok', 'nok', 'part_id')
worst_part = by_part.sort_values('nok_rate_pct', ascending=False).iloc[0]
print(f"Worst part: {worst_part['part_number']} - {worst_part['nok_rate_pct']:.1f}% NOK")

# 2. What defects?
defects = QualityTracking(df).nok_by_reason('nok_counter', 'defect_reason')
print("Top defects:")
print(defects.head(3))

# 3. When did it happen?
by_shift = QualityTracking(df).nok_by_shift('ok', 'nok')
print("NOK by shift:")
print(by_shift)
```

### Use Case 3: Performance Trending

```python
# Availability trend
avail_trend = DowntimeTracking(df).availability_trend('state', window='1D')

# Quality trend
quality_trend = QualityTracking(df).daily_quality_summary('ok', 'nok')

# Merge for complete view
import pandas as pd
trend = pd.merge(avail_trend, quality_trend, left_on='period', right_on='date')

print("Weekly Trend:")
print(trend[['date', 'availability_pct', 'first_pass_yield_pct']])

# Identify improvement or degradation
if trend['availability_pct'].iloc[-1] > trend['availability_pct'].iloc[0]:
    print("✓ Availability improving!")
else:
    print("✗ Availability degrading - investigate!")
```

---

## 📚 Documentation

- **DAILY_PRODUCTION_MODULES.md** - PartProductionTracking, CycleTimeTracking, ShiftReporting
- **DOWNTIME_QUALITY_MODULES.md** - DowntimeTracking, QualityTracking
- **PRODUCTION_MODULES_SUMMARY.md** - This file - complete overview

---

## ✅ Test Coverage

All modules have comprehensive test coverage:

- **test_production_tracking.py** - 21 tests (PartProduction, CycleTime, Shift)
- **test_downtime_quality.py** - 18 tests (Downtime, Quality)
- **Total: 39 tests - 100% passing**

Coverage includes:
- Basic functionality
- Edge cases (empty data, single signals)
- Custom configurations
- Integration between modules

---

## 🎯 Summary

You now have **5 essential modules** that answer **every daily question** a plant manager asks:

1. **How many?** → PartProductionTracking, ShiftReporting
2. **How fast?** → CycleTimeTracking
3. **How much uptime?** → DowntimeTracking
4. **How good?** → QualityTracking

Combined, these modules give you:
- ✅ Complete production visibility
- ✅ Root cause analysis capability
- ✅ Shift-based performance tracking
- ✅ Trend identification
- ✅ KPI measurement (Availability, FPY, OEE)
- ✅ Daily operational dashboards
- ✅ Continuous improvement focus

**All following the simple "one UUID per signal" design principle!**

---

## 🚀 Getting Started

```python
# Install ts-shape (if not already installed)
# pip install ts-shape

# Import all production modules
from ts_shape.events.production import (
    PartProductionTracking,
    CycleTimeTracking,
    ShiftReporting,
    DowntimeTracking,
    QualityTracking,
)

# Load your data
import pandas as pd
df = pd.read_parquet('your_data.parquet')

# Start analyzing!
tracker = PartProductionTracking(df)
result = tracker.daily_production_summary('part_id_uuid', 'counter_uuid')
print(result)
```

Happy analyzing! 🎉
