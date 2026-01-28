# Production Modules Overview

Essential bread-and-butter modules for daily plant management. Every module focuses on answering the critical questions that plant managers ask every day.

## 🎯 The 5 Essential Modules

| Module | Purpose | Key Question |
|--------|---------|--------------|
| **PartProductionTracking** | Production quantity tracking | How many parts did we make? |
| **CycleTimeTracking** | Cycle time analysis | How fast are we producing? |
| **ShiftReporting** | Shift-based summaries | How did each shift perform? |
| **DowntimeTracking** | Availability & downtime | How much uptime did we have? |
| **QualityTracking** | NOK parts & defects | What's our quality rate? |

## 📊 The 4 Pillars of Manufacturing Performance

These modules give you complete visibility into manufacturing:

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

## 🚀 Quick Start

```python
from ts_shape.events.production import (
    PartProductionTracking,
    CycleTimeTracking,
    ShiftReporting,
    DowntimeTracking,
    QualityTracking,
)

# Complete daily performance dashboard
production = PartProductionTracking(df)
cycles = CycleTimeTracking(df)
downtime = DowntimeTracking(df)
quality = QualityTracking(df)

# Get the 4 key metrics
daily_prod = production.daily_production_summary('part_id', 'counter')
cycle_stats = cycles.cycle_time_statistics('part_id', 'cycle_trigger')
availability = downtime.downtime_by_shift('state', running_value='Running')
quality_metrics = quality.nok_by_shift('ok_counter', 'nok_counter')
```

## 🎓 Design Principles

All production modules follow these principles:

1. **One UUID Per Signal** - Each UUID represents exactly one signal
2. **Simple DataFrames** - All methods return pandas DataFrames
3. **Shift-Based** - Support shift analysis with custom definitions
4. **Daily Questions** - Answer practical plant manager questions
5. **No Over-Engineering** - Simple, focused implementations

## 📈 Key Performance Indicators

Track industry-standard manufacturing KPIs:

| Metric | Formula | Good | Excellent | World-Class |
|--------|---------|------|-----------|-------------|
| **Availability** | Uptime / Total Time | >85% | >90% | >95% |
| **Quality (FPY)** | Good Parts / Total | >95% | >98% | >99% |
| **OEE** | Avail × Perf × Quality | >60% | >75% | >85% |
| **NOK Rate** | Bad Parts / Total | <5% | <2% | <1% |

## 📚 Documentation Structure

- **[Quick Start](quick_start.md)** - Get up and running in 5 minutes
- **[Daily Production Tracking](daily_production.md)** - PartProductionTracking, CycleTimeTracking, ShiftReporting
- **[Downtime & Quality](downtime_quality.md)** - DowntimeTracking, QualityTracking
- **[Complete Module Guide](complete_guide.md)** - All 5 modules with examples
- **[Future Features](future_features.md)** - Roadmap and upcoming additions

## 🎯 Common Use Cases

### Morning Production Meeting

**Question**: "What was our performance yesterday?"

```python
# Get all key metrics
downtime = DowntimeTracking(df)
quality = QualityTracking(df)

yesterday_downtime = downtime.downtime_by_shift('state', running_value='Running')
yesterday_quality = quality.nok_by_shift('ok_counter', 'nok_counter')

print(f"Shift 1: {yesterday_downtime.iloc[0]['availability_pct']:.1f}% availability, "
      f"{yesterday_quality.iloc[0]['first_pass_yield_pct']:.1f}% FPY")
```

### Root Cause Investigation

**Question**: "Why did Shift 2 have such low production yesterday?"

```python
# Step 1: Check downtime
downtime = tracker.downtime_by_shift('state', running_value='Running')

# Step 2: Find root cause
reasons = tracker.downtime_by_reason('state', 'reason', stopped_value='Stopped')

# Step 3: Check quality issues
defects = quality.nok_by_reason('nok_counter', 'defect_reason')
```

### Quality Problem Analysis

**Question**: "Which part is causing quality issues?"

```python
# Check quality by part
quality = tracker.quality_by_part('ok_counter', 'nok_counter', 'part_number')

# Sort by worst NOK rate
worst_parts = quality.sort_values('nok_rate_pct', ascending=False')

# Find defect types
defects = tracker.nok_by_reason('nok_counter', 'defect_reason')
```

## ✅ Test Coverage

All modules have comprehensive test coverage:

- **test_production_tracking.py** - 21 tests (Production, Cycles, Shifts)
- **test_downtime_quality.py** - 18 tests (Downtime, Quality)
- **Total: 39 tests - 100% passing**

## 🔄 Integration with Existing Modules

Production modules integrate seamlessly with existing ts-shape components:

- **Data Loading** - Use any ts-shape loader (Parquet, Azure, S3, TimescaleDB)
- **Filters** - Pre-process data with numeric/boolean/time filters
- **Features** - Combine with existing feature extraction
- **Events** - Work alongside event detection modules

## 📦 Installation

```bash
pip install ts-shape
```

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/jakobgabriel/ts-shape/issues)
- **Source**: [GitHub Repository](https://github.com/jakobgabriel/ts-shape)
- **PyPI**: [ts-shape on PyPI](https://pypi.org/project/ts-shape/)

## 🎉 What's Next?

1. Check out the **[Quick Start Guide](quick_start.md)** to get started
2. Explore **[Daily Production Tracking](daily_production.md)** for production, cycle time, and shift modules
3. Learn about **[Downtime & Quality Tracking](downtime_quality.md)** for availability and quality metrics
4. See **[Future Features](future_features.md)** for upcoming additions like OEE tracking

---

**Ready to track your manufacturing performance?** Start with the [Quick Start Guide](quick_start.md)!
