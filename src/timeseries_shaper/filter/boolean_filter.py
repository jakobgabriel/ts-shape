import pandas as pd
from ..base import Base

class IsDeltaFilter(Base):
    """
    Provides methods for filtering is_delta columns in a pandas DataFrame,
    Allows specification of which column to operate on.

    Inherits from:
        Base (class): Base class with common initializations for DataFrame handling.

    Attributes:
        dataframe (DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to filter, defaulting to 'is_delta'.
    """
    def __init__(self, dataframe: pd.DataFrame, column_name: str = 'is_delta') -> None:
        """Initializes the StringFilter with a DataFrame and column name."""
        super().__init__(dataframe)
        self.column_name = column_name
    
    def filter_is_delta_true(self) -> pd.DataFrame:
        """Filters rows where 'is_delta' is True."""
        return self.dataframe[self.dataframe[self.column_name] == True]

    def filter_is_delta_false(self) -> pd.DataFrame:
        """Filters rows where 'is_delta' is False."""
        return self.dataframe[self.dataframe[self.column_name] == False]

class BooleanFilter(Base):
    """
    Provides methods for filtering boolean columns in a pandas DataFrame,
    particularly focusing on e.g. status changes. Allows specification of which column to operate on.

    Inherits from:
        Base (class): Base class with common initializations for DataFrame handling.

    Attributes:
        dataframe (DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to filter, defaulting to 'value_bool'.
    """
    def __init__(self, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> None:
        """Initializes the StringFilter with a DataFrame and column name."""
        super().__init__(dataframe)
        self.column_name = column_name
    
    def filter_falling_value_bool(self) -> pd.DataFrame:
        """Filters rows where 'value_bool' changes from True to False."""
        self.dataframe['previous_value_bool'] = self.dataframe['value_bool'].shift(1)
        return self.dataframe[(self.dataframe['previous_value_bool'] == True) & (self.dataframe['value_bool'] == False)]

    def filter_raising_value_bool(self) -> pd.DataFrame:
        """Filters rows where 'value_bool' changes from False to True."""
        self.dataframe['previous_value_bool'] = self.dataframe['value_bool'].shift(1)
        return self.dataframe[(self.dataframe['previous_value_bool'] == False) & (self.dataframe['value_bool'] == True)]