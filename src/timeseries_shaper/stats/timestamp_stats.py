import pandas as pd
from ..base import Base

class TimestampStatistics(Base):
    def __init__(self, dataframe: pd.DataFrame, column_name: str) -> None:
        """
        Initialize the TimestampStatistics class by using the Base class initialization.
        """
        super().__init__(dataframe)
        self.column_name = column_name

    def count_null(self) -> int:
        """Returns the number of null (NaN) values in the timestamp column."""
        return self.dataframe[self.column_name].isna().sum()

    def count_not_null(self) -> int:
        """Returns the number of non-null (valid) timestamps in the column."""
        return self.dataframe[self.column_name].notna().sum()

    def earliest_timestamp(self):
        """Returns the earliest timestamp in the column."""
        return self.dataframe[self.column_name].min()

    def latest_timestamp(self):
        """Returns the latest timestamp in the column."""
        return self.dataframe[self.column_name].max()

    def timestamp_range(self):
        """Returns the time range (difference) between the earliest and latest timestamps."""
        return self.latest_timestamp() - self.earliest_timestamp()

    def most_frequent_timestamp(self):
        """Returns the most frequent timestamp in the column."""
        return self.dataframe[self.column_name].mode().iloc[0]

    def count_most_frequent_timestamp(self) -> int:
        """Returns the count of the most frequent timestamp in the column."""
        most_frequent_value = self.most_frequent_timestamp()
        return self.dataframe[self.column_name].value_counts().loc[most_frequent_value]

    def year_distribution(self) -> pd.Series:
        """Returns the distribution of timestamps per year."""
        return self.dataframe[self.column_name].dt.year.value_counts()

    def month_distribution(self) -> pd.Series:
        """Returns the distribution of timestamps per month."""
        return self.dataframe[self.column_name].dt.month.value_counts()

    def weekday_distribution(self) -> pd.Series:
        """Returns the distribution of timestamps per weekday."""
        return self.dataframe[self.column_name].dt.weekday.value_counts()

    def hour_distribution(self) -> pd.Series:
        """Returns the distribution of timestamps per hour of the day."""
        return self.dataframe[self.column_name].dt.hour.value_counts()

    def most_frequent_day(self) -> int:
        """Returns the most frequent day of the week (0=Monday, 6=Sunday)."""
        return self.dataframe[self.column_name].dt.weekday.mode().iloc[0]

    def most_frequent_hour(self) -> int:
        """Returns the most frequent hour of the day (0-23)."""
        return self.dataframe[self.column_name].dt.hour.mode().iloc[0]

    def average_time_gap(self) -> pd.Timedelta:
        """Returns the average time gap between consecutive timestamps."""
        sorted_times = self.dataframe[self.column_name].dropna().sort_values()
        time_deltas = sorted_times.diff().dropna()
        return time_deltas.mean()

    def median_timestamp(self):
        """Returns the median timestamp in the column."""
        return self.dataframe[self.column_name].median()

    def standard_deviation_timestamps(self) -> pd.Timedelta:
        """Returns the standard deviation of the time differences between consecutive timestamps."""
        sorted_times = self.dataframe[self.column_name].dropna().sort_values()
        time_deltas = sorted_times.diff().dropna()
        return time_deltas.std()

    def timestamp_quartiles(self) -> pd.Series:
        """Returns the 25th, 50th (median), and 75th percentiles of the timestamps."""
        return self.dataframe[self.column_name].quantile([0.25, 0.5, 0.75])

    def days_with_most_activity(self, n: int = 3) -> pd.Series:
        """Returns the top N days with the most timestamp activity."""
        return self.dataframe[self.column_name].dt.date.value_counts().head(n)