import pytest
import pandas as pd  # type: ignore

requests = pytest.importorskip("requests")

from ts_shape.loader.metadata.metadata_api_loader import DatapointAPI


class DummyResp:
    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


def test_metadata_api_loader_monkeypatched(monkeypatch, tmp_path):
    # Build fake endpoints
    datatrons = [{"id": 1}]
    devices = [{"id": 10, "name": "Device A"}]
    datapoints = [
        {"uuid": "u1", "label": "A1", "config": {"x": 1}, "enabled": True},
        {"uuid": "u2", "label": "A2", "config": {"x": 2}, "enabled": False},
    ]

    def fake_get(url, headers=None):
        if url.endswith("/devices"):
            return DummyResp(devices)
        if url.endswith("/data_points"):
            return DummyResp(datapoints)
        # base_url
        return DummyResp(datatrons)

    monkeypatch.setattr(requests, "get", fake_get)

    api = DatapointAPI(
        device_names=["Device A"],
        base_url="http://api",
        api_token="t",
        output_path=str(tmp_path),
        required_uuid_list=["u1"],
        filter_enabled=True,
    )

    uuids = api.get_all_uuids()
    assert set(uuids.keys()) == {"Device A"}
    assert uuids["Device A"] == ["u1"]

