# ts-shape | Timeseries Shaper

[![pypi version](https://img.shields.io/pypi/v/ts-shape.svg)](https://pypi.org/project/ts-shape/)
[![downloads](https://static.pepy.tech/badge/ts-shape/week)](https://pepy.tech/projects/ts-shape)
[![docs](https://img.shields.io/badge/docs-mkdocs-708FCC.svg?style=flat)](https://jakobgabriel.github.io/ts-shape/)

ts-shape is a lightweight, composable toolkit to load, shape, and analyze time series data. It embraces a simple DataFrame-in → DataFrame-out philosophy across loaders, transforms, feature extractors, and event detectors.

Key ideas:

- Unified DataFrame workflow: Load timeseries + metadata, join on `uuid`, and process.
- Modular building blocks: Use only what you need; components are decoupled and easy to extend.
- Performance aware: Vectorized ops, chunked DB reads, and concurrent I/O for remote storage.

## Install

```bash
pip install ts-shape
# Parquet engine (recommended)
pip install pyarrow  # or: pip install fastparquet
```

Optional integrations:

- Azure Blob Storage: `pip install azure-storage-blob`
- Azure AAD + management (optional): `pip install azure-identity azure-mgmt-storage`
- S3 proxy access: already included via `s3fs`
- TimescaleDB: `pip install sqlalchemy psycopg2-binary`

## What’s Inside

- Loaders (timeseries):
  - Parquet folders (local)
  - S3 proxy parquet via `s3fs`
  - Azure Blob parquet (hourly layout, UUID filters, time range)
  - TimescaleDB (chunked reads, parquet export by hour)
- Loaders (metadata):
  - JSON metadata loader (robust input shapes, flattens config)
- Transformations:
  - Filters (numeric/string/boolean/datetime), generic functions, time functions, calculators
- Features:
  - Descriptive stats, time stats, cycles utilities
- Events:
  - Quality (outlier detection, SPC, tolerance deviation), production/maintenance patterns

See the extended concept overview in `docs/concept.md`.

## License

MIT — see `LICENSE.txt`.
