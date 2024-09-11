import pandas as pd
from ..base import Base

class NumericStatistics(Base):
    """
    Provides class methods to calculate statistics on numeric columns in a pandas DataFrame.
    """

    @classmethod
    def column_mean(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the mean of a specified column."""
        return dataframe[column_name].mean()

    @classmethod
    def column_median(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the median of a specified column."""
        return dataframe[column_name].median()

    @classmethod
    def column_std(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the standard deviation of a specified column."""
        return dataframe[column_name].std()

    @classmethod
    def column_variance(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the variance of a specified column."""
        return dataframe[column_name].var()

    @classmethod
    def column_min(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the minimum value of a specified column."""
        return dataframe[column_name].min()

    @classmethod
    def column_max(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the maximum value of a specified column."""
        return dataframe[column_name].max()

    @classmethod
    def column_sum(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the sum of a specified column."""
        return dataframe[column_name].sum()

    @classmethod
    def column_kurtosis(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the kurtosis of a specified column."""
        return dataframe[column_name].kurt()

    @classmethod
    def column_skewness(cls, dataframe: pd.DataFrame, column_name: str) -> float:
        """Calculate the skewness of a specified column."""
        return dataframe[column_name].skew()

    @classmethod
    def describe(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Provide a statistical summary for numeric columns in the DataFrame."""
        return dataframe.describe()