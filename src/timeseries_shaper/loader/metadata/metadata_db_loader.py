import pandas as pd
import psycopg2
import json
from typing import List, Dict


class DatapointDB:
    """
    Class for accessing datapoints via a database.
    """

    def __init__(self, device_name: str, db_user: str, db_pass: str, db_host: str, output_path: str = "data_points.json"):
        self.device_name = device_name
        self.db_user = db_user
        self.db_pass = db_pass
        self.db_host = db_host
        self.output_path = output_path
        self.uuids: List[str] = []
        self.metadata: pd.DataFrame = pd.DataFrame([])
        self._db_access()

    def _db_access(self) -> None:
        """Connect to the database and retrieve metadata for the specified device."""
        conn = psycopg2.connect(
            dbname="config_repository",
            user=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=5432
        )
        cursor = conn.cursor()

        cursor.execute(f"""
            SELECT dp.uuid, dp.label, dp.config
            FROM data_points dp
            INNER JOIN devices dev ON dev.id = dp.device_id
            WHERE dp.enabled = true AND dp.archived = false AND dev.name = %s
        """, (self.device_name,))

        data_points = [{"uuid": r[0], "label": r[1], "config": r[2]} for r in cursor.fetchall()]
        conn.close()

        self.metadata = pd.DataFrame(data_points)
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