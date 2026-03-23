import pytest
import pandas as pd
import numpy as np
from ts_shape.features.metric_pattern_analysis import MetricPatternAnalysis


@pytest.fixture
def multi_uuid_df():
    """DataFrame with 4 UUIDs: A and B similar (sine), C different (high freq), D constant."""
    np.random.seed(42)
    n = 200
    times = pd.date_range('2024-01-01', periods=n, freq='1s')

    # A and B: similar sine waves
    a_vals = np.sin(np.linspace(0, 4 * np.pi, n)) + np.random.randn(n) * 0.05
    b_vals = np.sin(np.linspace(0, 4 * np.pi, n)) + np.random.randn(n) * 0.05 + 0.1

    # C: high frequency sine
    c_vals = np.sin(np.linspace(0, 20 * np.pi, n)) * 3.0

    # D: constant with slight noise
    d_vals = np.full(n, 5.0) + np.random.randn(n) * 0.01

    frames = []
    for uuid_val, vals in [('A', a_vals), ('B', b_vals), ('C', c_vals), ('D', d_vals)]:
        frames.append(pd.DataFrame({
            'systime': times,
            'uuid': uuid_val,
            'value_double': vals,
        }))
    return pd.concat(frames, ignore_index=True)


@pytest.fixture
def windowed_df():
    """Longer DataFrame for testing time-windowed analysis."""
    np.random.seed(42)
    n = 600  # 10 minutes at 1s
    times = pd.date_range('2024-01-01', periods=n, freq='1s')

    # UUID X: sine that changes to large constant midway (strong regime change)
    x_vals = np.concatenate([
        np.sin(np.linspace(0, 4 * np.pi, n // 2)),
        np.full(n // 2, 10.0) + np.random.randn(n // 2) * 0.01,
    ])

    # UUID Y: stable sine throughout
    y_vals = np.sin(np.linspace(0, 8 * np.pi, n))

    frames = []
    for uuid_val, vals in [('X', x_vals), ('Y', y_vals)]:
        frames.append(pd.DataFrame({
            'systime': times,
            'uuid': uuid_val,
            'value_double': vals,
        }))
    return pd.concat(frames, ignore_index=True)


class TestComputeMetricProfiles:
    def test_no_window(self, multi_uuid_df):
        result = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        assert len(result) == 4  # one row per UUID
        assert 'uuid' in result.columns
        assert 'mean' in result.columns
        assert 'std' in result.columns

    def test_with_window(self, windowed_df):
        result = MetricPatternAnalysis.compute_metric_profiles(windowed_df, window='2min')
        assert len(result) > 2  # multiple windows per UUID
        assert 'window_start' in result.columns
        assert 'window_end' in result.columns

    def test_metrics_subset(self, multi_uuid_df):
        result = MetricPatternAnalysis.compute_metric_profiles(
            multi_uuid_df, metrics=['mean', 'std', 'min', 'max']
        )
        metric_cols = [c for c in result.columns if c not in ('uuid', 'window_start', 'window_end')]
        assert set(metric_cols) == {'mean', 'std', 'min', 'max'}

    def test_invalid_metric_raises(self, multi_uuid_df):
        with pytest.raises(ValueError, match="Unknown metrics"):
            MetricPatternAnalysis.compute_metric_profiles(
                multi_uuid_df, metrics=['mean', 'nonexistent']
            )

    def test_correct_values(self):
        """Verify metric values for a simple known case."""
        df = pd.DataFrame({
            'systime': pd.date_range('2024-01-01', periods=5, freq='1s'),
            'uuid': ['A'] * 5,
            'value_double': [1.0, 2.0, 3.0, 4.0, 5.0],
        })
        result = MetricPatternAnalysis.compute_metric_profiles(df, metrics=['mean', 'min', 'max'])
        row = result.iloc[0]
        assert row['mean'] == 3.0
        assert row['min'] == 1.0
        assert row['max'] == 5.0


class TestComputeDistanceMatrix:
    def test_symmetry(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        np.testing.assert_array_almost_equal(dm.values, dm.values.T)

    def test_zero_diagonal(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        np.testing.assert_array_almost_equal(np.diag(dm.values), 0.0)

    def test_similar_uuids_closer(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        # A and B should be closer to each other than A to C or A to D
        assert dm.loc['A', 'B'] < dm.loc['A', 'C']
        assert dm.loc['A', 'B'] < dm.loc['A', 'D']

    def test_distance_metrics(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        for metric in ['euclidean', 'cosine', 'manhattan']:
            dm = MetricPatternAnalysis.compute_distance_matrix(profiles, distance_metric=metric)
            assert dm.shape == (4, 4)

    def test_invalid_metric_raises(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        with pytest.raises(ValueError):
            MetricPatternAnalysis.compute_distance_matrix(profiles, distance_metric='invalid')


class TestClusterUuids:
    def test_n_clusters(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        clusters = MetricPatternAnalysis.cluster_uuids(dm, n_clusters=2)
        assert len(clusters) == 4
        assert 'cluster' in clusters.columns
        assert clusters['cluster'].nunique() <= 2

    def test_similar_uuids_same_cluster(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        clusters = MetricPatternAnalysis.cluster_uuids(dm, n_clusters=3)
        a_cluster = clusters.loc[clusters['uuid'] == 'A', 'cluster'].values[0]
        b_cluster = clusters.loc[clusters['uuid'] == 'B', 'cluster'].values[0]
        assert a_cluster == b_cluster

    def test_distance_threshold(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        clusters = MetricPatternAnalysis.cluster_uuids(dm, distance_threshold=0.5)
        assert len(clusters) == 4
        assert clusters['cluster'].nunique() >= 1


class TestFindSimilarUuids:
    def test_top_k(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        result = MetricPatternAnalysis.find_similar_uuids(dm, target_uuid='A', top_k=2)
        assert len(result) == 2
        assert 'rank' in result.columns

    def test_most_similar_is_b(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        result = MetricPatternAnalysis.find_similar_uuids(dm, target_uuid='A', top_k=1)
        assert result.iloc[0]['uuid'] == 'B'

    def test_invalid_uuid_raises(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        with pytest.raises(ValueError):
            MetricPatternAnalysis.find_similar_uuids(dm, target_uuid='NONEXISTENT')

    def test_distances_sorted(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        result = MetricPatternAnalysis.find_similar_uuids(dm, target_uuid='A', top_k=3)
        assert list(result['distance']) == sorted(result['distance'])


class TestDetectAnomalousUuids:
    def test_output_columns(self, multi_uuid_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        result = MetricPatternAnalysis.detect_anomalous_uuids(dm)
        assert 'anomaly_score' in result.columns
        assert 'z_score' in result.columns
        assert 'is_anomalous' in result.columns

    def test_constant_uuid_anomalous(self, multi_uuid_df):
        """The constant UUID D should have a high anomaly score."""
        profiles = MetricPatternAnalysis.compute_metric_profiles(multi_uuid_df)
        dm = MetricPatternAnalysis.compute_distance_matrix(profiles)
        result = MetricPatternAnalysis.detect_anomalous_uuids(dm, threshold=1.0)
        d_score = result.loc[result['uuid'] == 'D', 'anomaly_score'].values[0]
        a_score = result.loc[result['uuid'] == 'A', 'anomaly_score'].values[0]
        # D (constant) should be more anomalous than A (similar to B)
        assert d_score > a_score


class TestDetectBehaviorChanges:
    def test_regime_change_detected(self, windowed_df):
        # Use scale-invariant metrics to compare behavior changes
        profiles = MetricPatternAnalysis.compute_metric_profiles(
            windowed_df, window='2min', metrics=['mean', 'std', 'min', 'max']
        )
        result = MetricPatternAnalysis.detect_behavior_changes(
            profiles, normalize=False, metric_columns=['mean', 'std', 'min', 'max']
        )
        assert len(result) > 0
        assert 'change_score' in result.columns

        # UUID X has a regime change (sine -> constant 10.0);
        # its max change_score should be higher than Y's (stable sine)
        x_max = result.loc[result['uuid'] == 'X', 'change_score'].max()
        y_max = result.loc[result['uuid'] == 'Y', 'change_score'].max()
        assert x_max > y_max

    def test_empty_without_windows(self):
        """Without multiple windows, there are no behavior changes to detect."""
        df = pd.DataFrame({
            'systime': pd.date_range('2024-01-01', periods=10, freq='1s'),
            'uuid': ['A'] * 10,
            'value_double': range(10),
        })
        profiles = MetricPatternAnalysis.compute_metric_profiles(df)
        result = MetricPatternAnalysis.detect_behavior_changes(profiles)
        assert len(result) == 0


class TestFindSimilarWindows:
    def test_output_columns(self, windowed_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(windowed_df, window='2min')
        result = MetricPatternAnalysis.find_similar_windows(profiles, top_k=3)
        assert 'uuid_a' in result.columns
        assert 'window_a' in result.columns
        assert 'uuid_b' in result.columns
        assert 'distance' in result.columns
        assert 'rank' in result.columns

    def test_top_k_respected(self, windowed_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(windowed_df, window='2min')
        result = MetricPatternAnalysis.find_similar_windows(profiles, top_k=2)
        assert len(result) == 2

    def test_distances_sorted(self, windowed_df):
        profiles = MetricPatternAnalysis.compute_metric_profiles(windowed_df, window='2min')
        result = MetricPatternAnalysis.find_similar_windows(profiles, top_k=5)
        assert list(result['distance']) == sorted(result['distance'])
