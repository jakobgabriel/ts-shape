# Downtime Pareto Analysis Pipeline

> From Azure Blob timeseries to Pareto-ranked downtime reasons, shift-level comparison, and availability trends.

**Signals needed:**

| Role | UUID example | Type | Description |
|------|-------------|------|-------------|
| Machine state | `machine_state_str` | `value_string` | "Running", "Stopped", "Idle" |
| Downtime reason | `downtime_reason` | `value_string` | Reason code (e.g., "Tool_Change", "Material_Shortage") |

**Modules used:** [AzureBlobParquetLoader](../reference/ts_shape/loader/timeseries/azure_blob_loader/) | [MetadataJsonLoader](../reference/ts_shape/loader/metadata/metadata_json_loader/) | [ContextEnricher](../reference/ts_shape/loader/context/context_enricher/) | [DataHarmonizer](../reference/ts_shape/transform/harmonization/) | [MachineStateEvents](../reference/ts_shape/events/production/machine_state/) | [DowntimeTracking](../reference/ts_shape/events/production/downtime_tracking/)

---

## Prerequisites

```python
AZURE_CONNECTION = "DefaultEndpointsProtocol=https;AccountName=...;AccountKey=..."
CONTAINER = "timeseries-data"

UUID_LIST = [
    "machine_state_str",   # string: Running/Stopped/Idle
    "downtime_reason",     # string: reason code
]

START = "2024-06-01"
END   = "2024-06-08"

METADATA_PATH = "config/signal_metadata.json"

SHIFT_DEFINITIONS = {
    "day":       ("06:00", "14:00"),
    "afternoon": ("14:00", "22:00"),
    "night":     ("22:00", "06:00"),
}
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

print(f"Loaded {len(df):,} rows")
print(f"Unique reason codes: {df[df['uuid'] == 'downtime_reason']['value_string'].nunique()}")
```

---

## Step 2: Enrich with Metadata

```python
from ts_shape.loader.metadata.metadata_json_loader import MetadataJsonLoader
from ts_shape.loader.context.context_enricher import ContextEnricher

meta = MetadataJsonLoader.from_file(METADATA_PATH)
enricher = ContextEnricher(df)
df = enricher.enrich_with_metadata(meta.to_df(), columns=["description", "area"])
```

---

## Step 3: Validate Data Quality

```python
from ts_shape.transform.harmonization import DataHarmonizer

harmonizer = DataHarmonizer(df, value_column="value_double")
gaps = harmonizer.detect_gaps(threshold="60s")

if not gaps.empty:
    print("Signal gaps detected:")
    print(gaps.groupby("uuid")["gap_duration"].agg(["count", "max"]))
```

!!! tip "State signal continuity"
    The machine state signal should be continuous (no gaps). Gaps are ambiguous — was the machine running or stopped? Fill with `ffill` for short gaps, flag long gaps as "Unknown".

```python
# Forward-fill small gaps in state signal
df_clean = harmonizer.fill_gaps(strategy="ffill", max_gap="120s")
```

---

## Step 4: Downtime by Shift

```python
from ts_shape.events.production.downtime_tracking import DowntimeTracking

tracker = DowntimeTracking(df, shift_definitions=SHIFT_DEFINITIONS)

# Downtime duration per shift
shift_downtime = tracker.downtime_by_shift(
    state_uuid="machine_state_str",
    running_value="Running",
)

print("--- Downtime by Shift ---")
print(shift_downtime)
# Columns: date, shift, total_time_minutes, downtime_minutes, availability_pct
```

---

## Step 5: Downtime by Reason (Pareto)

```python
# Break down by reason code
reason_analysis = tracker.downtime_by_reason(
    state_uuid="machine_state_str",
    reason_uuid="downtime_reason",
    stopped_value="Stopped",
)

print("--- Downtime by Reason ---")
print(reason_analysis)
```

```python
# Top reasons (Pareto ranking)
top_reasons = tracker.top_downtime_reasons(
    state_uuid="machine_state_str",
    reason_uuid="downtime_reason",
    top_n=5,
    stopped_value="Stopped",
)

print("--- Top 5 Downtime Reasons (Pareto) ---")
print(top_reasons)
# Columns: reason, total_minutes, occurrence_count, pct_of_total, cumulative_pct
```

!!! info "The 80/20 rule"
    In most plants, 2-3 reason codes account for 80% of downtime. Focus improvement efforts on these first.

---

## Step 6: Availability Trend

```python
# Daily availability trend
availability = tracker.availability_trend(
    state_uuid="machine_state_str",
    running_value="Running",
    window="1D",
)

print("--- Daily Availability Trend ---")
print(availability)
# Columns: period, running_minutes, total_minutes, availability_pct
```

---

## Results

| Output | Description | Merge key |
|--------|-------------|-----------|
| `shift_downtime` | Downtime minutes and availability per shift | `date`, `shift` |
| `reason_analysis` | Downtime broken down by reason code | `reason` |
| `top_reasons` | Pareto-ranked reasons with cumulative % | `reason` |
| `availability` | Daily availability trend | `period` |

!!! tip "Merge with production data"
    Join `shift_downtime` with [OEE Dashboard](oee-dashboard.md) `shift_prod` on `[date, shift]` for a complete shift handover report:
    ```python
    report = shift_prod.merge(shift_downtime, on=["date", "shift"])
    ```

---

## Next Steps

- Merge shift downtime with [OEE Dashboard](oee-dashboard.md) results for full shift reports
- Correlate top reasons with [Cycle Time Analysis](cycle-time-analysis.md) slow cycles
- Add [Quality & SPC](quality-spc.md) to check if downtime reasons correlate with quality issues
