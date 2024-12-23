import requests
import pandas as pd
import json
from typing import List, Dict


class DatapointAPI:
    """
    Class for accessing datapoints for multiple devices via an API.
    """

    def __init__(self, device_names: List[str], base_url: str, api_token: str, output_path: str = "data", required_uuid_list: List[str] = None, filter_enabled: bool = True):
        """
        Initialize the DatapointAPI class.

        :param device_names: List of device names to retrieve metadata for.
        :param base_url: Base URL of the API.
        :param api_token: API token for authentication.
        :param output_path: Directory to save the data points JSON files.
        :param required_uuid_list: Mixed list of UUIDs to filter the metadata across devices (optional).
        :param filter_enabled: Whether to filter metadata by "enabled == True" (default is True).
        """
        self.device_names = device_names
        self.base_url = base_url
        self.api_token = api_token
        self.output_path = output_path
        self.required_uuid_list = required_uuid_list or []  # Defaults to an empty list if None
        self.filter_enabled = filter_enabled
        self.device_metadata: Dict[str, pd.DataFrame] = {}  # Store metadata for each device
        self.device_uuids: Dict[str, List[str]] = {}  # Store UUIDs for each device
        self._api_access()

    def _api_access(self) -> None:
        """Connect to the API and retrieve metadata for the specified devices."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}",
        }

        for device_name in self.device_names:
            metadata = []
            devices_found = []

            for datatron in requests.get(f"{self.base_url}", headers=headers).json():
                for device in requests.get(f"{self.base_url}/{datatron['id']}/devices", headers=headers).json():
                    if device["name"] == device_name:
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

            # Process metadata for the current device
            metadata_df = pd.DataFrame(metadata)
            if not metadata_df.empty:
                if self.filter_enabled:
                    metadata_df = metadata_df[metadata_df["enabled"] == True]

                metadata_df = metadata_df[["uuid", "label", "config"]]

                # Filter metadata by required UUIDs, if any
                if self.required_uuid_list:
                    metadata_df = metadata_df[metadata_df["uuid"].isin(self.required_uuid_list)]

                # Store processed metadata and UUIDs
                self.device_metadata[device_name] = metadata_df
                self.device_uuids[device_name] = metadata_df["uuid"].tolist()

                # Export JSON file for this device
                self._export_json(metadata_df.to_dict(orient="records"), device_name)

    def _export_json(self, data_points: List[Dict[str, str]], device_name: str) -> None:
        """Export data points to a JSON file for the specified device."""
        file_name = f"{self.output_path}/{device_name.replace(' ', '_')}_data_points.json"
        with open(file_name, 'w') as f:
            json.dump(data_points, f, indent=2)

    def get_all_uuids(self) -> Dict[str, List[str]]:
        """Return a dictionary of UUIDs for each device."""
        return self.device_uuids

    def get_all_metadata(self) -> Dict[str, List[Dict[str, str]]]:
        """Return a dictionary of metadata for each device."""
        return {device: metadata.to_dict(orient="records") for device, metadata in self.device_metadata.items()}

    def display_dataframe(self, device_name: str = None) -> None:
        """
        Print the metadata DataFrame for a specific device or all devices.

        :param device_name: Name of the device to display metadata for (optional).
                            If None, displays metadata for all devices.
        """
        if device_name:
            # Display metadata for a specific device
            if device_name in self.device_metadata:
                print(f"Metadata for device: {device_name}")
                print(self.device_metadata[device_name])
            else:
                print(f"No metadata found for device: {device_name}")
        else:
            # Display metadata for all devices
            for device, metadata in self.device_metadata.items():
                print(f"\nMetadata for device: {device}")
                print(metadata)