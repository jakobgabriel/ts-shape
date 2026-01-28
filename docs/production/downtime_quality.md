# Downtime and Quality Tracking Modules

Essential bread-and-butter modules for daily plant management. Every plant manager asks these questions:
- "How much downtime did we have per shift?"
- "What are our top downtime reasons?"
- "What's our NOK rate today?"
- "Which part numbers have quality issues?"

## Overview

Two new production tracking modules:

1. **DowntimeTracking** - Machine downtime and availability analysis
2. **QualityTracking** - NOK (defective parts) and quality metrics

Both modules follow the simple **one UUID per signal** design principle and provide shift-based reporting.

## Module 1: DowntimeTracking

Track machine downtimes, availability, and identify top reasons for production losses.

### Quick Start

```python
from ts_shape.events.production import DowntimeTracking

# Initialize tracker
tracker = DowntimeTracking(df)

# Downtime per shift
shift_downtime = tracker.downtime_by_shift(
    state_uuid='machine_state_signal',
    running_value='Running'
)

# Top downtime reasons (Pareto analysis)
top_reasons = tracker.top_downtime_reasons(
    state_uuid='machine_state_signal',
    reason_uuid='downtime_reason_signal',
    top_n=5
)
```

### Data Requirements

#### Required Signals:
- **state_uuid**: Machine state signal (string)
  - Values: 'Running', 'Stopped', 'Idle', etc.
  - Delta tracking recommended

#### Optional Signals:
- **reason_uuid**: Downtime reason code (string)
  - Values: 'Material_Shortage', 'Tool_Change', 'Quality_Issue', etc.
  - Used for root cause analysis

### Methods

#### 1. `downtime_by_shift()`

Calculate downtime and availability per shift.

```python
result = tracker.downtime_by_shift(
    state_uuid='machine_state',
    running_value='Running'
)

# Returns:
#     date        shift    total_minutes  downtime_minutes  uptime_minutes  availability_pct
# 0   2024-01-01  shift_1  480            45.2             434.8           90.6
# 1   2024-01-01  shift_2  480            67.5             412.5           85.9
# 2   2024-01-01  shift_3  480            92.0             388.0           80.8
```

**Use Cases:**
- Morning production meetings: "What was our availability yesterday?"
- Shift handover: "How much downtime did we have?"
- Trend identification: "Which shift has the most downtime?"

#### 2. `downtime_by_reason()`

Analyze downtime by reason code - identify root causes.

```python
result = tracker.downtime_by_reason(
    state_uuid='machine_state',
    reason_uuid='downtime_reason',
    stopped_value='Stopped'
)

# Returns:
#     reason              occurrences  total_minutes  avg_minutes  pct_of_total
# 0   Material_Shortage   12           145.5         12.1         35.2
# 1   Tool_Change         8            98.2          12.3         23.8
# 2   Quality_Issue       5            76.0          15.2         18.4
```

**Use Cases:**
- Root cause analysis: "What's causing most downtime?"
- Prioritization: "Which problem should we fix first?"
- Improvement tracking: "Is our material shortage issue getting better?"

#### 3. `top_downtime_reasons()`

Pareto analysis - focus on the vital few (80/20 rule).

```python
result = tracker.top_downtime_reasons(
    state_uuid='machine_state',
    reason_uuid='downtime_reason',
    top_n=5
)

# Returns:
#     reason              total_minutes  pct_of_total  cumulative_pct
# 0   Material_Shortage   145.5         35.2          35.2
# 1   Tool_Change         98.2          23.8          59.0
# 2   Quality_Issue       76.0          18.4          77.4
# 3   Maintenance         45.0          10.9          88.3
# 4   Changeover          30.5          7.4           95.7
```

**Use Cases:**
- Focus improvement efforts on top 3 reasons (usually 70-80% of total downtime)
- Weekly review: "What are the biggest time wasters?"
- Lean/Six Sigma projects: "Where should we start?"

#### 4. `availability_trend()`

Track availability over time to identify degradation or improvement.

```python
result = tracker.availability_trend(
    state_uuid='machine_state',
    running_value='Running',
    window='1D'  # Daily trend
)

# Returns:
#     period      availability_pct  uptime_minutes  downtime_minutes
# 0   2024-01-01  87.5             1260.0          180.0
# 1   2024-01-02  91.2             1313.3          126.7
# 2   2024-01-03  85.8             1235.5          204.5
```

**Use Cases:**
- Identify trends: "Is our availability improving or degrading?"
- Equipment health: "Is this machine becoming unreliable?"
- Maintenance effectiveness: "Did the preventive maintenance help?"

### Custom Shift Definitions

```python
# 2-shift operation
custom_shifts = {
    'day': ('06:00', '18:00'),
    'night': ('18:00', '06:00'),
}

tracker = DowntimeTracking(df, shift_definitions=custom_shifts)
```

---

## Module 2: QualityTracking

Track NOK (Not OK/defective) parts, quality rates, and identify defect patterns.

### Quick Start

```python
from ts_shape.events.production import QualityTracking

# Initialize tracker
tracker = QualityTracking(df)

# NOK parts per shift
shift_quality = tracker.nok_by_shift(
    ok_counter_uuid='good_parts_counter',
    nok_counter_uuid='bad_parts_counter'
)

# Quality by part number
part_quality = tracker.quality_by_part(
    ok_counter_uuid='good_parts_counter',
    nok_counter_uuid='bad_parts_counter',
    part_id_uuid='part_number_signal'
)
```

### Data Requirements

#### Required Signals:
- **ok_counter_uuid**: Good parts counter (integer)
  - Monotonically increasing counter for OK parts
  - Delta tracking recommended

- **nok_counter_uuid**: Defective parts counter (integer)
  - Monotonically increasing counter for NOK parts
  - Delta tracking recommended

#### Optional Signals:
- **part_id_uuid**: Part number signal (string)
  - Current part number being produced
  - Enables quality tracking by part

- **defect_reason_uuid**: Defect reason code (string)
  - Root cause of quality issue
  - Examples: 'Dimension_Error', 'Surface_Defect', 'Wrong_Color'

### Methods

#### 1. `nok_by_shift()`

Track NOK parts and quality rates per shift.

```python
result = tracker.nok_by_shift(
    ok_counter_uuid='good_parts',
    nok_counter_uuid='bad_parts'
)

# Returns:
#     date        shift    ok_parts  nok_parts  total_parts  nok_rate_pct  first_pass_yield_pct
# 0   2024-01-01  shift_1  450       12         462          2.6           97.4
# 1   2024-01-01  shift_2  425       18         443          4.1           95.9
# 2   2024-01-01  shift_3  380       25         405          6.2           93.8
```

**Use Cases:**
- Morning meetings: "What was our quality yesterday?"
- Shift comparison: "Which shift has quality issues?"
- Target tracking: "Are we meeting our <2% NOK target?"

#### 2. `quality_by_part()`

Analyze quality metrics for each part number.

```python
result = tracker.quality_by_part(
    ok_counter_uuid='good_parts',
    nok_counter_uuid='bad_parts',
    part_id_uuid='part_number'
)

# Returns:
#     part_number  ok_parts  nok_parts  total_parts  nok_rate_pct  first_pass_yield_pct
# 0   PART_A       1255      55         1310         4.2           95.8
# 1   PART_B       890       38         928          4.1           95.9
# 2   PART_C       2150      45         2195         2.1           97.9
```

**Use Cases:**
- Problem identification: "Which part has quality issues?"
- Customer reporting: "What's the FPY for part XYZ?"
- Process validation: "Is PART_A meeting the 95% FPY requirement?"

#### 3. `nok_by_reason()`

Pareto analysis of defect reasons.

```python
result = tracker.nok_by_reason(
    nok_counter_uuid='bad_parts',
    defect_reason_uuid='defect_reason'
)

# Returns:
#     reason              nok_parts  pct_of_total
# 0   Dimension_Error     45         40.5
# 1   Surface_Defect      28         25.2
# 2   Wrong_Color         22         19.8
# 3   Material_Defect     12         10.8
```

**Use Cases:**
- Root cause analysis: "What's our #1 quality problem?"
- Focus improvement: "Fix dimension errors = 40% reduction in scrap"
- Supplier issues: "Material defects are 11% of our quality problems"

#### 4. `daily_quality_summary()`

Daily quality rollup across all shifts.

```python
result = tracker.daily_quality_summary(
    ok_counter_uuid='good_parts',
    nok_counter_uuid='bad_parts'
)

# Returns:
#     date        ok_parts  nok_parts  total_parts  nok_rate_pct  first_pass_yield_pct
# 0   2024-01-01  1255      55         1310         4.2           95.8
# 1   2024-01-02  1308      42         1350         3.1           96.9
# 2   2024-01-03  1290      60         1350         4.4           95.6
```

**Use Cases:**
- Daily reports: "Yesterday's FPY: 96.9%"
- Weekly trends: "Quality improving - down from 4.2% to 3.1% NOK"
- Month-end summaries

---

## Real-World Examples

### Example 1: Daily Production Meeting

**Question**: "What was our performance yesterday?"

```python
from ts_shape.events.production import DowntimeTracking, QualityTracking

# Downtime analysis
downtime_tracker = DowntimeTracking(df)
yesterday_downtime = downtime_tracker.downtime_by_shift(
    state_uuid='machine_state',
    running_value='Running'
)

# Quality analysis
quality_tracker = QualityTracking(df)
yesterday_quality = quality_tracker.nok_by_shift(
    ok_counter_uuid='ok_counter',
    nok_counter_uuid='nok_counter'
)

# Combine for complete picture
print("Yesterday's Performance:")
print(f"Shift 1: {yesterday_downtime.iloc[0]['availability_pct']:.1f}% availability, "
      f"{yesterday_quality.iloc[0]['first_pass_yield_pct']:.1f}% FPY")
```

### Example 2: Root Cause Investigation

**Question**: "Why did Shift 2 have such low production yesterday?"

```python
# Step 1: Check downtime
downtime = tracker.downtime_by_shift(
    state_uuid='machine_state',
    running_value='Running'
)
shift_2 = downtime[downtime['shift'] == 'shift_2']
print(f"Shift 2 had {shift_2['downtime_minutes'].values[0]:.0f} minutes downtime")

# Step 2: Find root cause
reasons = tracker.downtime_by_reason(
    state_uuid='machine_state',
    reason_uuid='downtime_reason',
    stopped_value='Stopped'
)
print("Top 3 reasons:")
print(reasons.head(3))

# Answer: "Material shortage caused 145 minutes of downtime (35% of total)"
```

### Example 3: Quality Problem Analysis

**Question**: "Which part is causing quality issues?"

```python
# Check quality by part
quality = tracker.quality_by_part(
    ok_counter_uuid='ok_counter',
    nok_counter_uuid='nok_counter',
    part_id_uuid='part_number'
)

# Sort by worst NOK rate
worst_parts = quality.sort_values('nok_rate_pct', ascending=False)
print("Parts with highest NOK rates:")
print(worst_parts[['part_number', 'nok_rate_pct', 'nok_parts']].head(3))

# Find defect types for worst part
defects = tracker.nok_by_reason(
    nok_counter_uuid='nok_counter',
    defect_reason_uuid='defect_reason'
)
print(f"\nTop defects:")
print(defects.head(3))
```

### Example 4: Weekly Performance Review

**Question**: "How did we trend this week?"

```python
# Availability trend
availability = tracker.availability_trend(
    state_uuid='machine_state',
    running_value='Running',
    window='1D'
)

# Quality trend
quality = tracker.daily_quality_summary(
    ok_counter_uuid='ok_counter',
    nok_counter_uuid='nok_counter'
)

# Merge and analyze
import pandas as pd
weekly = pd.merge(availability, quality, left_on='period', right_on='date')

print("Weekly Performance:")
print(weekly[['date', 'availability_pct', 'first_pass_yield_pct', 'nok_rate_pct']])

# Calculate OEE (simplified)
weekly['oee_approx'] = (weekly['availability_pct'] * weekly['first_pass_yield_pct']) / 100
print(f"\nAverage weekly OEE: {weekly['oee_approx'].mean():.1f}%")
```

---

## Integration with Other Modules

These modules work seamlessly with the existing production tracking modules:

```python
from ts_shape.events.production import (
    PartProductionTracking,
    CycleTimeTracking,
    ShiftReporting,
    DowntimeTracking,
    QualityTracking,
)

# Complete daily report
production = PartProductionTracking(df)
cycles = CycleTimeTracking(df)
downtime = DowntimeTracking(df)
quality = QualityTracking(df)

# Production: How many parts?
prod_by_shift = production.daily_production_summary('part_id', 'counter')

# Speed: How fast were cycles?
cycle_stats = cycles.cycle_time_statistics('part_id', 'cycle_trigger')

# Availability: How much uptime?
availability = downtime.downtime_by_shift('state', running_value='Running')

# Quality: How good were parts?
quality_metrics = quality.nok_by_shift('ok_counter', 'nok_counter')

# Now you have the complete picture!
```

---

## Key Metrics Explained

### Availability
```
Availability % = (Uptime / Total Time) × 100
```
Target: Usually >85% for good performance, >95% for world-class

### NOK Rate
```
NOK Rate % = (Defective Parts / Total Parts) × 100
```
Target: Usually <5%, <2% for critical parts

### First Pass Yield (FPY)
```
FPY % = (Good Parts / Total Parts) × 100 = 100% - NOK Rate %
```
Target: Usually >95%, >98% for critical parts

### Simplified OEE
```
OEE % = Availability % × FPY % / 100
```
Example: 90% availability × 96% FPY = 86.4% OEE
Target: >85% is world-class manufacturing

---

## Tips and Best Practices

### 1. Custom Shift Definitions
Match your actual plant shifts:
```python
# Continental shift pattern
shifts = {
    'morning': ('06:00', '14:00'),
    'afternoon': ('14:00', '22:00'),
    'night': ('22:00', '06:00'),
}

# 2-shift operation
shifts = {
    'day': ('07:00', '19:00'),
    'night': ('19:00', '07:00'),
}
```

### 2. Focus on the Vital Few
Use Pareto analysis (80/20 rule):
- Fix top 3 downtime reasons → typically 70-80% improvement potential
- Fix top 3 defect types → biggest quality impact
- Don't try to fix everything at once

### 3. Set Realistic Targets
Based on industry benchmarks:
- Availability: 85% good, 90% excellent, 95% world-class
- FPY: 95% good, 98% excellent, 99% world-class
- OEE: 60% typical, 85% world-class

### 4. Daily Monitoring
Create a simple daily dashboard:
- Yesterday's availability by shift
- Yesterday's NOK rate by shift
- Top 3 downtime reasons this week
- Top 3 defect types this week

### 5. Trend Analysis
Look for patterns:
- Does one shift always have more downtime?
- Does quality degrade as shifts progress?
- Are there day-of-week patterns?
- Use `availability_trend()` and `daily_quality_summary()` for this

---

## Summary

**DowntimeTracking** answers:
- ✅ How much downtime per shift?
- ✅ What caused the downtime?
- ✅ What's our availability?
- ✅ Where should we focus improvement?

**QualityTracking** answers:
- ✅ How many NOK parts per shift?
- ✅ Which parts have quality issues?
- ✅ What defects are most common?
- ✅ What's our first pass yield?

Together with the existing production modules, you now have complete visibility into:
1. **Production** - How many parts?
2. **Speed** - How fast?
3. **Availability** - How much uptime?
4. **Quality** - How good?

This gives you everything needed for effective daily plant management and continuous improvement!
