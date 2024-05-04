import pandas as pd
from ..base import Base

class IntegerFilter(Base):
    """
    Provides filtering methods for integer columns in a pandas DataFrame.

    Inherits from:
        Base (class): Base class with common initializations for DataFrame handling.

    Attributes:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to apply the filters to; defaults to 'value_integer'.
    
    Args:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to apply the filters to; defaults to 'value_integer'.
    """
    def __init__(self, dataframe: pd.DataFrame, column_name: str = 'value_integer') -> None:
        """Initializes the StringFilter with a DataFrame and column name."""
        super().__init__(dataframe)
        self.column_name = column_name

    def filter_value_integer_match(self, integer_value: int) -> pd.DataFrame:
        """Filters rows where 'value_integer' matches the specified integer."""
        return self.dataframe[self.dataframe[self.column_name] == integer_value]

    def filter_value_integer_not_match(self, integer_value: int) -> pd.DataFrame:
        """Filters rows where 'value_integer' does not match the specified integer."""
        return self.dataframe[self.dataframe[self.column_name] != integer_value]

class DoubleFilte(Base):
    """
    Provides methods for filtering double (floating-point) columns in a pandas DataFrame,
    particularly focusing on NaN values.

    Inherits from:
        Base (class): Base class with common initializations for DataFrame handling.

    Attributes:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to apply the filters to; defaults to 'value_double'.
    
    Args:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to apply the filters to; defaults to 'value_double'.
    """
    def __init__(self, dataframe: pd.DataFrame, column_name: str = 'value_double') -> None:
        """Initializes the StringFilter with a DataFrame and column name."""
        super().__init__(dataframe)
        self.column_name = column_name

    def filter_nan_value_double(self) -> pd.DataFrame:
        """Filters out rows where 'value_double' is NaN."""
        return self.dataframe[self.dataframe[self.column_name].notna()]