import pandas as pd
import numpy as np
from scipy.stats import zscore
from typing import Callable, Union
from ts_shape.utils.base import Base


class OutlierDetectionEvents(Base):
    """
    Processes time series data to detect outliers based on specified statistical methods.
    """

    def __init__(self, dataframe: pd.DataFrame, value_column: str, event_uuid: str = 'outlier_event', 
                 time_threshold: str = '5min') -> None:
        """
        Initializes the OutlierDetectionEvents with specific attributes for outlier detection.

        Parameters:
            dataframe (pd.DataFrame): The input time series DataFrame.
            value_column (str): The name of the column containing the values for outlier detection.
            event_uuid (str): A UUID or identifier for detected outlier events.
            time_threshold (str): The time threshold to group close events together.
        """
        super().__init__(dataframe)
        self.value_column = value_column
        self.event_uuid = event_uuid
        self.time_threshold = time_threshold

    def _group_outliers(self, outliers_df: pd.DataFrame) -> pd.DataFrame:
        """
        Groups detected outliers that are close in time and prepares the final events DataFrame.

        Returns:
            pd.DataFrame: A DataFrame of grouped outlier events.
        """
        # Grouping outliers that are close to each other in terms of time
        outliers_df['group_id'] = (outliers_df['systime'].diff().abs() > pd.to_timedelta(self.time_threshold)).cumsum()

        # Prepare events DataFrame
        events_data = []

        for group_id in outliers_df['group_id'].unique():
            group_data = outliers_df[outliers_df['group_id'] == group_id]
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
            events_df = pd.DataFrame(columns=outliers_df.columns)  # Create empty DataFrame if no data

        events_df[self.value_column] = np.nan
        events_df['is_delta'] = True

        return events_df.drop(['outlier', 'group_id'], axis=1)

    def detect_outliers_zscore(self, threshold: float = 3.0) -> pd.DataFrame:
        """
        Detects outliers using the Z-score method.

        Parameters:
            threshold (float): The Z-score threshold for detecting outliers.

        Returns:
            pd.DataFrame: A DataFrame of detected outliers and grouped events.
        """
        df = self.dataframe.copy()

        # Convert 'systime' to datetime and sort the DataFrame by 'systime' in descending order
        df['systime'] = pd.to_datetime(df['systime'])
        df = df.sort_values(by='systime', ascending=False)

        # Detect outliers using the Z-score method
        df['outlier'] = np.abs(zscore(df[self.value_column])) > threshold

        # Filter to keep only outliers
        outliers_df = df[df['outlier']]

        # Group and return the outliers
        return self._group_outliers(outliers_df)

    def detect_outliers_iqr(self, threshold: tuple = (1.5, 1.5)) -> pd.DataFrame:
        """
        Detects outliers using the IQR method.

        Parameters:
            threshold (tuple): The multipliers for the IQR range for detecting outliers (lower, upper).

        Returns:
            pd.DataFrame: A DataFrame of detected outliers and grouped events.
        """
        df = self.dataframe.copy()

        # Convert 'systime' to datetime and sort the DataFrame by 'systime' in descending order
        df['systime'] = pd.to_datetime(df['systime'])
        df = df.sort_values(by='systime', ascending=False)

        # Detect outliers using the IQR method
        Q1 = df[self.value_column].quantile(0.25)
        Q3 = df[self.value_column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold[0] * IQR
        upper_bound = Q3 + threshold[1] * IQR
        df['outlier'] = (df[self.value_column] < lower_bound) | (df[self.value_column] > upper_bound)

        # Filter to keep only outliers
        outliers_df = df[df['outlier']]

        # Group and return the outliers
        return self._group_outliers(outliers_df)

# Example usage:
# outlier_detector = OutlierDetectionEvents(dataframe=df, value_column='value')
# detected_outliers_zscore = outlier_detector.detect_outliers_zscore(threshold=3.0)
# detected_outliers_iqr = outlier_detector.detect_outliers_iqr(threshold=(1.5, 1.5))