import pandas as pd
from ..base import Base

class StringFilter(Base):
    """
    A class for filtering operations on string columns within a pandas DataFrame.

    Inherits from:
        Base (class): Base class with common initializations for DataFrame handling.

    Attributes:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to apply the filters to; defaults to 'value_string'.

    Args:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to apply the filters to; defaults to 'value_string'.
    """
    def __init__(self, dataframe: pd.DataFrame, column_name: str = 'value_string') -> None:
        """Initializes the StringFilter with a DataFrame and column name."""
        super().__init__(dataframe)
        self.column_name = column_name
    
    def filter_na_value_string(self) -> pd.DataFrame:
        """Filters out rows where the specified string column is NA."""
        return self.dataframe[self.dataframe[self.column_name].notna()]

    def filter_value_string_match(self, string_value: str) -> pd.DataFrame:
        """Filters rows where the specified string column matches the provided string."""
        return self.dataframe[self.dataframe[self.column_name] == string_value]

    def filter_value_string_not_match(self, string_value: str) -> pd.DataFrame:
        """Filters rows where the specified string column does not match the provided string."""
        return self.dataframe[self.dataframe[self.column_name] != string_value]

    def filter_string_contains(self, substring: str) -> pd.DataFrame:
        """Filters rows where the specified string column contains the provided substring."""
        return self.dataframe[self.dataframe[self.column_name].str.contains(substring, na=False)]

    def regex_clean_value_string(self, regex_pattern: str = r'(\d+)\s*([a-zA-Z]*)', replacement: str = '', regex: bool = True) -> pd.DataFrame:
        """Applies a regex pattern to split the specified string column into components."""
        self.dataframe[self.column_name] = self.dataframe[self.column_name].str.replace(regex_pattern, replacement, regex=regex)
        return self.dataframe

    def detect_changes_in_string(self) -> pd.DataFrame:
        """Detects changes from row to row in the specified string column."""
        changes_detected = self.dataframe[self.column_name].ne(self.dataframe[self.column_name].shift())
        self.dataframe = self.dataframe[changes_detected]
        if self.dataframe.empty:
            print("No changes detected in the '{0}' column between consecutive rows.".format(self.column_name))
        return self.dataframe
