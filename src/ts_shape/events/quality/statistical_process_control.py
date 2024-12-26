import pandas as pd  # type: ignore
import numpy as np
from typing import Callable, List, Optional
from ts_shape.utils.base import Base

class StatisticalProcessControlRuleBased(Base):
    """
    Inherits from Base and applies SPC rules (Western Electric Rules) to a DataFrame for event detection.
    Processes data based on control limit UUIDs, actual value UUIDs, and generates events with an event UUID.
    """

    def __init__(self, dataframe: pd.DataFrame, value_column: str, tolerance_uuid: str, actual_uuid: str, event_uuid: str) -> None:
        """
        Initializes the SPCMonitor with UUIDs for tolerance, actual, and event values.
        Inherits the sorted dataframe from the Base class.
        
        Args:
            dataframe (pd.DataFrame): The input DataFrame containing the data to be processed.
            value_column (str): The column containing the values to monitor.
            tolerance_uuid (str): UUID identifier for rows that set tolerance values.
            actual_uuid (str): UUID identifier for rows containing actual values.
            event_uuid (str): UUID to assign to generated events.
        """
        super().__init__(dataframe)  # Initialize the Base class
        self.value_column: str = value_column
        self.tolerance_uuid: str = tolerance_uuid
        self.actual_uuid: str = actual_uuid
        self.event_uuid: str = event_uuid
    
    def calculate_control_limits(self) -> pd.DataFrame:
        """
        Calculate the control limits (mean ± 1σ, 2σ, 3σ) for the tolerance values.
        
        Returns:
            pd.DataFrame: DataFrame with control limits for each tolerance group.
        """
        df = self.dataframe[self.dataframe['uuid'] == self.tolerance_uuid]
        mean = df[self.value_column].mean()
        sigma = df[self.value_column].std()
        
        control_limits = {
            'mean': mean,
            '1sigma_upper': mean + sigma,
            '1sigma_lower': mean - sigma,
            '2sigma_upper': mean + 2 * sigma,
            '2sigma_lower': mean - 2 * sigma,
            '3sigma_upper': mean + 3 * sigma,
            '3sigma_lower': mean - 3 * sigma,
        }
        
        return pd.DataFrame([control_limits])
    
    def rule_1(self, df: pd.DataFrame, limits: pd.DataFrame) -> pd.DataFrame:
        """
        Rule 1: One point beyond the 3σ control limits.
        
        Returns:
            pd.DataFrame: Filtered DataFrame with rule violations.
        """
        df['rule_1'] = (df[self.value_column] > limits['3sigma_upper'].values[0]) | (df[self.value_column] < limits['3sigma_lower'].values[0])
        return df[df['rule_1']]

    def rule_2(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rule 2: Nine consecutive points on one side of the mean.
        
        Returns:
            pd.DataFrame: Filtered DataFrame with rule violations.
        """
        mean = df[self.value_column].mean()
        df['above_mean'] = df[self.value_column] > mean
        df['below_mean'] = df[self.value_column] < mean
        df['rule_2'] = (df['above_mean'].rolling(window=9).sum() == 9) | (df['below_mean'].rolling(window=9).sum() == 9)
        return df[df['rule_2']]

    def rule_3(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rule 3: Six consecutive points steadily increasing or decreasing.
        
        Returns:
            pd.DataFrame: Filtered DataFrame with rule violations.
        """
        df['increasing'] = df[self.value_column].diff().gt(0)
        df['decreasing'] = df[self.value_column].diff().lt(0)
        df['rule_3'] = (df['increasing'].rolling(window=6).sum() == 6) | (df['decreasing'].rolling(window=6).sum() == 6)
        return df[df['rule_3']]

    def rule_4(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rule 4: Fourteen consecutive points alternating up and down.
        
        Returns:
            pd.DataFrame: Filtered DataFrame with rule violations.
        """
        df['alternating'] = df[self.value_column].diff().apply(np.sign)
        df['rule_4'] = df['alternating'].rolling(window=14).apply(lambda x: (x != x.shift()).sum() == 13, raw=True)
        return df[df['rule_4']]

    def rule_5(self, df: pd.DataFrame, limits: pd.DataFrame) -> pd.DataFrame:
        """
        Rule 5: Two out of three consecutive points near the control limit (beyond 2σ but within 3σ).
        
        Returns:
            pd.DataFrame: Filtered DataFrame with rule violations.
        """
        df['rule_5'] = df[self.value_column].apply(
            lambda x: 1 if ((x > limits['2sigma_upper'].values[0] and x < limits['3sigma_upper'].values[0]) or 
                            (x < limits['2sigma_lower'].values[0] and x > limits['3sigma_lower'].values[0])) else 0
        )
        df['rule_5'] = df['rule_5'].rolling(window=3).sum() >= 2
        return df[df['rule_5']]

    def rule_6(self, df: pd.DataFrame, limits: pd.DataFrame) -> pd.DataFrame:
        """
        Rule 6: Four out of five consecutive points near the control limit (beyond 1σ but within 2σ).
        
        Returns:
            pd.DataFrame: Filtered DataFrame with rule violations.
        """
        df['rule_6'] = df[self.value_column].apply(
            lambda x: 1 if ((x > limits['1sigma_upper'].values[0] and x < limits['2sigma_upper'].values[0]) or 
                            (x < limits['1sigma_lower'].values[0] and x > limits['2sigma_lower'].values[0])) else 0
        )
        df['rule_6'] = df['rule_6'].rolling(window=5).sum() >= 4
        return df[df['rule_6']]

    def rule_7(self, df: pd.DataFrame, limits: pd.DataFrame) -> pd.DataFrame:
        """
        Rule 7: Fifteen consecutive points within 1σ of the centerline.
        
        Returns:
            pd.DataFrame: Filtered DataFrame with rule violations.
        """
        df['rule_7'] = df[self.value_column].apply(
            lambda x: 1 if (x < limits['1sigma_upper'].values[0] and x > limits['1sigma_lower'].values[0]) else 0
        )
        df['rule_7'] = df['rule_7'].rolling(window=15).sum() == 15
        return df[df['rule_7']]

    def rule_8(self, df: pd.DataFrame, limits: pd.DataFrame) -> pd.DataFrame:
        """
        Rule 8: Eight consecutive points on both sides of the mean within 1σ.
        
        Returns:
            pd.DataFrame: Filtered DataFrame with rule violations.
        """
        df['rule_8'] = df[self.value_column].apply(
            lambda x: 1 if (x < limits['1sigma_upper'].values[0] and x > limits['1sigma_lower'].values[0]) else 0
        )
        df['rule_8'] = df['rule_8'].rolling(window=8).sum() == 8
        return df[df['rule_8']]

    def process(self, selected_rules: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Applies the selected SPC rules and generates a DataFrame of events where any rules are violated.
        
        Args:
            selected_rules (Optional[List[str]]): List of rule names (e.g., ['rule_1', 'rule_3']) to apply.
        
        Returns:
            pd.DataFrame: DataFrame with rule violations and detected events.
        """
        df = self.dataframe[self.dataframe['uuid'] == self.actual_uuid]
        df['systime'] = pd.to_datetime(df['systime'])
        df = df.sort_values(by='systime')

        limits = self.calculate_control_limits()

        # Dictionary of rule functions
        rules = {
            'rule_1': lambda df: self.rule_1(df, limits),
            'rule_2': lambda df: self.rule_2(df),
            'rule_3': lambda df: self.rule_3(df),
            'rule_4': lambda df: self.rule_4(df),
            'rule_5': lambda df: self.rule_5(df, limits),
            'rule_6': lambda df: self.rule_6(df, limits),
            'rule_7': lambda df: self.rule_7(df, limits),
            'rule_8': lambda df: self.rule_8(df, limits)
        }

        # If no specific rules are provided, use all rules
        if selected_rules is None:
            selected_rules = list(rules.keys())

        # Apply selected rules and concatenate results
        events = pd.concat([rules[rule](df) for rule in selected_rules if rule in rules]).drop_duplicates()

        # Add the event UUID to the detected events
        events['uuid'] = self.event_uuid

        return events[['systime', self.value_column, 'uuid']].drop_duplicates()