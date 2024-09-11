import pandas as pd
from ..base import Base

class StringStatistics(Base):
    """
    Provides class methods to calculate statistics on string columns in a pandas DataFrame.
    """

    @classmethod
    def count_unique(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> int:
        """Returns the number of unique strings in the column."""
        return dataframe[column_name].nunique()

    @classmethod
    def most_frequent(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> str:
        """Returns the most frequent string in the column."""
        return dataframe[column_name].mode().iloc[0]

    @classmethod
    def count_most_frequent(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> int:
        """Returns the count of the most frequent string in the column."""
        most_frequent_value = cls.most_frequent(dataframe, column_name)
        return dataframe[column_name].value_counts().loc[most_frequent_value]

    @classmethod
    def count_null(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> int:
        """Returns the number of null (NaN) values in the column."""
        return dataframe[column_name].isna().sum()

    @classmethod
    def average_string_length(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> float:
        """Returns the average length of strings in the column, excluding null values."""
        return dataframe[column_name].dropna().str.len().mean()

    @classmethod
    def longest_string(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> str:
        """Returns the longest string in the column."""
        return dataframe[column_name].dropna().loc[dataframe[column_name].dropna().str.len().idxmax()]

    @classmethod
    def shortest_string(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> str:
        """Returns the shortest string in the column."""
        return dataframe[column_name].dropna().loc[dataframe[column_name].dropna().str.len().idxmin()]

    @classmethod
    def string_length_summary(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> pd.DataFrame:
        """Returns a summary of string lengths, including min, max, and average lengths."""
        lengths = dataframe[column_name].dropna().str.len()
        return pd.DataFrame({
            'Min Length': [lengths.min()],
            'Max Length': [lengths.max()],
            'Average Length': [lengths.mean()]
        })

    @classmethod
    def most_common_n_strings(cls, dataframe: pd.DataFrame, n: int, column_name: str = 'value_string') -> pd.Series:
        """Returns the top N most frequent strings in the column."""
        return dataframe[column_name].value_counts().head(n)

    @classmethod
    def contains_substring_count(cls, dataframe: pd.DataFrame, substring: str, column_name: str = 'value_string') -> int:
        """Counts how many strings contain the specified substring."""
        return dataframe[column_name].dropna().str.contains(substring).sum()

    @classmethod
    def starts_with_count(cls, dataframe: pd.DataFrame, prefix: str, column_name: str = 'value_string') -> int:
        """Counts how many strings start with the specified prefix."""
        return dataframe[column_name].dropna().str.startswith(prefix).sum()

    @classmethod
    def ends_with_count(cls, dataframe: pd.DataFrame, suffix: str, column_name: str = 'value_string') -> int:
        """Counts how many strings end with the specified suffix."""
        return dataframe[column_name].dropna().str.endswith(suffix).sum()

    @classmethod
    def uppercase_percentage(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> float:
        """Returns the percentage of strings that are fully uppercase."""
        total_non_null = dataframe[column_name].notna().sum()
        if total_non_null == 0:
            return 0.0
        uppercase_count = dataframe[column_name].dropna().str.isupper().sum()
        return (uppercase_count / total_non_null) * 100

    @classmethod
    def lowercase_percentage(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> float:
        """Returns the percentage of strings that are fully lowercase."""
        total_non_null = dataframe[column_name].notna().sum()
        if total_non_null == 0:
            return 0.0
        lowercase_count = dataframe[column_name].dropna().str.islower().sum()
        return (lowercase_count / total_non_null) * 100

    @classmethod
    def contains_digit_count(cls, dataframe: pd.DataFrame, column_name: str = 'value_string') -> int:
        """Counts how many strings contain digits."""
        return dataframe[column_name].dropna().str.contains(r'\d').sum()