from ..base import Base

class IntegerFilters(Base):
    """
    
    """
    def filter_value_integer_match(self, integer_value):
        """Filters rows where 'value_integer' matches the specified integer."""
        return self.dataframe[self.dataframe['value_integer'] == integer_value]

    def filter_value_integer_not_match(self, integer_value):
        """Filters rows where 'value_integer' does not match the specified integer."""
        return self.dataframe[self.dataframe['value_integer'] != integer_value]

class DoubleFilters(Base):
    """
    
    """
    def filter_nan_value_double(self):
        """Filters out rows where 'value_double' is NaN."""
        return self.dataframe[self.dataframe['value_double'].notna()]