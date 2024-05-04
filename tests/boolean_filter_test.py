import pandas as pd
import pytest
from timeseries_shaper.filter.boolean_filter import IsDeltaFilter, BooleanFilter

def test_is_delta_true():
    # Ensure to include the 'systime' column in the test DataFrame
    data = {'is_delta': [True, False, True, False, True], 'systime': pd.date_range(start='1/1/2022', periods=5, freq='T')}
    df = pd.DataFrame(data)
    
    filter = IsDeltaFilter(df)
    result = filter.filter_is_delta_true()
    
    assert len(result) == 3
    assert all(result['is_delta'])

def test_is_delta_false():
    data = {'is_delta': [True, False, True, False, True], 'systime': pd.date_range(start='1/1/2022', periods=5, freq='T')}
    df = pd.DataFrame(data)
    filter = IsDeltaFilter(df)
    result = filter.filter_is_delta_false()
    
    assert len(result) == 2
    assert not any(result['is_delta'])

def test_boolean_filter_falling():
    data = {'value_bool': [True, True, False, True, False], 'systime': pd.date_range(start='1/1/2022', periods=5, freq='T')}
    df = pd.DataFrame(data)
    filter = BooleanFilter(df)
    result = filter.filter_falling_value_bool()
    
    assert len(result) == 2
    assert not result['value_bool'].iloc[0]
    assert not result['value_bool'].iloc[1]

def test_boolean_filter_raising():
    data = {'value_bool': [False, True, False, True, False], 'systime': pd.date_range(start='1/1/2022', periods=5, freq='T')}
    df = pd.DataFrame(data)
    filter = BooleanFilter(df)
    result = filter.filter_raising_value_bool()
    
    assert len(result) == 2
    assert result['value_bool'].iloc[0]
    assert result['value_bool'].iloc[1]