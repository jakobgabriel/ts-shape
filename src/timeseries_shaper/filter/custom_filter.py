from ..base import Base

class CustomFilter(Base):
    def filter_custom_conditions(self, conditions):
        """
        Filters the DataFrame based on a set of user-defined conditions passed as a string.

        This method allows for flexible data filtering by evaluating a condition or multiple conditions
        specified in the 'conditions' parameter. The conditions must be provided as a string
        that can be interpreted by pandas' DataFrame.query() method.

        Args:
        - conditions (str): A string representing the conditions to filter the DataFrame.
                                                The string should be formatted according to pandas query syntax.

        Returns:
        - pd.DataFrame: A DataFrame containing only the rows that meet the specified conditions.

        Example:
        --------
        # Given a DataFrame 'df' initialized with CustomFilter and containing columns 'age' and 'score':
        >>> sf = CustomFilter(df)
        >>> # To filter rows where 'age' is greater than 30 and 'score' is above 80
        >>> filtered_data = sf.filter_custom_conditions("age > 30 and score > 80")
        >>> print(filtered_data)

        Note:
        - Ensure that the column names and values used in conditions match those in the DataFrame.
        - Complex expressions and functions available in pandas query syntax can also be used.
        """
        return self.dataframe.query(conditions)