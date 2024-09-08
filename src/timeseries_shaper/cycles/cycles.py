import pandas as pd
from ..base import Base

class CycleCutter(Base):
    """
    Processes a DataFrame to extract cycles of values (such as temperature, pressure)
    based on UUID identifiers for start, stop, and optional marker points. Provides
    raw cycle data and cycle-level statistics where values are identified by UUIDs
    and stored in a single value column (e.g., 'value_integer').

    Inherits from:
        Base (class): Base class with common initializations for DataFrame handling.

    Attributes:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        time_column (str): The column with timestamp data; defaults to 'systime'.
        uuid_column (str): The column containing unique UUID values for sensors.
        value_column (str): The column containing the sensor values (e.g., 'value_integer').
    """
    
    def __init__(self, dataframe: pd.DataFrame, time_column: str = 'systime', 
                 uuid_column: str = 'uuid', value_column: str = 'value_integer') -> None:
        """Initializes the CycleCutter with a DataFrame and relevant column names."""
        super().__init__(dataframe)
        self.time_column = time_column
        self.uuid_column = uuid_column
        self.value_column = value_column

    def get_raw_cycle_data(self, start_uuids: list, stop_uuids: list, 
                           value_mappings: dict, marker_uuids: list = None) -> pd.DataFrame:
        """
        Extracts raw cycles from the DataFrame based on the start and stop UUIDs,
        normalizes time by seconds after the cycle start, and returns a DataFrame
        where values (e.g., temperature, pressure) are identified by UUIDs and stored 
        in a single value column (e.g., 'value_integer').

        Args:
            start_uuids (list): List of UUIDs indicating where each cycle starts.
            stop_uuids (list): List of UUIDs indicating where each cycle ends.
            value_mappings (dict): A dictionary where keys are value types (e.g., 'temperature', 'pressure')
                                   and values are the UUIDs corresponding to those sensors.
            marker_uuids (list, optional): List of marker UUIDs to be added. Defaults to None.
        
        Returns:
            pd.DataFrame: A DataFrame where each entry contains the raw data of each cycle.
        """
        if len(start_uuids) != len(stop_uuids):
            raise ValueError("The number of start UUIDs must match the number of stop UUIDs.")

        cycles = []

        # Iterate over the list of start and stop UUIDs
        for idx, (start_uuid, stop_uuid) in enumerate(zip(start_uuids, stop_uuids)):
            # Find the systime for start and stop UUIDs
            cycle_data = self._get_cycle_data(start_uuid, stop_uuid, value_mappings, marker_uuids, idx)
            if cycle_data is not None:
                cycles.append(cycle_data)

        # Return DataFrame of DataFrames for easy visualization and manipulation
        return pd.DataFrame({'cycle': cycles})

    def get_cycle_statistics(self, start_uuids: list, stop_uuids: list, value_mappings: dict) -> pd.DataFrame:
        """
        Extracts and computes cycle-level statistics (duration, mean, max, min, std dev)
        for each cycle based on the start and stop UUIDs.

        Args:
            start_uuids (list): List of UUIDs indicating where each cycle starts.
            stop_uuids (list): List of UUIDs indicating where each cycle ends.
            value_mappings (dict): A dictionary where keys are value types (e.g., 'temperature', 'pressure')
                                   and values are the UUIDs corresponding to those sensors.

        Returns:
            pd.DataFrame: A DataFrame containing the cycle-level statistics.
        """
        if len(start_uuids) != len(stop_uuids):
            raise ValueError("The number of start UUIDs must match the number of stop UUIDs.")

        cycle_stats = []

        # Iterate over the list of start and stop UUIDs
        for idx, (start_uuid, stop_uuid) in enumerate(zip(start_uuids, stop_uuids)):
            # Find the systime for start and stop UUIDs
            cycle_data = self._get_cycle_data(start_uuid, stop_uuid, value_mappings, None, idx)
            if cycle_data is not None:
                cycle_stats.append(self._calculate_cycle_statistics(cycle_data, value_mappings, idx))

        # Convert the list of statistics dictionaries into a DataFrame
        return pd.DataFrame(cycle_stats)

    def _get_cycle_data(self, start_uuid, stop_uuid, value_mappings, marker_uuids, cycle_id) -> pd.DataFrame:
        """
        Extracts the data for a single cycle based on the start and stop UUIDs, 
        normalizes the time column, and returns the cycle DataFrame. If marker 
        UUIDs are provided, they are added as a separate column with normalized times.

        Args:
            start_uuid (str): The UUID marking the start of the cycle.
            stop_uuid (str): The UUID marking the end of the cycle.
            value_mappings (dict): A dictionary of value types and their corresponding sensor UUIDs.
            marker_uuids (list): List of marker UUIDs to add to the cycle.
            cycle_id (int): The unique identifier for the cycle.
        
        Returns:
            pd.DataFrame: A DataFrame for the cycle with normalized time and markers, or None if UUIDs are not found.
        """
        # Find rows corresponding to the start and stop UUIDs
        start_row = self.dataframe[self.dataframe[self.uuid_column] == start_uuid]
        stop_row = self.dataframe[self.dataframe[self.uuid_column] == stop_uuid]

        if start_row.empty or stop_row.empty:
            print(f"Start or stop UUID not found for {start_uuid} - {stop_uuid}")
            return None

        # Get the systime for the start and stop points
        cycle_start_time = start_row[self.time_column].iloc[0]
        cycle_stop_time = stop_row[self.time_column].iloc[0]

        # Initialize an empty DataFrame to store the merged cycle data
        cycle_df = pd.DataFrame()

        # Extract data for each sensor (e.g., temperature, pressure) based on UUID mappings
        for value_type, sensor_uuid in value_mappings.items():
            value_data = self.dataframe[(self.dataframe[self.uuid_column] == sensor_uuid) & 
                                        (self.dataframe[self.time_column] >= cycle_start_time) &
                                        (self.dataframe[self.time_column] <= cycle_stop_time)]
            value_data['time_normalized'] = (value_data[self.time_column] - cycle_start_time).dt.total_seconds()
            value_data = value_data[[self.time_column, 'time_normalized', self.value_column]].rename(
                columns={self.value_column: value_type})
            cycle_df = pd.concat([cycle_df, value_data.set_index(self.time_column)], axis=1, join='outer') if not cycle_df.empty else value_data.set_index(self.time_column)

        # Add marker column if marker_uuids are provided
        if marker_uuids:
            cycle_df['marker_time'] = self.dataframe[self.uuid_column].apply(
                lambda uuid: self._get_marker_time(uuid, marker_uuids, cycle_start_time)
            )

        # Add cycle-specific information
        cycle_df['cycle_id'] = cycle_id
        cycle_df['start_time'] = cycle_start_time
        cycle_df['stop_time'] = cycle_stop_time

        return cycle_df.reset_index(drop=True)

    def _calculate_cycle_statistics(self, cycle_df: pd.DataFrame, value_mappings: dict, cycle_id: int) -> dict:
        """
        Calculate cycle-level statistics (duration, mean, max, min, std dev)
        for a given cycle.

        Args:
            cycle_df (pd.DataFrame): The DataFrame of a single cycle's data.
            value_mappings (dict): A dictionary of value columns and their corresponding sensor UUIDs.
            cycle_id (int): The unique identifier for the cycle.

        Returns:
            dict: A dictionary of cycle-level statistics.
        """
        # Calculate the duration of the cycle
        cycle_duration = (cycle_df['stop_time'].iloc[0] - cycle_df['start_time'].iloc[0]).total_seconds()

        # Initialize stats dictionary with general cycle info
        stats = {
            'cycle_id': cycle_id,
            'cycle_duration': cycle_duration,
            'start_time': cycle_df['start_time'].iloc[0],
            'stop_time': cycle_df['stop_time'].iloc[0]
        }

        # For each value type (e.g., temperature, pressure), calculate statistics
        for value_type in value_mappings.keys():
            if value_type in cycle_df.columns:
                stats[f'{value_type}_mean']
        for value_type in value_mappings.keys():
            if value_type in cycle_df.columns:
                stats[f'{value_type}_mean'] = cycle_df[value_type].mean()
                stats[f'{value_type}_max'] = cycle_df[value_type].max()
                stats[f'{value_type}_min'] = cycle_df[value_type].min()
                stats[f'{value_type}_std'] = cycle_df[value_type].std()
            else:
                # If the column is missing, store NaN
                stats[f'{value_type}_mean'] = float('nan')
                stats[f'{value_type}_max'] = float('nan')
                stats[f'{value_type}_min'] = float('nan')
                stats[f'{value_type}_std'] = float('nan')

        return stats