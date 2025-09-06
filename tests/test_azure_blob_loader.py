import pytest
import pandas as pd  # type: ignore
from types import SimpleNamespace

from ts_shape.loader.timeseries.azure_blob_loader import AzureBlobParquetLoader


def _make_loader_without_init(prefix="", files=None):
    # Bypass __init__ to avoid importing azure-storage-blob
    loader = object.__new__(AzureBlobParquetLoader)
    # Fake container_client with list_blobs
    class DummyClient:
        def __init__(self, names):
            self._names = names or []

        def list_blobs(self, name_starts_with=None):
            # Filter by prefix if provided
            ns = [n for n in self._names if (not name_starts_with) or n.startswith(name_starts_with)]
            # Yield objects with a .name attribute
            return [SimpleNamespace(name=n) for n in ns]

    loader.container_client = DummyClient(files or [])
    loader.prefix = prefix
    loader.max_workers = 2
    return loader


def test_hour_prefix_and_slots():
    loader = _make_loader_without_init(prefix="parquet/")
    ts = pd.Timestamp('2024-01-01 09:05:00')
    pfx = loader._hour_prefix(ts)
    assert pfx.endswith('2024/01/01/09/')
    slots = list(loader._hourly_slots('2024-01-01 08:00:00', '2024-01-01 10:00:00'))
    assert len(slots) == 3


def test_list_structure_and_load_all(monkeypatch):
    files = [
        'parquet/2024/01/01/09/u1.parquet',
        'parquet/2024/01/01/10/u2.parquet',
        'parquet/2024/01/01/10/ignore.txt',
    ]
    loader = _make_loader_without_init(prefix="parquet/", files=files)

    # Patch download to return frames with some rows
    monkeypatch.setattr(loader, "_download_parquet", lambda name: pd.DataFrame({'name': [name]}))

    listed = loader.list_structure()
    assert listed['files'] == [f for f in files if f.endswith('.parquet')]
    assert all(p.endswith('/') for p in listed['folders'])

    all_df = loader.load_all_files()
    assert not all_df.empty
    assert set(all_df['name']) == set([f for f in files if f.endswith('.parquet')])


def test_load_by_time_range_and_uuid(monkeypatch):
    # Construct files and ensure prefixes match hourly
    files = [
        'parquet/2024/01/01/09/u1.parquet',
        'parquet/2024/01/01/10/u1.parquet',
        'parquet/2024/01/01/11/u2.parquet',
    ]
    loader = _make_loader_without_init(prefix="parquet/", files=files)
    monkeypatch.setattr(loader, "_download_parquet", lambda name: pd.DataFrame({'uuid': [name.split('/')[-1].split('.')[0]]}))

    df1 = loader.load_by_time_range('2024-01-01 09:00:00', '2024-01-01 10:30:00')
    assert set(df1['uuid']) == {'u1'}

    df2 = loader.load_files_by_time_range_and_uuids('2024-01-01 09:00:00', '2024-01-01 11:00:00', ['u2'])
    assert set(df2['uuid']) == {'u2'}

