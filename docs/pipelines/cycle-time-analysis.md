# Cycle Time Analysis Pipeline

> From Azure Blob timeseries to cycle time statistics, slow cycle detection, trend analysis, and golden cycle comparison.

**Signals needed:**

| Role | UUID example | Type | Description |
|------|-------------|------|-------------|
| Cycle trigger | `cycle_complete` | `value_bool` | Rising edge (False to True) marks cycle end |
| Part number | `part_number_signal` | `value_string` | Current part type being produced |
| Machine state | `machine_run_state` | `value_bool` | True = running (optional, for filtering) |

**Modules used:** [AzureBlobParquetLoader](../reference/ts_shape/loader/timeseries/azure_blob_loader/) | [MetadataJsonLoader](../reference/ts_shape/loader/metadata/metadata_json_loader/) | [ContextEnricher](../reference/ts_shape/loader/context/context_enricher/) | [DataHarmonizer](../reference/ts_shape/transform/harmonization/) | [CycleExtractor](../reference/ts_shape/features/cycles/cycles_extractor/) | [CycleTimeTracking](../reference/ts_shape/events/production/cycle_time_tracking/) | [CycleDataProcessor](../reference/ts_shape/features/cycles/cycle_processor/)

---

## Prerequisites

```python
AZURE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."
CONTAINER = "timeseries-data"

UUID_LIST = [
    "cycle_complete",       # bool: rising edge = cycle end
    "part_number_signal",   # string: current part type
    "machine_run_state",    # bool: machine running (optional)
]

START = "2024-06-01"
END   = "2024-06-08"

METADATA_PATH = "config/signal_metadata.json"
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
df = enricher.enrich_with_metadata(meta.to_df(), columns=["description", "unit"])
```

---

## Step 3: Validate Data Quality

```python
from ts_shape.transform.harmonization import DataHarmonizer

harmonizer = DataHarmonizer(df, value_column="value_double")
gaps = harmonizer.detect_gaps(threshold="30s")

if not gaps.empty:
    print("Gaps per signal:")
    print(gaps.groupby("uuid")["gap_duration"].agg(["count", "max"]))

    # Fill small gaps to avoid false cycle breaks
    df_clean = harmonizer.fill_gaps(strategy="ffill", max_gap="60s")
else:
    df_clean = df
```

!!! warning "Cycle trigger gaps"
    Missing samples in the cycle trigger signal create phantom long cycles. Always check for gaps before extracting cycles.

---

## Step 4: Extract Cycles

Use `CycleExtractor` for fine-grained cycle detection, or `CycleTimeTracking` for quick part-based analysis. Here we show both approaches.

### Option A: Quick Analysis with CycleTimeTracking

```python
from ts_shape.events.production.cycle_time_tracking import CycleTimeTracking

tracker = CycleTimeTracking(df)

# Cycle times per part number
cycles = tracker.cycle_time_by_part(
    part_id_uuid="part_number_signal",
    cycle_trigger_uuid="cycle_complete",
)

print(f"Total cycles: {len(cycles)}")
print(cycles[["systime", "part_number", "cycle_time_seconds"]].head(10))
```

### Option B: Advanced Extraction with CycleExtractor

```python
from ts_shape.features.cycles.cycles_extractor import CycleExtractor

# Filter to cycle trigger signal
trigger_df = df[df["uuid"] == "cycle_complete"].copy()

extractor = CycleExtractor(
    dataframe=trigger_df,
    start_uuid="cycle_complete",
)

# Extract using trigger method (True -> False = one cycle)
cycle_df = extractor.process_trigger_cycle()

# Validate: remove unrealistic cycles
cycle_df = extractor.validate_cycles(
    cycle_df,
    min_duration="10s",    # no cycle shorter than 10s
    max_duration="10min",  # no cycle longer than 10 minutes
)

print(f"Valid cycles: {len(cycle_df)}")
print(extractor.get_extraction_stats())
```

---

## Step 5: Cycle Time Statistics

```python
# Statistics per part number
stats = tracker.cycle_time_statistics(
    part_id_uuid="part_number_signal",
    cycle_trigger_uuid="cycle_complete",
)
print(stats)
# Columns: part_number, count, mean, median, std, min, max
```

---

## Step 6: Detect Slow Cycles

```python
slow = tracker.detect_slow_cycles(
    part_id_uuid="part_number_signal",
    cycle_trigger_uuid="cycle_complete",
    threshold_factor=1.5,   # flag cycles > 1.5x median
)

print(f"Slow cycles: {len(slow)}")
if not slow.empty:
    print(slow[["systime", "part_number", "cycle_time_seconds", "deviation_factor"]].head())
```

---

## Step 7: Trend Analysis

```python
# Cycle time trend for a specific part
trend = tracker.cycle_time_trend(
    part_id_uuid="part_number_signal",
    cycle_trigger_uuid="cycle_complete",
    part_number="PART_A",
    window_size=20,    # rolling window of 20 cycles
)

print(trend[["systime", "cycle_time_seconds", "moving_avg", "trend"]].tail(10))
```

---

## Step 8: Golden Cycle Comparison (Advanced)

```python
from ts_shape.features.cycles.cycle_processor import CycleDataProcessor

processor = CycleDataProcessor(
    cycles_df=cycle_df,
    values_df=df,
)

# Find the most consistent cycles
golden = processor.identify_golden_cycles(
    metric="value_double",
    method="low_variability",
    top_n=5,
)
print(f"Golden cycle UUIDs: {golden}")

# Compare all cycles against a reference
comparison = processor.compare_cycles(
    reference_cycle_uuid=golden[0],
    metric="value_double",
)
print(comparison.head())
```

---

## Results

| Output | Description | Use case |
|--------|-------------|----------|
| `cycles` | Per-cycle times with part numbers | Raw cycle data |
| `stats` | Mean, median, std per part type | Capacity planning |
| `slow` | Cycles exceeding threshold | Loss investigation |
| `trend` | Rolling average + direction | Drift detection |
| `golden` | Best reference cycles | Quality benchmarking |

---

## Next Steps

- Feed slow cycle timestamps into [Downtime Pareto](downtime-pareto.md) to correlate with machine stops
- Use cycle statistics to set the `ideal_cycle_time` parameter in [OEE Dashboard](oee-dashboard.md)
- Combine with [Quality & SPC](quality-spc.md) to correlate cycle time outliers with quality defects
