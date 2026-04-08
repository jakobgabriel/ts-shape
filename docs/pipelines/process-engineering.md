# Process Engineering Pipeline

> From Azure Blob timeseries to setpoint adherence, startup detection, control loop health, and process stability scores.

**Signals needed:**

| Role | UUID example | Type | Description |
|------|-------------|------|-------------|
| Setpoint | `temperature_setpoint` | `value_double` | Target value from recipe/PLC |
| Actual value | `temperature_actual` | `value_double` | Measured process value (PV) |
| Controller output | `temperature_output` | `value_double` | Control valve position / PID output (optional) |

**Modules used:** [AzureBlobParquetLoader](../reference/ts_shape/loader/timeseries/azure_blob_loader.md) | [MetadataJsonLoader](../reference/ts_shape/loader/metadata/metadata_json_loader.md) | [ContextEnricher](../reference/ts_shape/loader/context/context_enricher.md) | [DataHarmonizer](../reference/ts_shape/transform/harmonization.md) | [SetpointChangeEvents](../reference/ts_shape/events/engineering/setpoint_events.md) | [StartupDetectionEvents](../reference/ts_shape/events/engineering/startup_events.md) | [SteadyStateDetectionEvents](../reference/ts_shape/events/engineering/steady_state_detection.md) | [ControlLoopHealthEvents](../reference/ts_shape/events/engineering/control_loop_health.md) | [ProcessStabilityIndex](../reference/ts_shape/events/engineering/process_stability_index.md)

---

## Prerequisites

```python
AZURE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."
CONTAINER = "timeseries-data"

UUID_LIST = [
    "temperature_setpoint",   # double: target value
    "temperature_actual",     # double: process value (PV)
    "temperature_output",     # double: controller output (optional)
]

START = "2024-06-01"
END   = "2024-06-08"

METADATA_PATH = "config/signal_metadata.json"

# Process specifications
TARGET_VALUE = 100.0
UPPER_SPEC = 105.0
LOWER_SPEC = 95.0
```

---

## Step 1: Load Data from Azure

```python
from ts_shape.loader.timeseries.azure_blob_loader import AzureBlobParquetLoader

loader = AzureBlobParquetLoader(
    connection_string=AZURE_CONNECTION,
    container_name=CONTAINER,
)

df = loader.load_files_by_time_range_and_uuids(
    start_timestamp=START,
    end_timestamp=END,
    uuid_list=UUID_LIST,
)

print(f"Loaded {len(df):,} rows, {df['uuid'].nunique()} signals")
```

---

## Step 2: Enrich with Metadata

```python
from ts_shape.loader.metadata.metadata_json_loader import MetadataJsonLoader
from ts_shape.loader.context.context_enricher import ContextEnricher

meta = MetadataJsonLoader.from_file(METADATA_PATH)
enricher = ContextEnricher(df)
df = enricher.enrich_with_metadata(meta.to_df(), columns=["description", "unit", "area"])
```

---

## Step 3: Validate Data Quality & Harmonize

```python
from ts_shape.transform.harmonization import DataHarmonizer

harmonizer = DataHarmonizer(df, value_column="value_double")

# Check for gaps in both signals
gaps = harmonizer.detect_gaps(threshold="10s")
if not gaps.empty:
    print("Signal gaps:")
    print(gaps.groupby("uuid")["gap_duration"].agg(["count", "max"]))

# Resample to uniform 1-second grid for clean alignment
df_uniform = harmonizer.resample_to_uniform(freq="1s", method="linear")
print(f"Uniform grid: {len(df_uniform)} rows")
```

!!! tip "Why harmonize?"
    Setpoint and actual value signals often arrive at different rates (setpoint changes only on recipe switch, PV updates every second). Resampling to a uniform grid ensures correct SP-PV alignment for control loop analysis.

```python
# Align setpoint and actual for side-by-side analysis
aligned = harmonizer.align_asof(
    left_uuid="temperature_setpoint",
    right_uuid="temperature_actual",
    tolerance="2s",
    direction="nearest",
)
print(aligned.head())
```

---

## Step 4: Detect Setpoint Changes

```python
from ts_shape.events.engineering.setpoint_events import SetpointChangeEvents

sp_events = SetpointChangeEvents(
    dataframe=df,
    setpoint_uuid="temperature_setpoint",
)

# Detect step changes (magnitude >= 1.0 degree)
steps = sp_events.detect_setpoint_steps(min_delta=1.0, min_hold="30s")
print(f"Setpoint steps detected: {len(steps)}")
if not steps.empty:
    print(steps[["start", "magnitude", "prev_level", "new_level"]].head())
```

```python
# Measure how well the process follows setpoint changes
settling = sp_events.settling_time(
    actual_uuid="temperature_actual",
    min_delta=1.0,
    band_pct=0.02,     # 2% settling band
    max_window="5min",
)
print(f"Average settling time: {settling['settling_seconds'].mean():.1f}s")

# Overshoot analysis
overshoot = sp_events.overshoot(
    actual_uuid="temperature_actual",
    min_delta=1.0,
    max_window="5min",
)
print(f"Average overshoot: {overshoot['overshoot_pct'].mean():.1f}%")
```

---

## Step 5: Startup Detection

```python
from ts_shape.events.engineering.startup_events import StartupDetectionEvents

startup = StartupDetectionEvents(
    dataframe=df,
    target_uuid="temperature_actual",
)

# Detect startups by threshold crossing
startups = startup.detect_startup_by_threshold(
    threshold=50.0,          # process considered "started" above 50 degrees
    min_above="60s",         # must stay above for 1 minute
)

print(f"Startup events: {len(startups)}")
if not startups.empty:
    print(startups[["start", "end"]].head())
```

!!! info "Startup vs steady state"
    Startup detection identifies *when* the process begins. Combine with steady-state detection (next step) to find *when* the process stabilizes after startup.

---

## Step 6: Steady-State Detection

```python
from ts_shape.events.engineering.steady_state_detection import SteadyStateDetectionEvents

steady = SteadyStateDetectionEvents(
    dataframe=df,
    signal_uuid="temperature_actual",
)

# Find steady-state intervals (low variance periods)
steady_intervals = steady.detect_steady_state(
    window="60s",
    threshold=0.5,          # rolling std below 0.5 = steady
    min_duration="120s",    # must be steady for at least 2 minutes
)
print(f"Steady-state intervals: {len(steady_intervals)}")

# Find transient (dynamic) periods
transients = steady.detect_transient_periods(
    window="60s",
    threshold=0.5,
)
print(f"Transient periods: {len(transients)}")

# Summary statistics
stats = steady.steady_state_statistics(window="60s", threshold=0.5)
print(f"Steady-state time: {stats['steady_pct']:.1f}%")
print(f"Transient time: {stats['transient_pct']:.1f}%")
```

---

## Step 7: Control Loop Health

```python
from ts_shape.events.engineering.control_loop_health import ControlLoopHealthEvents

loop = ControlLoopHealthEvents(
    dataframe=df,
    setpoint_uuid="temperature_setpoint",
    actual_uuid="temperature_actual",
    output_uuid="temperature_output",   # optional: controller output
)

# Error integrals per shift (8-hour windows)
integrals = loop.error_integrals(window="8h")
print("--- Error Integrals per Shift ---")
print(integrals)
# Columns: window_start, IAE, ISE, ITAE, bias

# Detect sustained oscillation in the error signal
oscillation = loop.detect_oscillation(
    window="30min",
    min_cycles=3,
)
print(f"Oscillation events: {len(oscillation)}")

# Check for valve saturation (output pegged at 0% or 100%)
if "temperature_output" in UUID_LIST:
    saturation = loop.output_saturation(
        low_pct=2.0,      # below 2% = saturated low
        high_pct=98.0,     # above 98% = saturated high
        min_duration="60s",
    )
    print(f"Saturation events: {len(saturation)}")

# Shift-level report card
summary = loop.loop_health_summary(window="8h")
print("\n--- Loop Health Summary ---")
print(summary)
```

---

## Step 8: Process Stability Score

```python
from ts_shape.events.engineering.process_stability_index import ProcessStabilityIndex

stability = ProcessStabilityIndex(
    dataframe=df,
    signal_uuid="temperature_actual",
    target=TARGET_VALUE,
    upper_spec=UPPER_SPEC,
    lower_spec=LOWER_SPEC,
)

# Composite 0-100 stability score per shift
scores = stability.stability_score(window="8h")
print("--- Stability Scores ---")
print(scores)

# Is stability improving or degrading?
trend = stability.score_trend(window="8h")
print(f"Trend direction: {trend['direction'].iloc[-1]}")

# Worst periods for investigation
worst = stability.worst_periods(window="8h", n=3)
print("--- Worst 3 Periods ---")
print(worst)
```

---

## Results

| Output | Description | Use case |
|--------|-------------|----------|
| `steps` | Setpoint change events with magnitude | Recipe tracking |
| `settling` | Time-to-settle per setpoint change | Tuning assessment |
| `overshoot` | Overshoot % per change | Control quality |
| `startups` | Equipment startup intervals | Startup optimization |
| `steady_intervals` | Steady-state vs transient periods | Process efficiency |
| `integrals` | IAE/ISE/ITAE per window | Loop performance KPIs |
| `oscillation` | Oscillation detection events | Tuning issues |
| `scores` | 0-100 stability score per shift | Daily process health |

---

## Next Steps

- Correlate setpoint changes with [Quality & SPC](quality-spc.md) to find which changes cause quality issues
- Use stability scores alongside [OEE Dashboard](oee-dashboard.md) for a complete production overview
- Feed startup times into [Cycle Time Analysis](cycle-time-analysis.md) to exclude warm-up from cycle statistics
