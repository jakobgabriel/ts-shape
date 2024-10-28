from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from typing import List, Dict

class TimescaleDBDataAccess:
    """
    A class to access timeseries data from a TimescaleDB database. This class 
    retrieves data for specified UUIDs within a defined time range, with the 
    option to output data as Parquet files or as a single combined DataFrame.
    """

    def __init__(self, start_timestamp: str, end_timestamp: str, uuids: List[str], db_config: Dict[str, str]):
        """
        Initialize the TimescaleDBDataAccess object.
        :param start_timestamp: Start timestamp in "Year-Month-Day Hour:Minute:Second" format.
        :param end_timestamp: End timestamp in "Year-Month-Day Hour:Minute:Second" format.
        :param uuids: List of UUIDs to retrieve data for.
        :param db_config: Configuration dictionary for database connection.
        """
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.uuids = uuids
        self.db_config = db_config

        # Establish database connection engine using SQLAlchemy
        self.engine = create_engine(
            f'postgresql+psycopg2://{db_config["db_user"]}:{db_config["db_pass"]}@{db_config["db_host"]}/{db_config["db_name"]}'
        )

    def _fetch_data(self, uuid: str) -> pd.DataFrame:
        """
        Executes an SQL query to fetch timeseries data for a specific UUID from TimescaleDB.
        :param uuid: The UUID for which data is being retrieved.
        :return: A DataFrame with timeseries data for the UUID.
        """
        query = f"""
            SELECT uuid::text, systime, value_integer, value_string, value_double, value_bool, is_delta 
            FROM telemetry 
            WHERE uuid = '{uuid}' 
              AND systime BETWEEN '{self.start_timestamp}' AND '{self.end_timestamp}' 
            ORDER BY systime ASC
        """
        return pd.read_sql(query, self.engine, chunksize=10000)

    def fetch_data_as_parquet(self, output_dir: str):
        """
        Retrieves timeseries data from TimescaleDB and saves it as Parquet files.
        Each file is saved in a directory structure of UUID/year/month/day/hour.
        :param output_dir: Base directory to save the Parquet files.
        """
        for uuid in self.uuids:
            for chunk in self._fetch_data(uuid):
                if not chunk.empty:
                    for _, row in chunk.iterrows():
                        systime = row['systime']
                        timeslot_dir = Path(str(systime.year), str(systime.month).zfill(2), str(systime.day).zfill(2), str(systime.hour).zfill(2))
                        output_path = Path(output_dir, f"{uuid}/{timeslot_dir}")
                        output_path.mkdir(parents=True, exist_ok=True)
                        row.to_frame().T.to_parquet(output_path / f"{uuid}.parquet", index=False)

    def fetch_data_as_dataframe(self) -> pd.DataFrame:
        """
        Retrieves timeseries data from TimescaleDB and returns it as a single DataFrame.
        :return: A combined DataFrame with data for all specified UUIDs within the time range.
        """
        df_list = [chunk for uuid in self.uuids for chunk in self._fetch_data(uuid)]
        return pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()