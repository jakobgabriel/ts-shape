# CycleExtractor Enhancements Documentation

This document describes the enhancements made to the `CycleExtractor` class in `/home/user/ts-shape/src/ts_shape/features/cycles/cycles_extractor.py`.

## Table of Contents

1. [Overview](#overview)
2. [New Features](#new-features)
3. [API Reference](#api-reference)
4. [Usage Examples](#usage-examples)
5. [Backward Compatibility](#backward-compatibility)

## Overview

The `CycleExtractor` class has been enhanced with several new features to improve cycle extraction, validation, and analysis capabilities while maintaining full backward compatibility with existing code.

### Key Improvements

- **Incomplete Cycle Tracking**: All cycles now include an `is_complete` flag
- **Cycle Validation**: Validate cycles based on duration constraints
- **Overlap Detection**: Identify and optionally resolve overlapping cycles
- **Method Suggestions**: Get AI-powered recommendations for the best extraction method
- **Extraction Statistics**: Detailed statistics about the extraction process
- **Value Change Threshold**: Configure significance threshold for numeric value changes
- **Better Error Handling**: Incomplete cycles are now tracked instead of silently lost

## New Features

### 1. Incomplete Cycle Handling

**What it does**: Tracks cycles that have a start time but no matching end time, marking them as incomplete instead of silently dropping them.

**Output changes**:
- All extracted cycle DataFrames now include an `is_complete` boolean column
- Incomplete cycles have `is_complete=False` and `cycle_end=NaT` (Not a Time)

**Benefits**:
- No silent data loss
- Better understanding of extraction quality
- Ability to investigate incomplete cycles

### 2. Cycle Validation

**What it does**: Validates extracted cycles against duration constraints and completeness criteria.

**New method**: `validate_cycles(cycle_df, min_duration='1s', max_duration='1h', warn=True)`

**Parameters**:
- `cycle_df`: DataFrame with extracted cycles
- `min_duration`: Minimum acceptable duration (e.g., '1s', '5m', '1h')
- `max_duration`: Maximum acceptable duration
- `warn`: Whether to log warnings for invalid cycles

**Output columns added**:
- `cycle_duration`: Calculated duration of each cycle
- `is_valid`: Boolean indicating if cycle passes validation
- `validation_issue`: String describing any validation issues

**Validation issues**:
- `incomplete_cycle`: Cycle has no end time
- `too_short`: Cycle duration is below minimum
- `too_long`: Cycle duration exceeds maximum

### 3. Overlapping Cycle Detection

**What it does**: Identifies cycles where one cycle's time range overlaps with another's.

**New method**: `detect_overlapping_cycles(cycle_df, resolve='flag')`

**Parameters**:
- `cycle_df`: DataFrame with extracted cycles
- `resolve`: How to handle overlaps
  - `'flag'`: Only mark overlapping cycles (default)
  - `'keep_first'`: Remove later overlapping cycles
  - `'keep_last'`: Remove earlier overlapping cycles
  - `'keep_longest'`: Keep the cycle with longest duration

**Output column added**:
- `has_overlap`: Boolean indicating if cycle overlaps with another

**Use cases**:
- Data quality checks
- Identifying extraction method issues
- Cleaning cycle data for analysis

### 4. Method Selection Helper

**What it does**: Analyzes input data characteristics and recommends the most appropriate cycle extraction method(s).

**New method**: `suggest_method()`

**Returns**: Dictionary with:
- `recommended_methods`: List of method names in priority order
- `reasoning`: List of explanations for each recommendation
- `data_characteristics`: Analysis of input data

**Data characteristics analyzed**:
- Presence of boolean, integer, double, and string values
- Boolean transition patterns
- Integer value diversity (for step sequences)
- Separate start/end UUID configuration

**Example output**:
```python
{
    'recommended_methods': ['process_persistent_cycle', 'process_trigger_cycle'],
    'reasoning': [
        'Boolean transitions detected, suitable for persistent cycles',
        'Boolean data present, can use trigger-based extraction'
    ],
    'data_characteristics': {
        'has_boolean_values': True,
        'has_integer_values': True,
        'has_double_values': False,
        'has_string_values': False,
        'row_count': 1000,
        'separate_start_end': False
    }
}
```

### 5. Cycle Extraction Statistics

**What it does**: Provides detailed statistics about the most recent cycle extraction.

**New methods**:
- `get_extraction_stats()`: Returns statistics dictionary
- `reset_stats()`: Resets statistics counters

**Statistics tracked**:
- `total_cycles`: Total number of cycles extracted
- `complete_cycles`: Number of complete cycles
- `incomplete_cycles`: Number of incomplete cycles
- `unmatched_starts`: Cycle starts with no matching end
- `unmatched_ends`: Cycle ends with no matching start
- `overlapping_cycles`: Number of overlapping cycle pairs detected
- `success_rate`: Ratio of complete to total cycles
- `warnings`: List of warning messages generated
- `configuration`: Extraction configuration used

**Use cases**:
- Quality assurance
- Debugging extraction issues
- Monitoring extraction performance
- Automated testing and validation

### 6. Improved Iterator Handling

**What changed**: The internal `_generate_cycle_dataframe()` method now continues processing all cycle starts even when cycle ends run out, marking remaining cycles as incomplete.

**Previous behavior**: Silently stopped processing when cycle ends were exhausted.

**New behavior**:
- Continues processing all starts
- Marks incomplete cycles with `is_complete=False`
- Logs warnings for each incomplete cycle
- Maintains statistics about unmatched starts

### 7. Value Change Significance Threshold

**What it does**: Allows configuration of a threshold for determining when numeric value changes are significant enough to trigger a new cycle.

**New parameter**: `value_change_threshold` in `__init__()`

**Default**: `0.0` (any change is significant)

**How it works**:
- For `value_double` and `value_integer` columns
- Change must exceed threshold: `abs(diff) > threshold`
- Boolean and string changes always considered significant
- Applied in `process_value_change_cycle()` method

**Use cases**:
- Filtering out noise in sensor data
- Ignoring minor fluctuations
- Focusing on significant state transitions

## API Reference

### Constructor

```python
CycleExtractor(
    dataframe: pd.DataFrame,
    start_uuid: str,
    end_uuid: Optional[str] = None,
    value_change_threshold: float = 0.0
)
```

**New parameter**:
- `value_change_threshold`: Minimum threshold for numeric value changes (default: 0.0)

### New Methods

#### validate_cycles()

```python
validate_cycles(
    cycle_df: pd.DataFrame,
    min_duration: str = '1s',
    max_duration: str = '1h',
    warn: bool = True
) -> pd.DataFrame
```

Validates cycles based on duration constraints.

**Parameters**:
- `cycle_df`: DataFrame with cycle data (output from process_* methods)
- `min_duration`: Minimum acceptable cycle duration (default: '1s')
- `max_duration`: Maximum acceptable cycle duration (default: '1h')
- `warn`: Whether to log warnings for invalid cycles (default: True)

**Returns**: DataFrame with added columns:
- `cycle_duration`: Duration of each cycle
- `is_valid`: Whether cycle passes validation
- `validation_issue`: Description of validation issues

**Duration format**: Number followed by unit:
- `s`: seconds (e.g., '30s')
- `m`: minutes (e.g., '5m')
- `h`: hours (e.g., '2h')
- `d`: days (e.g., '1d')

#### detect_overlapping_cycles()

```python
detect_overlapping_cycles(
    cycle_df: pd.DataFrame,
    resolve: str = 'flag'
) -> pd.DataFrame
```

Detects and optionally resolves overlapping cycles.

**Parameters**:
- `cycle_df`: DataFrame with cycle data
- `resolve`: How to handle overlaps
  - `'flag'`: Only mark overlapping cycles (default)
  - `'keep_first'`: Remove later overlapping cycles
  - `'keep_last'`: Remove earlier overlapping cycles
  - `'keep_longest'`: Keep cycles with longest duration

**Returns**: DataFrame with `has_overlap` column added (and potentially filtered rows)

#### suggest_method()

```python
suggest_method() -> Dict[str, Any]
```

Suggests the best cycle extraction method based on data characteristics.

**Returns**: Dictionary with:
- `recommended_methods`: List of recommended method names
- `reasoning`: List of explanations for each recommendation
- `data_characteristics`: Dictionary of analyzed data properties

#### get_extraction_stats()

```python
get_extraction_stats() -> Dict[str, Any]
```

Gets statistics about the last cycle extraction.

**Returns**: Dictionary with extraction statistics:
- `total_cycles`: Total cycles extracted
- `complete_cycles`: Number of complete cycles
- `incomplete_cycles`: Number of incomplete cycles
- `unmatched_starts`: Starts without matching ends
- `unmatched_ends`: Ends without matching starts
- `overlapping_cycles`: Number of overlapping pairs
- `success_rate`: Ratio of complete to total cycles
- `warnings`: List of warning messages
- `configuration`: Extraction configuration

#### reset_stats()

```python
reset_stats() -> None
```

Resets extraction statistics to initial values.

### Modified Methods

All existing `process_*` methods now return DataFrames with an additional `is_complete` column:

- `process_persistent_cycle()`
- `process_trigger_cycle()`
- `process_separate_start_end_cycle()`
- `process_step_sequence(start_step, end_step)`
- `process_state_change_cycle()`
- `process_value_change_cycle()`

## Usage Examples

### Example 1: Basic Usage with Incomplete Cycle Tracking

```python
from ts_shape.features.cycles.cycles_extractor import CycleExtractor
import pandas as pd

# Create extractor
df = pd.DataFrame(...)  # Your data
extractor = CycleExtractor(df, start_uuid='machine-status')

# Extract cycles
cycles = extractor.process_persistent_cycle()

# Check for incomplete cycles
print(f"Total cycles: {len(cycles)}")
print(f"Complete: {cycles['is_complete'].sum()}")
print(f"Incomplete: {(~cycles['is_complete']).sum()}")

# Filter out incomplete cycles if needed
complete_cycles = cycles[cycles['is_complete']]
```

### Example 2: Validation Workflow

```python
# Extract cycles
cycles = extractor.process_persistent_cycle()

# Validate with duration constraints
validated = extractor.validate_cycles(
    cycles,
    min_duration='10s',
    max_duration='5m',
    warn=True
)

# Get only valid cycles
valid_cycles = validated[validated['is_valid']]

# Investigate invalid cycles
invalid_cycles = validated[~validated['is_valid']]
print(invalid_cycles[['cycle_start', 'validation_issue']])
```

### Example 3: Overlap Detection and Resolution

```python
# Extract cycles
cycles = extractor.process_persistent_cycle()

# Detect overlaps
cycles_with_flags = extractor.detect_overlapping_cycles(cycles, resolve='flag')
print(f"Overlapping cycles: {cycles_with_flags['has_overlap'].sum()}")

# Resolve by keeping first occurrence
clean_cycles = extractor.detect_overlapping_cycles(cycles, resolve='keep_first')

# Or resolve by keeping longest cycles
clean_cycles = extractor.detect_overlapping_cycles(cycles, resolve='keep_longest')
```

### Example 4: Method Selection

```python
# Get method suggestions before extraction
suggestions = extractor.suggest_method()

print("Recommended methods:")
for method, reason in zip(suggestions['recommended_methods'], suggestions['reasoning']):
    print(f"- {method}: {reason}")

# Use the first recommended method
recommended_method = suggestions['recommended_methods'][0]
if recommended_method == 'process_persistent_cycle':
    cycles = extractor.process_persistent_cycle()
elif recommended_method == 'process_trigger_cycle':
    cycles = extractor.process_trigger_cycle()
# ... etc
```

### Example 5: Statistics and Monitoring

```python
# Extract cycles
cycles = extractor.process_persistent_cycle()

# Get statistics
stats = extractor.get_extraction_stats()

print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Complete cycles: {stats['complete_cycles']}")
print(f"Incomplete cycles: {stats['incomplete_cycles']}")
print(f"Warnings: {len(stats['warnings'])}")

# Check if extraction quality is acceptable
if stats['success_rate'] < 0.95:
    print("Warning: Low success rate detected!")
    print("Warnings:", stats['warnings'])
```

### Example 6: Value Change Threshold

```python
# Create extractor with threshold for significant changes
extractor = CycleExtractor(
    df,
    start_uuid='temperature-sensor',
    value_change_threshold=2.5  # Ignore changes < 2.5 units
)

# Extract cycles (only significant value changes trigger new cycles)
cycles = extractor.process_value_change_cycle()
```

### Example 7: Complete Workflow

```python
# 1. Initialize with threshold
extractor = CycleExtractor(df, start_uuid='process-id', value_change_threshold=1.0)

# 2. Get method suggestions
suggestions = extractor.suggest_method()
print(f"Using: {suggestions['recommended_methods'][0]}")

# 3. Extract cycles
cycles = extractor.process_persistent_cycle()

# 4. Validate
validated = extractor.validate_cycles(cycles, min_duration='5s', max_duration='2m')

# 5. Check for overlaps
clean_cycles = extractor.detect_overlapping_cycles(
    validated[validated['is_valid']],
    resolve='keep_longest'
)

# 6. Review statistics
stats = extractor.get_extraction_stats()
print(f"Final: {len(clean_cycles)} cycles, {stats['success_rate']:.1%} success rate")

# 7. Use clean cycles for analysis
final_cycles = clean_cycles[clean_cycles['is_complete'] & clean_cycles['is_valid']]
```

## Backward Compatibility

All enhancements are **fully backward compatible** with existing code:

### What Stays the Same

1. **All existing methods work unchanged**:
   - `process_persistent_cycle()`
   - `process_trigger_cycle()`
   - `process_separate_start_end_cycle()`
   - `process_step_sequence()`
   - `process_state_change_cycle()`
   - `process_value_change_cycle()`

2. **Existing return columns preserved**:
   - `cycle_start`
   - `cycle_end`
   - `cycle_uuid`

3. **Constructor still works with original parameters**:
   ```python
   # Old code continues to work
   extractor = CycleExtractor(df, start_uuid='my-uuid')
   extractor = CycleExtractor(df, start_uuid='start-uuid', end_uuid='end-uuid')
   ```

### What's New (Opt-in)

1. **New column added**: `is_complete` (can be ignored if not needed)
2. **New optional parameter**: `value_change_threshold` (defaults to 0.0 for original behavior)
3. **New methods**: All new methods are additions and don't affect existing functionality

### Migration Notes

No migration needed! Existing code will continue to work without changes. To use new features:

1. **For incomplete cycle tracking**: Simply use the new `is_complete` column
2. **For validation**: Call `validate_cycles()` on extracted cycles
3. **For overlap detection**: Call `detect_overlapping_cycles()` on extracted cycles
4. **For method suggestions**: Call `suggest_method()` before extraction
5. **For statistics**: Call `get_extraction_stats()` after extraction

## Performance Considerations

- **Validation**: O(n) where n is the number of cycles
- **Overlap detection**: O(n²) worst case, but typically much faster as it breaks early
- **Overlap resolution**: O(n) additional overhead
- **Method suggestion**: O(m) where m is the number of data rows
- **Statistics**: Negligible overhead (computed during extraction)

## Testing

A comprehensive demonstration script is available at:
`/home/user/ts-shape/examples/cycle_extractor_enhancements_demo.py`

Run it to see all features in action:
```bash
python examples/cycle_extractor_enhancements_demo.py
```

## Future Enhancements

Possible future additions (not yet implemented):

1. Custom validation rules
2. Cycle gap analysis
3. Automatic overlap resolution strategy selection
4. Parallel cycle extraction for large datasets
5. Cycle quality scoring
6. Interactive visualization of cycles and issues

## Support

For issues or questions about these enhancements, please refer to:
- Source code: `/home/user/ts-shape/src/ts_shape/features/cycles/cycles_extractor.py`
- Demo script: `/home/user/ts-shape/examples/cycle_extractor_enhancements_demo.py`
- This documentation: `/home/user/ts-shape/docs/CYCLE_EXTRACTOR_ENHANCEMENTS.md`
