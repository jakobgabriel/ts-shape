import pandas as pd
from ts_shape.base import Base

class IsDeltaFilter(Base):
    """
    Provides class methods for filtering is_delta columns in a pandas DataFrame.
    """

    @classmethod
    def filter_is_delta_true(cls, dataframe: pd.DataFrame, column_name: str = 'is_delta') -> pd.DataFrame:
        """Filters rows where 'is_delta' is True."""
        # No need for instance, working directly on class level
        return dataframe[dataframe[column_name] == True]

    @classmethod
    def filter_is_delta_false(cls, dataframe: pd.DataFrame, column_name: str = 'is_delta') -> pd.DataFrame:
        """Filters rows where 'is_delta' is False."""
        return dataframe[dataframe[column_name] == False]


class BooleanFilter(Base):
    """
    Provides class methods for filtering boolean columns in a pandas DataFrame,
    particularly focusing on status changes.
    """
    
    @classmethod
    def filter_falling_value_bool(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> pd.DataFrame:
        """Filters rows where 'value_bool' changes from True to False."""
        dataframe['previous_value_bool'] = dataframe[column_name].shift(1)
        return dataframe[(dataframe['previous_value_bool'] == True) & (dataframe[column_name] == False)]

    @classmethod
    def filter_raising_value_bool(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> pd.DataFrame:
        """Filters rows where 'value_bool' changes from False to True."""
        dataframe['previous_value_bool'] = dataframe[column_name].shift(1)
        return dataframe[(dataframe['previous_value_bool'] == False) & (dataframe[column_name] == True)]