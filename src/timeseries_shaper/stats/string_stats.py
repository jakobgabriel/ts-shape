import pandas as pd
from ..base import Base

class StringStatistics(Base):
    def __init__(self, dataframe: pd.DataFrame, column_name: str) -> None:
        """
        Initialize the StringStatistics class by using the Base class initialization.
        """
        super().__init__(dataframe)
        self.column_name = column_name

    def count_unique(self) -> int:
        """Returns the number of unique strings in the column."""
        return self.dataframe[self.column_name].nunique()

    def most_frequent(self) -> str:
        """Returns the most frequent string in the column."""
        return self.dataframe[self.column_name].mode().iloc[0]

    def count_most_frequent(self) -> int:
        """Returns the count of the most frequent string in the column."""
        most_frequent_value = self.most_frequent()
        return self.dataframe[self.column_name].value_counts().loc[most_frequent_value]

    def count_null(self) -> int:
        """Returns the number of null (NaN) values in the column."""
        return self.dataframe[self.column_name].isna().sum()

    def average_string_length(self) -> float:
        """Returns the average length of strings in the column, excluding null values."""
        return self.dataframe[self.column_name].dropna().str.len().mean()

    def longest_string(self) -> str:
        """Returns the longest string in the column."""
        return self.dataframe[self.column_name].dropna().loc[self.dataframe[self.column_name].dropna().str.len().idxmax()]

    def shortest_string(self) -> str:
        """Returns the shortest string in the column."""
        return self.dataframe[self.column_name].dropna().loc[self.dataframe[self.column_name].dropna().str.len().idxmin()]

    def string_length_summary(self) -> pd.DataFrame:
        """Returns a summary of string lengths, including min, max, and average lengths."""
        lengths = self.dataframe[self.column_name].dropna().str.len()
        return pd.DataFrame({
            'Min Length': [lengths.min()],
            'Max Length': [lengths.max()],
            'Average Length': [lengths.mean()]
        })
        
    def most_common_n_strings(self, n: int) -> pd.Series:
        """Returns the top N most frequent strings in the column."""
        return self.dataframe[self.column_name].value_counts().head(n)
    
    def contains_substring_count(self, substring: str) -> int:
        """Counts how many strings contain the specified substring."""
        return self.dataframe[self.column_name].dropna().str.contains(substring).sum()
    
    def starts_with_count(self, prefix: str) -> int:
        """Counts how many strings start with the specified prefix."""
        return self.dataframe[self.column_name].dropna().str.startswith(prefix).sum()
    
    def ends_with_count(self, suffix: str) -> int:
        """Counts how many strings end with the specified suffix."""
        return self.dataframe[self.column_name].dropna().str.endswith(suffix).sum()
    
    def uppercase_percentage(self) -> float:
        """Returns the percentage of strings that are fully uppercase."""
        total_non_null = self.dataframe[self.column_name].notna().sum()
        if total_non_null == 0:
            return 0.0
        uppercase_count = self.dataframe[self.column_name].dropna().str.isupper().sum()
        return (uppercase_count / total_non_null) * 100
    
    def lowercase_percentage(self) -> float:
        """Returns the percentage of strings that are fully lowercase."""
        total_non_null = self.dataframe[self.column_name].notna().sum()
        if total_non_null == 0:
            return 0.0
        lowercase_count = self.dataframe[self.column_name].dropna().str.islower().sum()
        return (lowercase_count / total_non_null) * 100
    
    def contains_digit_count(self) -> int:
        """Counts how many strings contain digits."""
        return self.dataframe[self.column_name].dropna().str.contains(r'\d').sum()
