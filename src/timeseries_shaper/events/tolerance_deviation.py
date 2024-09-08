from ..base import Base
import pandas as pd
import numpy as np
import operator
from typing import Callable

class ToleranceDeviationEvents(Base):
    """
    Inherits from Base and processes DataFrame data for specific events, comparing tolerance and actual values.
    """

    def __init__(self, dataframe: pd.DataFrame, tolerance_column: str, actual_column: str, 
                 tolerance_uuid: str, actual_uuid: str, event_uuid: str, 
                 compare_func: Callable[[pd.Series, pd.Series], pd.Series] = operator.ge, 
                 time_threshold: str = '5min') -> None:
        """
        Initializes the ToleranceDeviationEvents with specific event attributes.
        Inherits the sorted dataframe from the Base class.
        """
        super().__init__(dataframe)  # Inherit and initialize Base class

        self.tolerance_column: str = tolerance_column
        self.actual_column: str = actual_column
        self.tolerance_uuid: str = tolerance_uuid
        self.actual_uuid: str = actual_uuid
        self.event_uuid: str = event_uuid
        self.compare_func: Callable[[pd.Series, pd.Series], pd.Series] = compare_func
        self.time_threshold: str = time_threshold

    def process_and_group_data_with_events(self) -> pd.DataFrame:
        """
        Processes DataFrame to apply tolerance checks, group events by time, and generate an events DataFrame.

        Returns:
            pd.DataFrame: A DataFrame of processed and grouped event data.
        """
        df = self.dataframe  # Inherited from Base class

        # Convert 'systime' to datetime and sort the DataFrame by 'systime' in descending order
        df['systime'] = pd.to_datetime(df['systime'])
        df = df.sort_values(by='systime', ascending=False)

        # Create a column for lagged tolerance values
        df['tolerance_value'] = df.apply(
            lambda row: row[self.tolerance_column] if (row['uuid'] == self.tolerance_uuid and row['is_delta']) else pd.NA, axis=1
        )
        
        # Forward fill the tolerance values to propagate the last observed tolerance value
        df['tolerance_value'] = df['tolerance_value'].ffill()

        # Remove tolerance setting rows from the dataset
        df = df[df['uuid'] != self.tolerance_uuid]

        # Ensure there are no NA values in the tolerance_value column before comparison
        df = df.dropna(subset=['tolerance_value'])

        # Apply comparison function to compare actual values with tolerance values
        df = df[self.compare_func(df[self.actual_column], df['tolerance_value'])]
        df['value_bool'] = True  # Assign True in the value_bool column for kept rows

        # Grouping events that are close to each other in terms of time
        df['group_id'] = (df['systime'].diff().abs() > pd.to_timedelta(self.time_threshold)).cumsum()

        # Filter for specific UUID and prepare events DataFrame
        filtered_df = df[df['uuid'] == self.actual_uuid]
        events_data = []

        for group_id in filtered_df['group_id'].unique():
            group_data = filtered_df[filtered_df['group_id'] == group_id]
            if group_data.shape[0] > 1:  # Ensure there's more than one row to work with
                first_row = group_data.nsmallest(1, 'systime')
                last_row = group_data.nlargest(1, 'systime')
                combined_rows = pd.concat([first_row, last_row])
                events_data.append(combined_rows)

        # Convert list of DataFrame slices to a single DataFrame
        if events_data:
            events_df = pd.concat(events_data)
            events_df['uuid'] = self.event_uuid
        else:
            events_df = pd.DataFrame(columns=filtered_df.columns)  # Create empty DataFrame if no data

        events_df = events_df.drop(['tolerance_value', 'group_id'], axis=1)
        events_df[self.actual_column] = np.nan
        events_df['is_delta'] = True

        return events_df