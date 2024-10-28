import requests
import pandas as pd
import json
from typing import List, Dict


class DatapointAPI:
    """
    Class for accessing datapoints via an API.
    """

    def __init__(self, device_name: str, base_url: str, api_token: str, output_path: str = "data_points.json"):
        self.device_name = device_name
        self.base_url = base_url
        self.api_token = api_token
        self.output_path = output_path
        self.uuids: List[str] = []
        self.metadata: pd.DataFrame = pd.DataFrame([])
        self._api_access()

    def _api_access(self) -> None:
        """Connect to the API and retrieve metadata for the specified device."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

        metadata = []
        devices_found = []

        for datatron in requests.get(f"{self.base_url}", headers=headers).json():
            for device in requests.get(f"{self.base_url}/{datatron['id']}/devices", headers=headers).json():
                if device["name"] == self.device_name:
                    datapoints = requests.get(
                        f"{self.base_url}/{datatron['id']}/devices/{device['id']}/data_points",
                        headers=headers,
                    ).json()
                    metadata += datapoints
                    devices_found.append(device["name"])
                if devices_found:
                    break
            if devices_found:
                break

        self.metadata = pd.DataFrame(metadata)
        if not self.metadata.empty:
            self.metadata = self.metadata[self.metadata["enabled"] == True][["uuid", "label", "config"]]
            data_points = self.metadata.to_dict(orient="records")
            self._export_json(data_points)
            self.uuids = [data["uuid"] for data in data_points]

    def _export_json(self, data_points: List[Dict[str, str]]) -> None:
        """Export data points to a JSON file."""
        with open(self.output_path, 'w') as f:
            json.dump(data_points, f, indent=2)

    def get_uuids(self) -> List[str]:
        """Return the list of UUIDs."""
        return self.uuids

    def get_full_config(self) -> List[Dict[str, str]]:
        """Return the full configuration (uuid, label, config) as a list of dictionaries."""
        return self.metadata.to_dict(orient="records")

    def get_uuid_label_pairs(self) -> List[Dict[str, str]]:
        """Return a list of uuid and label pairs."""
        return self.metadata[['uuid', 'label']].to_dict(orient='records')

    def display_dataframe(self) -> None:
        """Print the metadata DataFrame to visually inspect data points."""
        print(self.metadata)