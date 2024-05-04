import pandas as pd

class Base:
    def __init__(self, dataframe):
        """
        Initializes the Base with a DataFrame.
        Args:
        - dataframe (pd.DataFrame): The DataFrame to be processed.
        """
        self.dataframe = dataframe.sort_values(by='systime')