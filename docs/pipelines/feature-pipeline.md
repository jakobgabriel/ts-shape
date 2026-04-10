# Feature Pipeline

> From raw timeseries to ML-ready feature tables in a single chain.

**Signals needed:**

| Role | UUID example | Type | Description |
|------|-------------|------|-------------|
| Order signal | `order_number` | `value_string` | Categorical signal that changes when a new order/batch/recipe starts |
| Process param 1 | `temperature` | `value_double` | Numeric measurement (any process variable) |
| Process param 2 | `pressure` | `value_double` | Numeric measurement |
| Process param 3 | `speed` | `value_double` | Numeric measurement |

**Modules used:** [FeaturePipeline](../reference/ts_shape/features/segment_analysis/feature_pipeline.md) | [DateTimeFilter](../reference/ts_shape/transform/filter/datetime_filter.md) | [DoubleFilter](../reference/ts_shape/transform/filter/numeric_filter.md) | [DataHarmonizer](../reference/ts_shape/transform/harmonization.md) | [SegmentExtractor](../reference/ts_shape/features/segment_analysis/segment_extractor.md) | [SegmentProcessor](../reference/ts_shape/features/segment_analysis/segment_processor.md) | [TimeWindowedFeatureTable](../reference/ts_shape/features/segment_analysis/time_windowed_features.md)

---

## Prerequisites

```python
# -- The only things you customize --
PROCESS_UUIDS = ['temperature', 'pressure', 'speed']
ORDER_UUID = 'order_number'

START = '2024-01-01'
END   = '2024-01-31'

FREQ    = '1min'                          # time window for features
METRICS = ['mean', 'std', 'min', 'max']   # statistical metrics per window
```

!!! info "New to FeaturePipeline?"
    Read the [Pipeline Builder guide](../guides/pipeline-builder.md) first — it explains the two class patterns (`add_step` vs `add_instance_step`), sentinels (`$prev`, `$input`), and debugging tools.

---

## Step 1: Build the Pipeline

```python
from ts_shape.features.segment_analysis.feature_pipeline import FeaturePipeline
from ts_shape.transform.filter.numeric_filter import DoubleFilter
from ts_shape.transform.filter.datetime_filter import DateTimeFilter
from ts_shape.transform.harmonization import DataHarmonizer
from ts_shape.features.segment_analysis.segment_extractor import SegmentExtractor
from ts_shape.features.segment_analysis.segment_processor import SegmentProcessor
from ts_shape.features.segment_analysis.time_windowed_features import TimeWindowedFeatureTable

pipe = (
    FeaturePipeline(df)

    # 1. Trim to time window
    .add_step(DateTimeFilter.filter_between_datetimes,
              start_datetime=START, end_datetime=END)

    # 2. Remove rows with NaN in value_double
    .add_step(DoubleFilter.filter_nan_value_double)

    # 3. Keep only process signals (drop the order signal for numeric steps)
    .add_lambda_step(
        lambda df: df[df['uuid'].isin(PROCESS_UUIDS)],
        name='select_process_signals',
    )

    # 4. Resample to uniform 1-second grid
    .add_instance_step(DataHarmonizer, call='resample_to_uniform', freq='1s')

    # 5. Extract time ranges from the order signal (uses original data)
    .add_step(SegmentExtractor.extract_time_ranges,
              dataframe='$input', segment_uuid=ORDER_UUID)

    # 6. Apply ranges to process data
    .add_step(SegmentProcessor.apply_ranges,
              dataframe='$input', time_ranges='$prev',
              target_uuids=PROCESS_UUIDS)

    # 7. Compute feature table
    .add_step(TimeWindowedFeatureTable.compute,
              freq=FREQ, metrics=METRICS)
)
```

---

## Step 2: Preview with `describe()`

Before running, verify the pipeline is wired correctly:

```python
print(pipe.describe())
```

```
FeaturePipeline (4800 rows, 4 cols)
  1. [step    ] DateTimeFilter.filter_between_datetimes  start_datetime='2024-01-01', end_datetime='2024-01-31'
  2. [step    ] DoubleFilter.filter_nan_value_double
  3. [func    ] select_process_signals
  4. [instance] DataHarmonizer.resample_to_uniform  freq='1s'
  5. [step    ] SegmentExtractor.extract_time_ranges  dataframe='$input', segment_uuid='order_number'
  6. [step    ] SegmentProcessor.apply_ranges  dataframe='$input', time_ranges='$prev', target_uuids=['temperature', 'pressure', 'speed']
  7. [step    ] TimeWindowedFeatureTable.compute  freq='1min', metrics=['mean', 'std', 'min', 'max']
```

Check that:

- Step types are correct (`step` for classmethods, `instance` for DataHarmonizer, `func` for lambdas)
- Sentinels (`$input`, `$prev`) appear where expected
- Parameters match your config

---

## Step 3: Run

```python
result = pipe.run()

print(f"Feature table: {result.shape[0]} rows x {result.shape[1]} cols")
print(result.head())
```

```
Feature table: 90 rows x 14 cols

  time_window          segment_value  temperature__mean  temperature__std  pressure__mean  pressure__std  speed__mean  ...
  2024-01-01 00:00:00  Order-A        50.12              1.87              100.34           4.92           1000.1       ...
  2024-01-01 00:01:00  Order-A        50.08              1.91              100.28           5.01           999.8        ...
  2024-01-01 00:02:00  Order-A        49.95              1.85              100.41           4.88           1000.3       ...
```

Each row is one time window.  Columns follow the pattern `{uuid}__{metric}`.

---

## Step 4: Debug with `run_steps()`

If the output looks wrong, inspect every intermediate DataFrame:

```python
intermediates = pipe.run_steps()

for name, step_df in intermediates.items():
    print(f"{name:50s} → {step_df.shape[0]:>6} rows x {step_df.shape[1]} cols")
```

```
input                                              →   4800 rows x 4 cols
DateTimeFilter.filter_between_datetimes            →   4800 rows x 4 cols
DoubleFilter.filter_nan_value_double               →   3600 rows x 4 cols
select_process_signals                             →   3600 rows x 4 cols
DataHarmonizer.resample_to_uniform                 →   3600 rows x 4 cols
SegmentExtractor.extract_time_ranges               →      3 rows x 5 cols
SegmentProcessor.apply_ranges                      →   3600 rows x 6 cols
TimeWindowedFeatureTable.compute                   →     90 rows x 14 cols
```

Drill into any step:

```python
# Check what the segment extractor found
print(intermediates['SegmentExtractor.extract_time_ranges'])
# segment_value | segment_start       | segment_end         | segment_duration | segment_index
# Order-A       | 2024-01-01 00:00:00 | 2024-01-01 01:39:59 | 01:39:59         | 0
# Order-B       | 2024-01-01 01:40:00 | 2024-01-01 03:19:59 | 01:39:59         | 1
# Order-A       | 2024-01-01 03:20:00 | 2024-01-01 04:59:59 | 01:39:59         | 2
```

---

## Step 5: Customize

Swap components to match your use case:

=== "Different metrics"

    ```python
    # Use distribution-aware metrics instead of basic stats
    .add_step(TimeWindowedFeatureTable.compute,
              freq='1min',
              metrics=['mean', 'median', 'skewness', 'kurtosis', 'iqr'])
    ```

=== "Long format output"

    ```python
    # One row per (time_window, uuid) instead of wide columns
    .add_step(TimeWindowedFeatureTable.compute_long,
              freq='1min', metrics=['mean', 'std'])

    # Result columns: time_window | uuid | segment_value | mean | std
    ```

=== "Metric profiles instead of time windows"

    ```python
    # Aggregate per order instead of per time window
    .add_step(SegmentProcessor.compute_metric_profiles,
              group_column='segment_value',
              metrics=['mean', 'std', 'min', 'max'])

    # Result: uuid | segment_value | mean | std | min | max
    ```

=== "Add profile comparison"

    ```python
    from ts_shape.features.segment_analysis.profile_comparison import ProfileComparison

    # After computing metric profiles, compare orders
    .add_step(SegmentProcessor.compute_metric_profiles,
              group_column='segment_value',
              metrics=['mean', 'std', 'min', 'max'])
    .add_step(ProfileComparison.compute_distance_matrix,
              group_column='segment_value')

    # Result: distance matrix between orders
    ```

---

## Results

At the end of this pipeline you have:

| Output | Description | Typical shape |
|--------|-------------|---------------|
| `result` (wide) | Feature table: one row per time window, columns = `{uuid}__{metric}` | 90 rows x 14 cols |
| `result` (long) | Feature table: one row per (time window, uuid), metric columns | 270 rows x 6 cols |
| `intermediates` | Dict of DataFrames for every pipeline step | 8 entries |

The feature table can be:

- Exported to CSV/Parquet for downstream ML pipelines
- Fed into `ProfileComparison` for order-to-order distance analysis
- Joined with outputs from other pipelines (e.g., [Quality & SPC](quality-spc.md)) on `time_window`

---

## Next Steps

- [Pipeline Builder](../guides/pipeline-builder.md) — Understand the three step types, sentinels, and debugging tools
- [Feature Extraction](../guides/feature-extraction.md) — Detailed guide on cycles vs segments (manual approach)
- [Quality & SPC](quality-spc.md) — Apply SPC rules and capability analysis to your feature table
- [Process Engineering](process-engineering.md) — Correlate features with setpoint changes and process stability
