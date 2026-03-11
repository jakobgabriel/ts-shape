import logging
import pandas as pd  # type: ignore

logger = logging.getLogger(__name__)

class Base:
    @staticmethod
    def _validate_column(dataframe: pd.DataFrame, column_name: str) -> None:
        """Validate that a column exists in the DataFrame.

        Raises:
            ValueError: If column_name is not in dataframe.columns.
        """
        if column_name not in dataframe.columns:
            raise ValueError(
                f"Column '{column_name}' not found. "
                f"Available columns: {list(dataframe.columns)}"
            )

    def __init__(self, dataframe: pd.DataFrame, column_name: str = 'systime') -> None:
        """
        Initializes the Base with a DataFrame, detects time columns, converts them to datetime,
        and sorts the DataFrame by the specified column (or the detected time column if applicable).

        Args:
            dataframe (pd.DataFrame): The DataFrame to be processed.
            column_name (str): The column to sort by. Default is 'systime'. If the column is not found or is not a time column, the class will attempt to detect other time columns.

        Raises:
            TypeError: If dataframe is not a pandas DataFrame.
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame, got {type(dataframe).__name__}")
        self.dataframe = dataframe.copy()
        if self.dataframe.empty:
            return
        
        # Attempt to convert the specified column_name to datetime if it exists
        if column_name in self.dataframe.columns:
            self.dataframe[column_name] = pd.to_datetime(self.dataframe[column_name], errors='coerce')
        else:
            # If the column_name is not in the DataFrame, fallback to automatic time detection
            time_columns = [col for col in self.dataframe.columns if 'time' in col.lower() or 'date' in col.lower()]
            
            # Convert all detected time columns to datetime, if any
            for col in time_columns:
                self.dataframe[col] = pd.to_datetime(self.dataframe[col], errors='coerce')
            
            # If any time columns are detected, sort by the first one; otherwise, do nothing
            if time_columns:
                column_name = time_columns[0]
        
        # Sort by the datetime column (either specified or detected)
        if column_name in self.dataframe.columns:
            self.dataframe = self.dataframe.sort_values(by=column_name)
    
    def get_dataframe(self) -> pd.DataFrame:
        """Returns the processed DataFrame."""
        return self.dataframe
