import pytest
import pandas as pd
import numpy as np
from ts_shape.features.metric_pattern_analysis import MetricPatternAnalysis


@pytest.fixture
def production_df():
    """Simulate production data: an order signal + 3 process parameters.

    Order signal changes: Order-A (0-99s), Order-B (100-199s), Order-A again (200-299s).
    Process params: temperature (similar for A runs), pressure (different per order), speed (constant).
    """
    np.random.seed(42)
    n = 300
    times = pd.date_range('2024-01-01', periods=n, freq='1s')

    frames = []

    # Order signal (value_string)
    orders = ['Order-A'] * 100 + ['Order-B'] * 100 + ['Order-A'] * 100
    frames.append(pd.DataFrame({
        'systime': times,
        'uuid': 'order_number',
        'value_string': orders,
        'value_double': np.nan,
    }))

    # Temperature: ~50 for Order-A, ~80 for Order-B
    temp = np.concatenate([
        50 + np.random.randn(100) * 2,   # Order-A run 1
        80 + np.random.randn(100) * 2,   # Order-B
        50 + np.random.randn(100) * 2,   # Order-A run 2
    ])
    frames.append(pd.DataFrame({
        'systime': times,
        'uuid': 'temperature',
        'value_string': '',
        'value_double': temp,
    }))

    # Pressure: ~100 for Order-A, ~200 for Order-B
    pressure = np.concatenate([
        100 + np.random.randn(100) * 5,
        200 + np.random.randn(100) * 5,
        100 + np.random.randn(100) * 5,
    ])
    frames.append(pd.DataFrame({
        'systime': times,
        'uuid': 'pressure',
        'value_string': '',
        'value_double': pressure,
    }))

    # Speed: constant ~1000 regardless of order
    speed = 1000 + np.random.randn(n) * 1
    frames.append(pd.DataFrame({
        'systime': times,
        'uuid': 'speed',
        'value_string': '',
        'value_double': speed,
    }))

    return pd.concat(frames, ignore_index=True)


@pytest.fixture
def time_ranges(production_df):
    """Pre-extracted time ranges for convenience."""
    return MetricPatternAnalysis.extract_time_ranges(
        production_df, segment_uuid='order_number'
    )


@pytest.fixture
def segmented_df(production_df, time_ranges):
    """Production data filtered and annotated with segments."""
    return MetricPatternAnalysis.apply_ranges(
        production_df, time_ranges,
        target_uuids=['temperature', 'pressure', 'speed'],
    )


class TestExtractTimeRanges:
    def test_detects_all_segments(self, production_df):
        result = MetricPatternAnalysis.extract_time_ranges(
            production_df, segment_uuid='order_number'
        )
        assert len(result) == 3  # Order-A, Order-B, Order-A

    def test_correct_values(self, production_df):
        result = MetricPatternAnalysis.extract_time_ranges(
            production_df, segment_uuid='order_number'
        )
        assert result.iloc[0]['segment_value'] == 'Order-A'
        assert result.iloc[1]['segment_value'] == 'Order-B'
        assert result.iloc[2]['segment_value'] == 'Order-A'

    def test_correct_columns(self, production_df):
        result = MetricPatternAnalysis.extract_time_ranges(
            production_df, segment_uuid='order_number'
        )
        expected_cols = {'segment_value', 'segment_start', 'segment_end',
                         'segment_duration', 'segment_index'}
        assert set(result.columns) == expected_cols

    def test_sequential_indices(self, production_df):
        result = MetricPatternAnalysis.extract_time_ranges(
            production_df, segment_uuid='order_number'
        )
        assert list(result['segment_index']) == [0, 1, 2]

    def test_min_duration_filters(self, production_df):
        result = MetricPatternAnalysis.extract_time_ranges(
            production_df, segment_uuid='order_number',
            min_duration='200s',  # Only segments >= 200s survive (none, since each is ~99s)
        )
        assert len(result) == 0

    def test_empty_uuid(self, production_df):
        result = MetricPatternAnalysis.extract_time_ranges(
            production_df, segment_uuid='nonexistent'
        )
        assert len(result) == 0

    def test_integer_value_column(self):
        """Test with value_integer instead of value_string."""
        df = pd.DataFrame({
            'systime': pd.date_range('2024-01-01', periods=10, freq='1s'),
            'uuid': 'part_id',
            'value_integer': [1, 1, 1, 2, 2, 2, 2, 3, 3, 3],
        })
        result = MetricPatternAnalysis.extract_time_ranges(
            df, segment_uuid='part_id', value_column='value_integer'
        )
        assert len(result) == 3
        assert list(result['segment_value']) == [1, 2, 3]


class TestApplyRanges:
    def test_filters_to_target_uuids(self, production_df, time_ranges):
        result = MetricPatternAnalysis.apply_ranges(
            production_df, time_ranges,
            target_uuids=['temperature'],
        )
        assert result['uuid'].unique().tolist() == ['temperature']

    def test_annotates_segment_value(self, segmented_df):
        assert 'segment_value' in segmented_df.columns
        assert set(segmented_df['segment_value'].unique()) == {'Order-A', 'Order-B'}

    def test_annotates_segment_index(self, segmented_df):
        assert 'segment_index' in segmented_df.columns
        assert set(segmented_df['segment_index'].unique()) == {0, 1, 2}

    def test_all_uuids_present(self, segmented_df):
        assert set(segmented_df['uuid'].unique()) == {'temperature', 'pressure', 'speed'}

    def test_empty_ranges(self, production_df):
        empty_ranges = pd.DataFrame(columns=[
            'segment_value', 'segment_start', 'segment_end',
            'segment_duration', 'segment_index',
        ])
        result = MetricPatternAnalysis.apply_ranges(production_df, empty_ranges)
        assert len(result) == 0


class TestComputeMetricProfiles:
    def test_by_segment_value(self, segmented_df):
        result = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        # 3 UUIDs x 2 unique segment_values = 6 rows
        # (temperature x Order-A, temperature x Order-B, etc.)
        assert len(result) == 6
        assert 'mean' in result.columns
        assert 'std' in result.columns

    def test_by_segment_index(self, segmented_df):
        result = MetricPatternAnalysis.compute_metric_profiles(
            segmented_df, group_column='segment_index'
        )
        # 3 UUIDs x 3 segments = 9 rows
        assert len(result) == 9

    def test_metrics_subset(self, segmented_df):
        result = MetricPatternAnalysis.compute_metric_profiles(
            segmented_df, metrics=['mean', 'std']
        )
        metric_cols = [c for c in result.columns
                       if c not in ('uuid', 'segment_value', 'sample_count')]
        assert set(metric_cols) == {'mean', 'std'}

    def test_correct_mean_values(self, segmented_df):
        """Temperature mean should be ~50 for Order-A and ~80 for Order-B."""
        result = MetricPatternAnalysis.compute_metric_profiles(
            segmented_df, metrics=['mean']
        )
        temp_a = result[(result['uuid'] == 'temperature') &
                        (result['segment_value'] == 'Order-A')]['mean'].values
        temp_b = result[(result['uuid'] == 'temperature') &
                        (result['segment_value'] == 'Order-B')]['mean'].values
        # Order-A temperature should be around 50
        assert all(abs(v - 50) < 5 for v in temp_a)
        # Order-B temperature should be around 80
        assert all(abs(v - 80) < 5 for v in temp_b)

    def test_invalid_metric_raises(self, segmented_df):
        with pytest.raises(ValueError, match="Unknown metrics"):
            MetricPatternAnalysis.compute_metric_profiles(
                segmented_df, metrics=['nonexistent']
            )


class TestComputeDistanceMatrix:
    def test_compare_uuids(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles, group_column='uuid')
        assert dm.shape == (3, 3)
        np.testing.assert_array_almost_equal(np.diag(dm.values), 0.0)

    def test_compare_segments(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(
            profiles, group_column='segment_value'
        )
        assert dm.shape == (2, 2)  # Order-A vs Order-B

    def test_symmetry(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles, group_column='uuid')
        np.testing.assert_array_almost_equal(dm.values, dm.values.T)

    def test_distance_metrics(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        for metric in ['euclidean', 'cosine', 'manhattan']:
            dm = MetricPatternAnalysis.compute_distance_matrix(
                profiles, group_column='uuid', distance_metric=metric
            )
            assert dm.shape == (3, 3)

    def test_invalid_metric_raises(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        with pytest.raises(ValueError):
            MetricPatternAnalysis.compute_distance_matrix(
                profiles, group_column='uuid', distance_metric='invalid'
            )


class TestClusterUuids:
    def test_n_clusters(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles, group_column='uuid')
        clusters = MetricPatternAnalysis.cluster_uuids(dm, n_clusters=2)
        assert len(clusters) == 3
        assert clusters['cluster'].nunique() <= 2

    def test_distance_threshold(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles, group_column='uuid')
        clusters = MetricPatternAnalysis.cluster_uuids(dm, distance_threshold=0.5)
        assert len(clusters) == 3


class TestFindSimilarUuids:
    def test_basic(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles, group_column='uuid')
        result = MetricPatternAnalysis.find_similar_uuids(dm, target_uuid='temperature')
        assert len(result) == 2  # top_k=5 but only 2 others exist
        assert 'distance' in result.columns
        assert 'rank' in result.columns

    def test_invalid_uuid_raises(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles, group_column='uuid')
        with pytest.raises(ValueError):
            MetricPatternAnalysis.find_similar_uuids(dm, target_uuid='nonexistent')

    def test_sorted_by_distance(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles, group_column='uuid')
        result = MetricPatternAnalysis.find_similar_uuids(dm, target_uuid='temperature')
        assert list(result['distance']) == sorted(result['distance'])


class TestDetectAnomalousUuids:
    def test_output_columns(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles, group_column='uuid')
        result = MetricPatternAnalysis.detect_anomalous_uuids(dm)
        assert 'anomaly_score' in result.columns
        assert 'z_score' in result.columns
        assert 'is_anomalous' in result.columns
        assert len(result) == 3


class TestDetectBehaviorChanges:
    def test_by_segment_index(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(
            segmented_df, group_column='segment_index'
        )
        result = MetricPatternAnalysis.detect_behavior_changes(profiles)
        assert 'change_score' in result.columns
        assert len(result) > 0

    def test_temperature_changes_more_than_speed(self, segmented_df):
        """Temperature varies across orders; speed stays constant."""
        profiles = MetricPatternAnalysis.compute_metric_profiles(
            segmented_df, group_column='segment_index'
        )
        result = MetricPatternAnalysis.detect_behavior_changes(profiles)
        temp_max = result.loc[result['uuid'] == 'temperature', 'change_score'].max()
        speed_max = result.loc[result['uuid'] == 'speed', 'change_score'].max()
        assert temp_max > speed_max


class TestFindSimilarWindows:
    def test_output_columns(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        result = MetricPatternAnalysis.find_similar_windows(profiles, top_k=3)
        assert 'uuid_a' in result.columns
        assert 'group_a' in result.columns
        assert 'uuid_b' in result.columns
        assert 'distance' in result.columns
        assert 'rank' in result.columns

    def test_top_k_respected(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        result = MetricPatternAnalysis.find_similar_windows(profiles, top_k=2)
        assert len(result) == 2

    def test_distances_sorted(self, segmented_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented_df)
        result = MetricPatternAnalysis.find_similar_windows(profiles, top_k=5)
        assert list(result['distance']) == sorted(result['distance'])


class TestEndToEndWorkflow:
    def test_full_pipeline(self, production_df):
        """Test the complete workflow: extract → apply → profile → analyze."""
        # Step 1: Extract time ranges from order signal
        ranges = MetricPatternAnalysis.extract_time_ranges(
            production_df, segment_uuid='order_number'
        )
        assert len(ranges) == 3

        # Step 2: Apply ranges to process parameters
        segmented = MetricPatternAnalysis.apply_ranges(
            production_df, ranges,
            target_uuids=['temperature', 'pressure', 'speed'],
        )
        assert 'segment_value' in segmented.columns

        # Step 3: Compute metric profiles per UUID per order
        profiles = MetricPatternAnalysis.compute_metric_profiles(segmented)
        assert len(profiles) == 6  # 3 uuids × 2 order values

        # Step 4: Compare orders
        dm = MetricPatternAnalysis.compute_distance_matrix(
            profiles, group_column='segment_value'
        )
        assert dm.shape == (2, 2)
        assert dm.loc['Order-A', 'Order-B'] > 0

        # Step 5: Compare UUIDs
        uuid_dm = MetricPatternAnalysis.compute_distance_matrix(
            profiles, group_column='uuid'
        )
        assert uuid_dm.shape == (3, 3)

        # Step 6: Cluster UUIDs
        clusters = MetricPatternAnalysis.cluster_uuids(uuid_dm, n_clusters=2)
        assert len(clusters) == 3

    def test_per_segment_index_analysis(self, production_df):
        """Test analyzing individual runs (not aggregated by order value)."""
        ranges = MetricPatternAnalysis.extract_time_ranges(
            production_df, segment_uuid='order_number'
        )
        segmented = MetricPatternAnalysis.apply_ranges(
            production_df, ranges,
            target_uuids=['temperature', 'pressure'],
        )
        profiles = MetricPatternAnalysis.compute_metric_profiles(
            segmented, group_column='segment_index'
        )
        # 2 uuids × 3 segment indices = 6 rows
        assert len(profiles) == 6

        # Detect behavior changes across segments
        changes = MetricPatternAnalysis.detect_behavior_changes(profiles)
        assert len(changes) > 0
