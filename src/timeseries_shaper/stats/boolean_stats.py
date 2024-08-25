import pandas as pd
from ..base import Base

class BooleanStatistics(Base):
    def __init__(self, dataframe: pd.DataFrame, column_name: str) -> None:
        """
        Initialize the BooleanStatistics class by using the Base class initialization.
        """
        super().__init__(dataframe)
        self.column_name = column_name

    def count_true(self) -> int:
        """Returns the count of True values in the boolean column."""
        return self.dataframe[self.column_name].sum()

    def count_false(self) -> int:
        """Returns the count of False values in the boolean column."""
        return (self.dataframe[self.column_name] == False).sum()

    def count_null(self) -> int:
        """Returns the count of null (NaN) values in the boolean column."""
        return self.dataframe[self.column_name].isna().sum()

    def count_not_null(self) -> int:
        """Returns the count of non-null (True or False) values in the boolean column."""
        return self.dataframe[self.column_name].notna().sum()

    def true_percentage(self) -> float:
        """Returns the percentage of True values in the boolean column."""
        true_count = self.count_true()
        total_count = self.count_not_null()
        return (true_count / total_count) * 100 if total_count > 0 else 0.0

    def false_percentage(self) -> float:
        """Returns the percentage of False values in the boolean column."""
        false_count = self.count_false()
        total_count = self.count_not_null()
        return (false_count / total_count) * 100 if total_count > 0 else 0.0

    def summary(self) -> pd.DataFrame:
        """Returns a summary DataFrame with counts and percentages of True, False, and Null values."""
        data = {
            'Count True': [self.count_true()],
            'Count False': [self.count_false()],
            'Count Null': [self.count_null()],
            'True %': [self.true_percentage()],
            'False %': [self.false_percentage()]
        }
        return pd.DataFrame(data)