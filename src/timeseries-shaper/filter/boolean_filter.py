from ..base import Base

class BooleanFilters(Base):
    """
    
    """
    def filter_is_delta_true(self):
        """Filters rows where 'is_delta' is True."""
        if 'is_delta' not in self.dataframe.columns:
            raise ValueError("The column 'is_delta' does not exist in the DataFrame")
        return self.dataframe[self.dataframe['is_delta'] == True]

    def filter_is_delta_false(self):
        """Filters rows where 'is_delta' is False."""
        if 'is_delta' not in self.dataframe.columns:
            raise ValueError("The column 'is_delta' does not exist in the DataFrame")
        return self.dataframe[self.dataframe['is_delta'] == False]
    
    def filter_falling_value_bool(self):
        """Filters rows where 'value_bool' changes from True to False."""
        self.dataframe['previous_value_bool'] = self.dataframe['value_bool'].shift(1)
        return self.dataframe[(self.dataframe['previous_value_bool'] == True) & (self.dataframe['value_bool'] == False)]

    def filter_raising_value_bool(self):
        """Filters rows where 'value_bool' changes from False to True."""
        self.dataframe['previous_value_bool'] = self.dataframe['value_bool'].shift(1)
        return self.dataframe[(self.dataframe['previous_value_bool'] == False) & (self.dataframe['value_bool'] == True)]