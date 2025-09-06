# Installation Guide

This guide helps you install ts-shape for common environments, and optionally enable cloud/data-source integrations.

## Requirements

- Python 3.10 or newer
- pip 22+ recommended
- A virtual environment (recommended): `python -m venv .venv && source .venv/bin/activate` (PowerShell: `.venv\Scripts\Activate.ps1`)

## Quick Start (PyPI)

- Install the package:
  - `pip install ts-shape`
- Verify import and version:
  - `python -c "import ts_shape, importlib.metadata as m; print('ts_shape imported, version', m.version('ts-shape'))"`

## Optional Parquet Engines

ts-shape uses pandas to read/write Parquet. Install one engine:

- `pip install pyarrow`  (recommended)
- or `pip install fastparquet`

Without one of these, `pd.read_parquet` will raise an error.

## Optional Integrations

- S3 access (S3 proxy loader):
  - Already included: `s3fs`

- Azure Blob Storage (Azure parquet loader):
  - `pip install azure-storage-blob pyarrow`
  - For AAD auth and management APIs:
    - `pip install azure-identity azure-mgmt-storage`

- TimescaleDB (Timescale loader):
  - `pip install sqlalchemy psycopg2-binary`

## From Source (Editable)

If you’re developing or want the latest:

1) Clone the repo and enter it:
   - `git clone https://github.com/jakobgabriel/ts-shape.git`
   - `cd ts-shape`

2) Create and activate a venv (recommended):
   - `python -m venv .venv`
   - Linux/macOS: `source .venv/bin/activate`
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`

3) Install base deps and package:
   - `pip install -r requirements.txt`
   - `pip install -e .`

4) Add optional integrations as needed (see above).

## Sanity Check

- Minimal check to ensure functionality:
  - `python - << 'PY'
import pandas as pd
from ts_shape.loader.metadata.metadata_json_loader import MetadataJsonLoader
data = {"uuid": {"0": "u1"}, "label": {"0": "sensor-1"}, "config": {"0": {"unit": "C"}}}
df = MetadataJsonLoader(data).to_df()
print(df)
PY`

## Troubleshooting

- Parquet engine missing: Install `pyarrow` (or `fastparquet`).
- ImportError for Azure classes: Install `azure-storage-blob` (and optionally `azure-identity`, `azure-mgmt-storage`).
- Timescale connection errors: Verify `sqlalchemy`/`psycopg2-binary` installed and DSN is correct.
- Version conflicts: `pip install --upgrade pip setuptools wheel` then reinstall.

## Uninstall

- `pip uninstall ts-shape`
