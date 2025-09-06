# Concept

ts-shape is a lightweight, composable toolkit for shaping time series data into analysis-ready DataFrames. It focuses on three pillars: loading, transforming, and extracting higher-level features/events — with a consistent, Pandas-first interface.

## Architecture Overview

```mermaid
graph TD
    A[Loaders<br/>Timeseries + Metadata] --> B[Combine<br/>(Join on uuid)]
    B --> C[Transform
        <br/>Filters · Functions · Time Functions · Calculator]
    C --> D[Features
        <br/>Stats · Time Stats · Cycles]
    D --> E[Events
        <br/>Quality · Maintenance · Production · Engineering]
```

Core ideas:
- DataFrame-in, DataFrame-out: Every stage accepts and returns Pandas DataFrames for easy composition.
- Simple schema: Timeseries frames use a compact set of typed columns; metadata/enrichment joins on a stable `uuid` key.
- Modular blocks: Use only what you need — loaders, transforms, features, and events are decoupled.

## Data Model

Timeseries DataFrame (typical columns):
- uuid: string identifier for a signal/series
- systime: timestamp (tz-aware recommended)
- value_double, value_integer, value_string, value_bool: value channels (one or more may be present)
- is_delta: boolean flag indicating delta semantics (optional)

Metadata DataFrame:
- Indexed by uuid or has a `uuid` column
- Arbitrary columns describing the signal (label, unit, config.*)

Conventions:
- Join key is `uuid` by default.
- Keep values narrow: prefer one type-specific value column where possible.

## Loaders

Timeseries:
- Parquet folder loader: Recursively reads parquet files from local/remote mounts.
- S3 proxy parquet loader: Streams parquet via S3-compatible endpoints.
- Azure Blob parquet loader: Loads parquet files from containers; supports time-based folder structure (parquet/YYYY/MM/DD/HH) and UUID filters.
- TimescaleDB loader: Streams rows by UUID and time range; can emit parquet partitioned by hour.

Metadata:
- JSON metadata loader: Robustly ingests JSON in multiple shapes (list-of-records, dicts of lists/dicts), flattens `config` into columns, and indexes by `uuid`.

All loaders expose either a DataFrame-returning method (e.g., `fetch_data_as_dataframe`, `to_df`) or a parquet materialization method when desired.

## Combination Layer

Use `DataIntegratorHybrid.combine_data(...)` to merge timeseries and metadata sources into one frame:
- Accepts DataFrames or source objects (with `fetch_data_as_dataframe`/`fetch_metadata`).
- Merges on `uuid` (configurable), supporting different join strategies (`left`, `inner`, ...).

Example:
```python
from ts_shape.loader.combine.integrator import DataIntegratorHybrid

combined = DataIntegratorHybrid.combine_data(
    timeseries_sources=[ts_df_or_loader],
    metadata_sources=[meta_df_or_loader],
    uuids=["id-1", "id-2"],
    join_key="uuid",
    merge_how="left",
)
```

## Transform

Reusable blocks to reshape and clean data:
- Filters: datatype-specific predicates (numeric/string/boolean/datetime) to subset rows or fix values.
- Functions: arbitrary lambda-like transformations for columns.
- Time Functions: timestamp operations (timezone shift, conversion, resampling helpers).
- Calculator: numeric calculators to derive engineered columns.

All transformations accept/return DataFrames to compose pipelines like small, testable steps.

## Features

Feature extractors summarize series into compact descriptors:
- Stats: per-type descriptive stats (min/max/mean/std for numeric, frequency for strings, etc.).
- Time Stats: timestamp-specific stats (first/last timestamp, counts per window, coverage).
- Cycles: utilities to identify and process cycles in signals.

`DescriptiveFeatures.compute(...)` can emit a nested dict or a flat DataFrame for easy downstream analysis.

## Events

Event detectors derive categorical flags and ranges from raw signals:
- Quality: outlier detection, SPC rules, tolerance deviations.
- Maintenance: downtime and other operational events.
- Production/Engineering: domain patterns extractable from the shaped series.

Each detector takes a DataFrame and returns either annotated frames or event tables.

## Typical Pipeline

1) Load
- Read timeseries (e.g., parquet or DB) into a DataFrame with `uuid`, `systime`, and values.
- Load metadata JSON and convert to a `uuid`-indexed DataFrame.

2) Combine
- Join timeseries with metadata on `uuid` to enrich context.

3) Transform
- Apply filters/functions/time operations; compute engineered columns.

4) Features & Events
- Compute stats and time stats; identify domain events.

5) Output
- Keep as a DataFrame, write parquet/CSV, or feed to a model/BI tool.

## Design Principles

- Minimal assumptions: Works with partial columns; you choose the value channel(s) in play.
- Composability: Small building blocks; pure DataFrame IO.
- Performance-aware: Vectorized Pandas ops; chunked DB reads; concurrent IO for remote storage.
- Extensible: Add new loaders, transforms, features, or events with simple, documented interfaces.

## Extending ts-shape

- New loader: implement a class with `fetch_data_as_dataframe()` or an explicit `to_parquet()` flow.
- New transform: write a function that takes/returns a DataFrame; place under `transform/*`.
- New feature/event: follow existing patterns; accept a DataFrame and return a summary/event frame.

## When to Use ts-shape

- You need a quick, pythonic path from raw timeseries + context to analysis-ready tables.
- You want modular building blocks instead of a monolithic framework.
- You operate across storage backends (parquet, S3/Azure, SQL) and prefer a unified DataFrame API.
