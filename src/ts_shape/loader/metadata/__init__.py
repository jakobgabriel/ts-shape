"""Metadata Loaders

Load and normalize datapoint metadata from JSON, REST APIs, or databases.

Classes:
- MetadataJsonLoader: Normalize metadata JSONs into a UUID-indexed DataFrame.
  - from_file: Create from a JSON file.
  - from_str: Create from a JSON string.
  - to_df: Return DataFrame view.
  - head: Preview top rows.
  - get_by_uuid: Access row by UUID.
  - get_by_label: Access row by label.
  - join_with: Join with other DataFrames.
  - filter_by_uuid: Filter by UUID set.
  - filter_by_label: Filter by label set.
  - list_uuids: List UUIDs.
  - list_labels: List non-null labels.

- DatapointAPI: Retrieve datapoint metadata from a REST API.
  - get_all_uuids: UUIDs per device.
  - get_all_metadata: Metadata per device.
  - display_dataframe: Print DataFrames for devices.

- DatapointDB: Retrieve datapoint metadata from PostgreSQL.
  - get_all_uuids: UUIDs per device.
  - get_all_metadata: Metadata per device.
  - display_dataframe: Print DataFrames for devices.
"""
