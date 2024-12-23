import pandas as pd
import os
from pathlib import Path

class ParquetLoader:
    """
    This class loads multiple parquet files from a specified directory structure (YYYY/MM/DD/HH)
    and can also filter files by a list of UUIDs.

    Args:
        base_path (str or Path): The base directory where the parquet files are stored.
    """

    def __init__(self, base_path: str) -> None:
        """
        Initialize the ParquetLoader with the base directory path.
        """
        self.base_path = Path(base_path)

    def _get_parquet_files(self) -> list:
        """
        Recursively finds all parquet files in the directory structure.
        
        Returns:
            list: A list of paths to all found parquet files.
        """
        return list(self.base_path.rglob("*.parquet"))

    def load_all_files(self) -> pd.DataFrame:
        """
        Loads all parquet files into a single pandas DataFrame.
        
        Returns:
            pd.DataFrame: A DataFrame containing all the data from the parquet files.
        """
        parquet_files = self._get_parquet_files()
        dataframes = [pd.read_parquet(file) for file in parquet_files]
        
        return pd.concat(dataframes, ignore_index=True)

    def load_by_time_range(self, start_time: pd.Timestamp, end_time: pd.Timestamp) -> pd.DataFrame:
        """
        Loads parquet files based on a specific time range, defined by the folder structure (YYYY/MM/DD/HH).
        
        Args:
            start_time (pd.Timestamp): The start timestamp.
            end_time (pd.Timestamp): The end timestamp.
        
        Returns:
            pd.DataFrame: A DataFrame containing the data from the parquet files within the time range.
        """
        # Ensure that start_time and end_time are pd.Timestamp
        if not isinstance(start_time, pd.Timestamp) or not isinstance(end_time, pd.Timestamp):
            raise ValueError("start_time and end_time must be pandas Timestamps")

        parquet_files = self._get_parquet_files()
        valid_files = []

        for file in parquet_files:
            # Extract the timestamp from the folder structure of the file path
            try:
                folder_parts = file.relative_to(self.base_path).parts[:4]  # Extract YYYY/MM/DD/HH parts
                folder_time_str = "/".join(folder_parts)
                file_time = pd.to_datetime(folder_time_str, format="%Y/%m/%d/%H")
                
                # Check if file_time is within the start_time and end_time
                if start_time <= file_time <= end_time:
                    valid_files.append(file)
            except ValueError:
                continue  # Skip files that don't match the expected folder structure

        # Load and concatenate DataFrames
        dataframes = [pd.read_parquet(file) for file in valid_files]
        return pd.concat(dataframes, ignore_index=True)

    def load_by_uuid_list(self, uuid_list: list) -> pd.DataFrame:
        """
        Loads parquet files based on a list of UUIDs. The UUIDs are expected to be part of the file names.
        
        Args:
            uuid_list (list): A list of UUIDs that should be loaded.
        
        Returns:
            pd.DataFrame: A DataFrame containing the data from the parquet files with matching UUIDs.
        """
        parquet_files = self._get_parquet_files()
        valid_files = []

        for file in parquet_files:
            file_name = file.stem  # Extract the file name without extension
            # Check if the file name contains any of the UUIDs in the list
            for uuid in uuid_list:
                if uuid in file_name:
                    valid_files.append(file)
                    break  # Stop checking other UUIDs for this file

        # Load and concatenate DataFrames
        dataframes = [pd.read_parquet(file) for file in valid_files]
        return pd.concat(dataframes, ignore_index=True)

    def load_files_by_time_range_and_uuids(self, start_time: pd.Timestamp, end_time: pd.Timestamp, uuid_list: list) -> pd.DataFrame:
        """
        Loads parquet files that fall within a time range and match UUIDs from the list.
        
        Args:
            start_time (pd.Timestamp): The start timestamp.
            end_time (pd.Timestamp): The end timestamp.
            uuid_list (list): A list of UUIDs that should be loaded.
        
        Returns:
            pd.DataFrame: A DataFrame containing the data from the parquet files that meet both criteria.
        """
        parquet_files = self._get_parquet_files()
        valid_files = []

        for file in parquet_files:
            try:
                # Extract the timestamp from the folder structure
                folder_parts = file.relative_to(self.base_path).parts[:4]  # Extract YYYY/MM/DD/HH parts
                folder_time_str = "/".join(folder_parts)
                file_time = pd.to_datetime(folder_time_str, format="%Y/%m/%d/%H")

                # Check if the file matches both the time range and UUIDs
                if start_time <= file_time <= end_time:
                    file_name = file.stem  # Extract the file name without extension
                    for uuid in uuid_list:
                        if uuid in file_name:
                            valid_files.append(file)
                            break  # Stop checking other UUIDs for this file
            except ValueError:
                continue  # Skip files that don't match the expected structure

        # Load and concatenate DataFrames
        dataframes = [pd.read_parquet(file) for file in valid_files]
        return pd.concat(dataframes, ignore_index=True)
