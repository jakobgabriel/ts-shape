"""Timeseries Loaders

Load timeseries data from parquet folders, S3-compatible stores, Azure Blob,
and TimescaleDB.

Classes:
- ParquetLoader: Read parquet files from local folder structures.
  - load_all_files: Load all parquet under a base path.
  - load_by_time_range: Load files within YYYY/MM/DD/HH path range.
  - load_by_uuid_list: Load files matching UUIDs in filenames.
  - load_files_by_time_range_and_uuids: Combine time range and UUID filters.

- S3ProxyDataAccess: Retrieve parquet via an S3-compatible proxy.
  - fetch_data_as_parquet: Save parquet files to a local folder structure.
  - fetch_data_as_dataframe: Return a combined DataFrame.

- AzureBlobParquetLoader: Load parquet from Azure Blob Storage.
  - load_all_files: Load all parquet under an optional prefix.
  - load_by_time_range: Load hourly folders between start and end.
  - load_files_by_time_range_and_uuids: Load per-hour per-UUID parquet files.
  - list_structure: List folders and files under a prefix.

- TimescaleDBDataAccess: Stream timeseries from TimescaleDB.
  - fetch_data_as_parquet: Partition-by-hour and write parquet.
  - fetch_data_as_dataframe: Return a combined DataFrame.
"""
