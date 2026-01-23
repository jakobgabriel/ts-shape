# Production Modules - Correct Import Structure

## ✅ Correct Import Path

All production tracking modules are now located in `ts_shape.events.production`:

```python
from ts_shape.events.production import (
    # Daily Production Tracking
    PartProductionTracking,
    CycleTimeTracking,
    ShiftReporting,
    DowntimeTracking,
    QualityTracking,

    # Event Detection (existing)
    MachineStateEvents,
    LineThroughputEvents,
    ChangeoverEvents,
    FlowConstraintEvents,
)
```

## 📁 Module Organization

### File Structure

```
src/ts_shape/events/production/
├── __init__.py                    # Exports all classes
│
├── Event Detection (existing):
│   ├── machine_state.py           # MachineStateEvents
│   ├── line_throughput.py         # LineThroughputEvents
│   ├── changeover.py              # ChangeoverEvents
│   ├── flow_constraints.py        # FlowConstraintEvents
│   └── downtime.py                # (empty placeholder)
│
└── Daily Production Tracking (new):
    ├── part_tracking.py           # PartProductionTracking
    ├── cycle_time_tracking.py    # CycleTimeTracking
    ├── shift_reporting.py         # ShiftReporting
    ├── downtime_tracking.py       # DowntimeTracking
    └── quality_tracking.py        # QualityTracking
```

### Architecture Rationale

**Why under `events/production/`?**

1. **Consistency**: Follows existing ts-shape architecture where production functionality lives under events/
2. **Logical Grouping**: Both event detection and tracking are production-related
3. **Single Import Source**: Users import all production tools from one location
4. **Namespace Organization**: Clear separation within the events namespace

## 🔄 Migration Guide

If you were using the old import path (from earlier in this session):

### Before (Incorrect)
```python
# ❌ This was temporary and incorrect
from ts_shape.production import PartProductionTracking
```

### After (Correct)
```python
# ✅ This is the correct, permanent path
from ts_shape.events.production import PartProductionTracking
```

## 📊 Usage Examples

### Example 1: Complete Daily Dashboard

```python
from ts_shape.events.production import (
    PartProductionTracking,
    CycleTimeTracking,
    DowntimeTracking,
    QualityTracking,
)

# Quantity
production = PartProductionTracking(df)
daily_prod = production.daily_production_summary('part_id', 'counter')

# Speed
cycles = CycleTimeTracking(df)
cycle_stats = cycles.cycle_time_statistics('part_id', 'cycle_trigger')

# Availability
downtime = DowntimeTracking(df)
availability = downtime.downtime_by_shift('state', running_value='Running')

# Quality
quality = QualityTracking(df)
quality_metrics = quality.nok_by_shift('ok_counter', 'nok_counter')
```

### Example 2: Event Detection + Tracking

```python
from ts_shape.events.production import (
    # Event detection
    MachineStateEvents,
    ChangeoverEvents,

    # Daily tracking
    DowntimeTracking,
    PartProductionTracking,
)

# Detect machine state events
state_events = MachineStateEvents(df)
run_idle = state_events.detect_run_idle('machine_running_uuid')

# Track downtime
downtime = DowntimeTracking(df)
shift_downtime = downtime.downtime_by_shift('machine_state_uuid')

# Detect changeovers
changeovers = ChangeoverEvents(df)
changeover_events = changeovers.detect_changeover('part_number_uuid')

# Track production by part
production = PartProductionTracking(df)
by_part = production.production_by_part('part_number_uuid', 'counter_uuid')
```

## ✅ Verification

### Check Your Installation

```python
# Verify correct import
from ts_shape.events.production import PartProductionTracking

print("✓ Import successful!")
```

### Run Tests

```bash
# All tests use the correct import path
pytest tests/test_production_tracking.py tests/test_downtime_quality.py -v
```

Expected output: `39 passed`

## 📚 Documentation References

All documentation has been updated to use the correct import path:

- ✅ `DAILY_PRODUCTION_MODULES.md`
- ✅ `DOWNTIME_QUALITY_MODULES.md`
- ✅ `PRODUCTION_MODULES_SUMMARY.md`
- ✅ `FUTURE_PRODUCTION_FEATURES.md`
- ✅ `docs/user_guide/quick_start.md`
- ✅ `docs/production/overview.md`
- ✅ All .rst API documentation files

## 🎯 Key Points

1. **Import from**: `ts_shape.events.production`
2. **NOT from**: `ts_shape.production` (doesn't exist)
3. **All modules available**: Both event detection and daily tracking
4. **Tests verified**: 39/39 passing with correct imports
5. **Documentation updated**: All examples use correct path

## 🔍 What Changed?

**Before this refactor**:
- Production tracking modules were in `src/ts_shape/production/` (incorrect)
- Event detection modules were in `src/ts_shape/events/production/` (correct)
- Split across two locations

**After this refactor**:
- ALL production functionality in `src/ts_shape/events/production/`
- Single import source for all production tools
- Consistent with existing codebase architecture

## 📦 Module Exports

The `__init__.py` in `events/production/` exports:

**Event Detection** (4 classes):
1. `MachineStateEvents` - Run/idle state detection
2. `LineThroughputEvents` - Throughput and takt time
3. `ChangeoverEvents` - Product changeover detection
4. `FlowConstraintEvents` - Blocked/starved detection

**Daily Production Tracking** (5 classes):
1. `PartProductionTracking` - Production quantities by part
2. `CycleTimeTracking` - Cycle time analysis
3. `ShiftReporting` - Shift-based reporting
4. `DowntimeTracking` - Downtime and availability
5. `QualityTracking` - NOK and quality metrics

Total: **9 production-related classes** in one namespace.

## ✨ Benefits

1. **Single Source**: Import all production functionality from one location
2. **Clear Namespace**: `events.production` clearly indicates production events and tracking
3. **Maintainable**: All production code in one directory
4. **Consistent**: Follows ts-shape's existing architecture patterns
5. **Future-Proof**: Easy to add new production modules in the same location

---

**Bottom Line**: Always import from `ts_shape.events.production`! 🎯
