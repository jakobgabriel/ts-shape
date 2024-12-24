from typing import Dict, List, Optional
import pandas as pd
from ts_shape.base import Base
import logging


class CycleDataProcessor(Base):
    """
    A class to process cycle-based data and values. It allows for splitting, merging, and grouping DataFrames 
    based on cycles, as well as handling grouping and transformations by cycle UUIDs.
    """

    def __init__(self, cycles_df: pd.DataFrame, values_df: pd.DataFrame, cycle_uuid_col: str = "cycle_uuid", systime_col: str = "systime"):
        """
        Initializes the CycleDataProcessor with cycles and values DataFrames.

        :param cycles_df: DataFrame containing columns 'cycle_start', 'cycle_end', and 'cycle_uuid'.
        :param values_df: DataFrame containing the values and timestamps in the 'systime' column.
        :param cycle_uuid_col: Name of the column representing cycle UUIDs.
        :param systime_col: Name of the column representing the timestamps for the values.
        """
        super().__init__(values_df)  # Call the parent constructor
        self.values_df = values_df.copy()  # Initialize self.values_df explicitly
        self.cycles_df = cycles_df.copy()
        self.cycle_uuid_col = cycle_uuid_col
        self.systime_col = systime_col

        # Ensure proper datetime format
        self.cycles_df['cycle_start'] = pd.to_datetime(self.cycles_df['cycle_start'])
        self.cycles_df['cycle_end'] = pd.to_datetime(self.cycles_df['cycle_end'])
        self.values_df[systime_col] = pd.to_datetime(self.values_df[systime_col])

        logging.info("CycleDataProcessor initialized with cycles and values DataFrames.")

    def split_by_cycle(self) -> Dict[str, pd.DataFrame]:
        """
        Splits the values DataFrame by cycles defined in the cycles DataFrame. 
        Each cycle is defined by a start and end time, and the corresponding values are filtered accordingly.

        :return: Dictionary where keys are cycle_uuids and values are DataFrames with the corresponding cycle data.
        """
        result = {}
        for _, row in self.cycles_df.iterrows():
            mask = (self.values_df[self.systime_col] >= row['cycle_start']) & (self.values_df[self.systime_col] <= row['cycle_end'])
            result[row[self.cycle_uuid_col]] = self.values_df[mask].copy()

        logging.info(f"Split {len(result)} cycles.")
        return result

    def merge_dataframes_by_cycle(self) -> pd.DataFrame:
        """
        Merges the values DataFrame with the cycles DataFrame based on the cycle time intervals. 
        Appends the 'cycle_uuid' to the values DataFrame.

        :return: DataFrame with an added 'cycle_uuid' column.
        """
        # Merge based on systime falling within cycle_start and cycle_end
        self.values_df[self.cycle_uuid_col] = None

        for _, row in self.cycles_df.iterrows():
            mask = (self.values_df[self.systime_col] >= row['cycle_start']) & (self.values_df[self.systime_col] <= row['cycle_end'])
            self.values_df.loc[mask, self.cycle_uuid_col] = row[self.cycle_uuid_col]

        merged_df = self.values_df.dropna(subset=[self.cycle_uuid_col])
        logging.info(f"Merged DataFrame contains {len(merged_df)} records.")
        return merged_df

    def group_by_cycle_uuid(self, data: Optional[pd.DataFrame] = None) -> List[pd.DataFrame]:
        """
        Group the DataFrame by the cycle_uuid column, resulting in a list of DataFrames, each containing data for one cycle.

        :param data: DataFrame containing the data to be grouped by cycle_uuid. If None, uses the internal values_df.
        :return: List of DataFrames, each containing data for a unique cycle_uuid.
        """
        if data is None:
            data = self.values_df

        grouped_dataframes = [group for _, group in data.groupby(self.cycle_uuid_col)]
        logging.info(f"Grouped data into {len(grouped_dataframes)} cycle UUID groups.")
        return grouped_dataframes

    def split_dataframes_by_group(self, dfs: List[pd.DataFrame], column: str) -> List[pd.DataFrame]:
        """
        Splits a list of DataFrames by groups based on a specified column. 
        This function performs a groupby operation on each DataFrame in the list and then flattens the result.

        :param dfs: List of DataFrames to be split.
        :param column: Column name to group by.
        :return: List of DataFrames, each corresponding to a group in the original DataFrames.
        """
        split_dfs = []
        for df in dfs:
            groups = df.groupby(column)
            for _, group in groups:
                split_dfs.append(group)

        logging.info(f"Split data into {len(split_dfs)} groups based on column '{column}'.")
        return split_dfs

    def _filter_by_time_range(self, start_time: pd.Timestamp, end_time: pd.Timestamp) -> pd.DataFrame:
        """
        Filters the values DataFrame by the given time range.

        :param start_time: Start of the time range.
        :param end_time: End of the time range.
        :return: Filtered DataFrame containing rows within the time range.
        """
        mask = (self.values_df[self.systime_col] >= start_time) & (self.values_df[self.systime_col] <= end_time)
        return self.values_df[mask]
