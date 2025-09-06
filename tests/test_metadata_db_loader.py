import pytest
import pandas as pd  # type: ignore

psycopg2 = pytest.importorskip("psycopg2")

from ts_shape.loader.metadata.metadata_db_loader import DatapointDB


class DummyCursor:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, query, params):
        self._last = (query, params)

    def fetchall(self):
        return self._rows


class DummyConn:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self):
        return DummyCursor(self._rows)

    def close(self):
        pass


def test_metadata_db_loader_monkeypatched(monkeypatch, tmp_path):
    rows = [
        ("u1", "L1", {"x": 1}),
        ("u2", "L2", {"x": 2}),
    ]

    monkeypatch.setattr(psycopg2, "connect", lambda **kwargs: DummyConn(rows))

    db = DatapointDB(
        device_names=["Device A"],
        db_user="u", db_pass="p", db_host="h",
        output_path=str(tmp_path),
        required_uuid_list=["u1"],
        filter_enabled=True,
    )

    uuids = db.get_all_uuids()
    # Device key present and filtered
    assert list(uuids.keys()) == ["Device A"]
    assert uuids["Device A"] == ["u1"]

