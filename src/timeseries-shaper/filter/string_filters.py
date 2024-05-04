from ..base import Base

class StringFilters(Base):
    """
    
    """
    def filter_na_value_string(self):
        """Filters out rows where 'value_string' is NA."""
        return self.dataframe[self.dataframe['value_string'].notna()]

    def filter_value_string_match(self, string_value):
        """Filters rows where 'value_string' matches the specified string."""
        return self.dataframe[self.dataframe['value_string'] == string_value]

    def filter_value_string_not_match(self, string_value):
        """Filters rows where 'value_string' does not match the specified string."""
        return self.dataframe[self.dataframe['value_string'] != string_value]

    def filter_string_contains(self, substring):
        """Filters rows where 'value_string' contains the specified substring."""
        return self.dataframe[self.dataframe['value_string'].str.contains(substring, na=False)]

    def regex_clean_value_string(self, regex_pattern=r'(\d+)\s*([a-zA-Z]*)', replacement='', regex=True):
        """Applies a regex pattern to split the 'value_string' column into components."""
        self.dataframe['value_string'] = self.dataframe['value_string'].str.replace(regex_pattern, replacement, regex=regex)
        return self.dataframe

    def detect_changes_in_string(self):
        """Detects changes from row to row in the 'value_string' column."""
        changes_detected = self.dataframe['value_string'].ne(self.dataframe['value_string'].shift())
        self.dataframe = self.dataframe[changes_detected]
        if self.dataframe.empty:
            print("No changes detected in the 'value_string' column between consecutive rows.")
        return self.dataframe