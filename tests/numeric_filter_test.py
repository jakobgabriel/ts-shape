import pytest
import pandas as pd
from timeseries_shaper.filter.numeric_filter import IntegerFilter, DoubleFilter

# Test class for IntegerFilter
class TestIntegerFilter:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup a sample DataFrame and IntegerFilter object for each test
        self.df = pd.DataFrame({
            'value_integer': [10, 20, 30, 40, 50],
            'systime': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'])
        })
        self.integer_filter = IntegerFilter(self.df)

    def test_filter_value_integer_match(self):
        # Test the filter_value_integer_match method
        result = self.integer_filter.filter_value_integer_match(30)
        expected = pd.DataFrame({'value_integer': [30], 'systime': ['2023-01-03']}, index=[2])
        expected['systime'] = pd.to_datetime(expected['systime'])
        pd.testing.assert_frame_equal(result, expected)

    def test_filter_value_integer_not_match(self):
        # Test the filter_value_integer_not_match method
        result = self.integer_filter.filter_value_integer_not_match(30)
        expected = pd.DataFrame({
            'value_integer': [10, 20, 40, 50],
            'systime': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-04', '2023-01-05'])
        }, index=[0, 1, 3, 4])
        pd.testing.assert_frame_equal(result, expected)

    def test_filter_value_integer_between(self):
        # Test the filter_value_integer_between method
        result = self.integer_filter.filter_value_integer_between(20, 40)
        expected = pd.DataFrame({
            'value_integer': [20, 30, 40],
            'systime': pd.to_datetime(['2023-01-02', '2023-01-03', '2023-01-04'])
        }, index=[1, 2, 3])
        pd.testing.assert_frame_equal(result, expected)

# Test class for DoubleFilter
class TestDoubleFilter:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        # Setup a sample DataFrame and DoubleFilter object for each test
        self.df = pd.DataFrame({
            'value_double': [0.5, 1.5, float('nan'), 2.5, 3.5],
            'systime': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'])
        })
        self.double_filter = DoubleFilter(self.df)

    def test_filter_nan_value_double(self):
        # Test the filter_nan_value_double method
        result = self.double_filter.filter_nan_value_double()
        expected = pd.DataFrame({
            'value_double': [0.5, 1.5, 2.5, 3.5],
            'systime': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-04', '2023-01-05'])
        }, index=[0, 1, 3, 4])
        pd.testing.assert_frame_equal(result, expected)

    def test_filter_value_double_between(self):
        # Test the filter_value_double_between method
        result = self.double_filter.filter_value_double_between(1.0, 3.0)
        expected = pd.DataFrame({
            'value_double': [1.5, 2.5],
            'systime': pd.to_datetime(['2023-01-02', '2023-01-04'])
        }, index=[1, 3])
        pd.testing.assert_frame_equal(result, expected)
