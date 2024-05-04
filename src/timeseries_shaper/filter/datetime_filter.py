import pandas as pd
from ..base import Base

class DateTimeFilter(Base):
    """
    Provides methods for filtering time columns in a pandas DataFrame,
    Allows specification of which column to operate on.

    Inherits from:
        Base (class): Base class with common initializations for DataFrame handling.

    Attributes:
        dataframe (DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to filter, defaulting to 'systime'.
    """
    def __init__(self, dataframe: pd.DataFrame, column_name: str = 'systime') -> None:
        """Initializes the StringFilter with a DataFrame and column name."""
        super().__init__(dataframe)
        self.column_name = column_name

    def filter_after_date(self, date) -> pd.DataFrame:
        """
        Filters the DataFrame to include only rows after the specified date.

        Args:
        - date (str): The cutoff date in 'YYYY-MM-DD' format.

        Returns:
        - pd.DataFrame: A DataFrame containing rows where the 'systime' is after the specified date.

        Example:
        --------
        >>> sf = DateTimeFilter(df)
        >>> filtered_data = sf.filter_after_date("2023-01-01")
        >>> print(filtered_data)
        """
        return self.dataframe[self.dataframe[self.column_name] > pd.to_datetime(date)]

    def filter_before_date(self, date) -> pd.DataFrame:
        """
        Filters the DataFrame to include only rows before the specified date.

        Args:
        - date (str): The cutoff date in 'YYYY-MM-DD' format.

        Returns:
        - pd.DataFrame: A DataFrame containing rows where the 'systime' is before the specified date.

        Example:
        --------
        >>> sf = DateTimeFilter(df)
        >>> filtered_data = sf.filter_before_date("2023-01-01")
        >>> print(filtered_data)
        """
        return self.dataframe[self.dataframe[self.column_name] < pd.to_datetime(date)]

    def filter_between_dates(self, start_date, end_date):
        """
        Filters the DataFrame to include only rows between the specified start and end dates.

        Args:
        - start_date (str): The start date of the interval in 'YYYY-MM-DD' format.
        - end_date (str): The end date of the interval in 'YYYY-MM-DD' format.

        Returns:
        - pd.DataFrame: A DataFrame containing rows where the 'systime' is between the specified dates.

        Example:
        --------
        >>> sf = DateTimeFilter(df)
        >>> filtered_data = sf.filter_between_dates("2023-01-01", "2023-02-01")
        >>> print(filtered_data)
        """
        mask = (self.dataframe[self.column_name] > pd.to_datetime(start_date)) & (self.dataframe[self.column_name] < pd.to_datetime(end_date))
        return self.dataframe[mask]

    def filter_after_datetime(self, datetime) -> pd.DataFrame:
        """
        Filters the DataFrame to include only rows after the specified datetime.

        Args:
        - datetime (str): The cutoff datetime in 'YYYY-MM-DD HH:MM:SS' format.

        Returns:
        - pd.DataFrame: A DataFrame containing rows where the 'systime' is after the specified datetime.

        Example:
        --------
        >>> sf = DateTimeFilter(df)
        >>> filtered_data = sf.filter_after_datetime("2023-01-01 12:00:00")
        >>> print(filtered_data)
        """
        return self.dataframe[self.dataframe[self.column_name] > pd.to_datetime(datetime)]

    def filter_before_datetime(self, datetime) -> pd.DataFrame:
        """
        Filters the DataFrame to include only rows before the specified datetime.

        Args:
        - datetime (str): The cutoff datetime in 'YYYY-MM-DD HH:MM:SS' format.

        Returns:
        - pd.DataFrame: A DataFrame containing rows where the 'systime' is before the specified datetime.

        Example:
        --------
        >>> sf = DateTimeFilter(df)
        >>> filtered_data = sf.filter_before_datetime("2023-01-01 12:00:00")
        >>> print(filtered_data)
        """
        return self.dataframe[self.dataframe[self.column_name] < pd.to_datetime(datetime)]

    def filter_between_datetimes(self, start_datetime, end_datetime) -> pd.DataFrame:
        """
        Filters the DataFrame to include only rows between the specified start and end datetimes.

        Args:
        - start_datetime (str): The start datetime of the interval in 'YYYY-MM-DD HH:MM:SS' format.
        - end_datetime (str): The end datetime of the interval in 'YYYY-MM-DD HH:MM:SS' format.

        Returns:
        - pd.DataFrame: A DataFrame containing rows where the 'systime' is between the specified datetimes.

        Example:
        --------
        >>> sf = DateTimeFilter(df)
        >>> filtered_data = sf.filter_between_datetimes("2023-01-01 12:00:00", "2023-02-01 12:00:00")
        >>> print(filtered_data)
        """
        mask = (self.dataframe[self.column_name] > pd.to_datetime(start_datetime)) & (self.dataframe[self.column_name] < pd.to_datetime(end_datetime))
        return self.dataframe[mask]