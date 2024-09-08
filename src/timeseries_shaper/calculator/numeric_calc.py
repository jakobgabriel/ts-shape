import pandas as pd
from ..base import Base

class IntegerCalc(Base):
    """
    Provides calculation methods for integer columns in a pandas DataFrame.

    Inherits from:
        Base (class): Base class with common initializations for DataFrame handling.

    Attributes:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to apply the calculations to; defaults to 'value_integer'.
    
    Args:
        dataframe (pd.DataFrame): The DataFrame to perform operations on.
        column_name (str): The name of the column to apply the calculations to; defaults to 'value_integer'.
    """
    def __init__(self, dataframe: pd.DataFrame, column_name: str = 'value_integer') -> None:
        """Initializes the IntegerCalc with a DataFrame and column name."""
        super().__init__(dataframe)
        self.column_name = column_name

    def scale_column(self, factor: float) -> pd.DataFrame:
        """
        Scales the integer column by the given factor.

        Args:
            factor (float): The scaling factor.

        Returns:
            pd.DataFrame: The DataFrame with the scaled column.
        """
        self.dataframe[self.column_name] = self.dataframe[self.column_name] * factor
        return self.dataframe
    
    def offset_column(self, offset_value: float) -> pd.DataFrame:
        """
        Offsets the integer column by the given value.

        Args:
            offset_value (float): The value to add (positive) or subtract (negative) from each element in the column.

        Returns:
            pd.DataFrame: The DataFrame with the offset column.
        """
        self.dataframe[self.column_name] = self.dataframe[self.column_name] + offset_value
        return self.dataframe

    def divide_column(self, divisor: float) -> pd.DataFrame:
        """
        Divides each value in the integer column by the given divisor.

        Args:
            divisor (float): The value by which to divide each element.

        Returns:
            pd.DataFrame: The DataFrame with the divided column.
        """
        self.dataframe[self.column_name] = self.dataframe[self.column_name] / divisor
        return self.dataframe

    def subtract_column(self, subtract_value: float) -> pd.DataFrame:
        """
        Subtracts a given value from each element in the integer column.

        Args:
            subtract_value (float): The value to subtract from each element.

        Returns:
            pd.DataFrame: The DataFrame with the subtracted column.
        """
        self.dataframe[self.column_name] = self.dataframe[self.column_name] - subtract_value
        return self.dataframe
    
    def calculate_with_fixed_factors(self, multiply_factor: float = 1, add_factor: float = 0) -> pd.DataFrame:
        """
        Performs a calculation by multiplying with a factor and then adding an additional factor.

        Args:
            multiply_factor (float): The factor to multiply each value by. Defaults to 1 (no scaling).
            add_factor (float): The value to add after multiplication. Defaults to 0 (no offset).

        Returns:
            pd.DataFrame: The DataFrame after applying the calculations.
        """
        self.dataframe[self.column_name] = (self.dataframe[self.column_name] * multiply_factor) + add_factor
        return self.dataframe

    def mod_column(self, mod_value: int) -> pd.DataFrame:
        """
        Performs a modulus operation on the integer column with a specified value.

        Args:
            mod_value (int): The value to perform the modulus operation with.

        Returns:
            pd.DataFrame: The DataFrame with the modulus operation applied.
        """
        self.dataframe[self.column_name] = self.dataframe[self.column_name] % mod_value
        return self.dataframe
    
    def power_column(self, power_value: float) -> pd.DataFrame:
        """
        Raises each value in the integer column to the power of a specified value.

        Args:
            power_value (float): The exponent to raise each element to.

        Returns:
            pd.DataFrame: The DataFrame with the power operation applied.
        """
        self.dataframe[self.column_name] = self.dataframe[self.column_name] ** power_value
        return self.dataframe