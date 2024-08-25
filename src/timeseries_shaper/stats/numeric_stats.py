import pandas as pd
from ..base import Base

class NumericStatistics(Base):
    def __init__(self, dataframe: pd.DataFrame, column_name: str) -> None:
        """
        Initialize the NumericStatistics class by using the Base class initialization.
        """
        super().__init__(dataframe)
        self.column_name = column_name

    def column_mean(self):
        """Calculate the mean of a specified column."""
        return self.dataframe[self.column_name].mean()

    def column_median(self):
        """Calculate the median of a specified column."""
        return self.dataframe[self.column_name].median()

    def column_std(self):
        """Calculate the standard deviation of a specified column."""
        return self.dataframe[self.column_name].std()

    def column_variance(self):
        """Calculate the variance of a specified column."""
        return self.dataframe[self.column_name].var()

    def column_min(self):
        """Calculate the minimum value of a specified column."""
        return self.dataframe[self.column_name].min()

    def column_max(self):
        """Calculate the maximum value of a specified column."""
        return self.dataframe[self.column_name].max()

    def column_sum(self):
        """Calculate the sum of a specified column."""
        return self.dataframe[self.column_name].sum()

    def column_kurtosis(self):
        """Calculate the kurtosis of a specified column."""
        return self.dataframe[self.column_name].kurt()

    def column_skewness(self):
        """Calculate the skewness of a specified column."""
        return self.dataframe[self.column_name].skew()

    def describe(self) -> pd.DataFrame:
        """Provide a statistical summary for numeric columns in the DataFrame."""
        return self.dataframe.describe()
