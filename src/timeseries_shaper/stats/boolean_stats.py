import pandas as pd
from ..base import Base

class BooleanStatistics(Base):
    """
    Provides class methods to calculate statistics on a boolean column in a pandas DataFrame.
    """

    @classmethod
    def count_true(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> int:
        """Returns the count of True values in the boolean column."""
        return dataframe[column_name].sum()

    @classmethod
    def count_false(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> int:
        """Returns the count of False values in the boolean column."""
        return (dataframe[column_name] == False).sum()

    @classmethod
    def count_null(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> int:
        """Returns the count of null (NaN) values in the boolean column."""
        return dataframe[column_name].isna().sum()

    @classmethod
    def count_not_null(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> int:
        """Returns the count of non-null (True or False) values in the boolean column."""
        return dataframe[column_name].notna().sum()

    @classmethod
    def true_percentage(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> float:
        """Returns the percentage of True values in the boolean column."""
        true_count = cls.count_true(dataframe, column_name)
        total_count = cls.count_not_null(dataframe, column_name)
        return (true_count / total_count) * 100 if total_count > 0 else 0.0

    @classmethod
    def false_percentage(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> float:
        """Returns the percentage of False values in the boolean column."""
        false_count = cls.count_false(dataframe, column_name)
        total_count = cls.count_not_null(dataframe, column_name)
        return (false_count / total_count) * 100 if total_count > 0 else 0.0

    @classmethod
    def summary(cls, dataframe: pd.DataFrame, column_name: str = 'value_bool') -> pd.DataFrame:
        """Returns a summary DataFrame with counts and percentages of True, False, and Null values."""
        data = {
            'Count True': [cls.count_true(dataframe, column_name)],
            'Count False': [cls.count_false(dataframe, column_name)],
            'Count Null': [cls.count_null(dataframe, column_name)],
            'True %': [cls.true_percentage(dataframe, column_name)],
            'False %': [cls.false_percentage(dataframe, column_name)]
        }
        return pd.DataFrame(data)