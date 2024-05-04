import pandas as pd
import numpy as np
import operator

class ToleranceDeviationEvents:
    """
    A class to process DataFrame data for specific events, comparing tolerance and actual values.

    Attributes:
        tolerance_column (str): The column name containing tolerance values.
        actual_column (str): The column name containing actual values to be compared against tolerances.
        tolerance_uuid (str): UUID identifier for rows that set tolerance values.
        actual_uuid (str): UUID identifier for rows containing actual values.
        event_uuid (str): UUID to assign to generated event rows.
        compare_func (callable): Function to compare tolerance and actual values (default: operator.ge).
        time_threshold (str): Time difference threshold to group close events (default: '5min').

    Methods:
        process_and_group_data_with_events(df):
            Processes a DataFrame to compare values, group events based on time threshold, and filter based on UUIDs.
    """

    def __init__(self, tolerance_column, actual_column, tolerance_uuid, actual_uuid, event_uuid, compare_func=operator.ge, time_threshold='5min'):
        """
        Constructs all the necessary attributes for the DataProcessor object.

        Parameters:
            tolerance_column (str): The name of the column from which to read the tolerance values.
            actual_column (str): The name of the column from which to read the actual values.
            tolerance_uuid (str): UUID for tolerance data rows.
            actual_uuid (str): UUID for actual data rows.
            event_uuid (str): UUID to assign to generated events.
            compare_func (callable, optional): Function to use for comparing actual values against tolerance values.
            time_threshold (str, optional): Threshold for time difference to group events.
        """
        self.tolerance_column = tolerance_column
        self.actual_column = actual_column
        self.tolerance_uuid = tolerance_uuid
        self.actual_uuid = actual_uuid
        self.event_uuid = event_uuid
        self.compare_func = compare_func
        self.time_threshold = time_threshold

    def process_and_group_data_with_events(self, df):
        """
        Processes DataFrame to apply tolerance checks, group events by time, and generate an events DataFrame.

        The function first sets tolerance values for comparison, removes non-relevant rows,
        and applies the specified comparison function. It then groups these events based on the defined time threshold and
        filters the events based on the actual_uuid. Events are aggregated to form a summary per group.

        Parameters:
            df (pd.DataFrame): DataFrame containing the data to process.

        Returns:
            pd.DataFrame: A DataFrame of processed and grouped event data.
        """
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