import logging
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from typing import Optional, List

from scipy.spatial.distance import pdist, squareform  # type: ignore
from scipy.cluster.hierarchy import linkage, fcluster  # type: ignore

from ts_shape.utils.base import Base
from ts_shape.features.stats.numeric_stats import NumericStatistics

logger = logging.getLogger(__name__)

ALL_METRICS = [
    'min', 'max', 'mean', 'median', 'std', 'var', 'sum',
    'kurtosis', 'skewness', 'q1', 'q3', 'iqr', 'range',
    'mad', 'coeff_var', 'sem', 'mode', 'percentile_90', 'percentile_10',
]


class MetricPatternAnalysis(Base):
    """Cross-UUID pattern recognition using metric profiles.

    Works on standard long-format DataFrames (systime, uuid, value_double, ...).
    Computes per-UUID, per-window statistical profiles and finds patterns
    across UUIDs: similarity clustering, anomalous UUID detection, and
    temporal behavior changes.

    Methods:
    - compute_metric_profiles: Compute statistical metrics per UUID per time window.
    - compute_distance_matrix: Pairwise distance matrix between UUID metric profiles.
    - cluster_uuids: Group UUIDs by metric similarity using hierarchical clustering.
    - find_similar_uuids: Find UUIDs most similar to a target.
    - detect_anomalous_uuids: Detect UUIDs with unusual metric profiles.
    - detect_behavior_changes: Track metric profile changes over time per UUID.
    - find_similar_windows: Find similar (UUID, window) pairs across all data.
    """

    @classmethod
    def compute_metric_profiles(
        cls,
        dataframe: pd.DataFrame,
        uuid_column: str = 'uuid',
        value_column: str = 'value_double',
        time_column: str = 'systime',
        window: Optional[str] = None,
        metrics: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Compute statistical metric profiles per UUID per time window.

        Args:
            dataframe: Input DataFrame in long format.
            uuid_column: Column identifying each timeseries.
            value_column: Column containing numeric values.
            time_column: Column containing timestamps.
            window: Pandas frequency string for time windows (e.g. '1h', '1D').
                None computes metrics over the entire range per UUID.
            metrics: Subset of metric names to compute. None uses all 19 metrics.

        Returns:
            DataFrame with columns [uuid, window_start, window_end, metric_1, ...].
        """
        cls._validate_column(dataframe, uuid_column)
        cls._validate_column(dataframe, value_column)

        if metrics is not None:
            invalid = set(metrics) - set(ALL_METRICS)
            if invalid:
                raise ValueError(f"Unknown metrics: {invalid}. Available: {ALL_METRICS}")

        rows = []

        for uuid_val, uuid_group in dataframe.groupby(uuid_column):
            if window is not None:
                cls._validate_column(dataframe, time_column)
                grouped = uuid_group.set_index(time_column).resample(window)
                for window_label, window_group in grouped:
                    window_group = window_group.reset_index()
                    if len(window_group) < 2 or window_group[value_column].isna().all():
                        continue
                    stats = NumericStatistics.summary_as_dict(window_group, value_column)
                    if metrics is not None:
                        stats = {k: v for k, v in stats.items() if k in metrics}
                    stats[uuid_column] = uuid_val
                    stats['window_start'] = window_label
                    stats['window_end'] = window_label + pd.tseries.frequencies.to_offset(window)
                    rows.append(stats)
            else:
                if len(uuid_group) < 2 or uuid_group[value_column].isna().all():
                    continue
                stats = NumericStatistics.summary_as_dict(uuid_group, value_column)
                if metrics is not None:
                    stats = {k: v for k, v in stats.items() if k in metrics}
                stats[uuid_column] = uuid_val
                if time_column in dataframe.columns:
                    stats['window_start'] = uuid_group[time_column].min()
                    stats['window_end'] = uuid_group[time_column].max()
                rows.append(stats)

        if not rows:
            return pd.DataFrame()

        result = pd.DataFrame(rows)
        # Reorder columns: uuid first, then window columns, then metrics
        leading = [uuid_column]
        if 'window_start' in result.columns:
            leading += ['window_start', 'window_end']
        metric_cols = [c for c in result.columns if c not in leading]
        return result[leading + metric_cols].reset_index(drop=True)

    @classmethod
    def _get_metric_columns(
        cls,
        df: pd.DataFrame,
        metric_columns: Optional[List[str]] = None,
    ) -> List[str]:
        """Identify metric columns from a metric profiles DataFrame."""
        non_metric = {'uuid', 'window_start', 'window_end'}
        available = [c for c in df.columns if c not in non_metric and pd.api.types.is_numeric_dtype(df[c])]
        if metric_columns is not None:
            missing = set(metric_columns) - set(available)
            if missing:
                raise ValueError(f"Columns not found or not numeric: {missing}")
            return metric_columns
        return available

    @classmethod
    def compute_distance_matrix(
        cls,
        metric_profiles: pd.DataFrame,
        uuid_column: str = 'uuid',
        metric_columns: Optional[List[str]] = None,
        distance_metric: str = 'euclidean',
        normalize: bool = True,
    ) -> pd.DataFrame:
        """Compute pairwise distance matrix between UUID metric profiles.

        If metric_profiles contains multiple windows per UUID, metrics are
        averaged across windows to produce one vector per UUID.

        Args:
            metric_profiles: Output from compute_metric_profiles.
            uuid_column: Column identifying each timeseries.
            metric_columns: Which metric columns to use. None auto-detects.
            distance_metric: 'euclidean', 'cosine', or 'manhattan'.
            normalize: Z-normalize metrics before computing distances.

        Returns:
            Square DataFrame indexed and columned by UUID with pairwise distances.
        """
        cols = cls._get_metric_columns(metric_profiles, metric_columns)

        # Aggregate to one vector per UUID
        agg = metric_profiles.groupby(uuid_column)[cols].mean()
        uuids = agg.index.tolist()
        matrix = agg.values.astype(float)

        # Handle NaN values
        matrix = np.nan_to_num(matrix, nan=0.0)

        if normalize and matrix.shape[0] > 1:
            col_std = matrix.std(axis=0)
            col_std[col_std < 1e-10] = 1.0
            matrix = (matrix - matrix.mean(axis=0)) / col_std

        metric_map = {'euclidean': 'euclidean', 'cosine': 'cosine', 'manhattan': 'cityblock'}
        if distance_metric not in metric_map:
            raise ValueError(f"Unknown distance_metric: {distance_metric}. Use 'euclidean', 'cosine', or 'manhattan'.")

        condensed = pdist(matrix, metric=metric_map[distance_metric])
        dist_matrix = squareform(condensed)

        return pd.DataFrame(dist_matrix, index=uuids, columns=uuids)

    @classmethod
    def cluster_uuids(
        cls,
        distance_matrix: pd.DataFrame,
        n_clusters: int = 3,
        distance_threshold: Optional[float] = None,
        linkage_method: str = 'average',
    ) -> pd.DataFrame:
        """Group UUIDs by metric similarity using hierarchical clustering.

        Args:
            distance_matrix: Square distance matrix from compute_distance_matrix.
            n_clusters: Number of clusters. Ignored if distance_threshold is set.
            distance_threshold: Cut the dendrogram at this distance. Overrides n_clusters.
            linkage_method: Linkage criterion: 'average', 'complete', 'single', 'ward'.
                Note: 'ward' requires euclidean distances.

        Returns:
            DataFrame with columns [uuid, cluster].
        """
        uuids = distance_matrix.index.tolist()
        condensed = squareform(distance_matrix.values, checks=False)

        Z = linkage(condensed, method=linkage_method)

        if distance_threshold is not None:
            labels = fcluster(Z, t=distance_threshold, criterion='distance')
        else:
            labels = fcluster(Z, t=n_clusters, criterion='maxclust')

        return pd.DataFrame({'uuid': uuids, 'cluster': labels.astype(int)})

    @classmethod
    def find_similar_uuids(
        cls,
        distance_matrix: pd.DataFrame,
        target_uuid: str,
        top_k: int = 5,
    ) -> pd.DataFrame:
        """Find UUIDs most similar to a target based on metric profiles.

        Args:
            distance_matrix: Square distance matrix from compute_distance_matrix.
            target_uuid: UUID to find similarities for.
            top_k: Number of similar UUIDs to return.

        Returns:
            DataFrame with columns [uuid, distance, rank] sorted by distance.
        """
        if target_uuid not in distance_matrix.index:
            raise ValueError(f"UUID '{target_uuid}' not found in distance matrix.")

        distances = distance_matrix.loc[target_uuid].drop(target_uuid)
        sorted_dists = distances.sort_values().head(top_k)

        return pd.DataFrame({
            'uuid': sorted_dists.index,
            'distance': sorted_dists.values,
            'rank': range(1, len(sorted_dists) + 1),
        }).reset_index(drop=True)

    @classmethod
    def detect_anomalous_uuids(
        cls,
        distance_matrix: pd.DataFrame,
        threshold: float = 2.0,
    ) -> pd.DataFrame:
        """Detect UUIDs with unusual metric profiles.

        Computes the mean distance from each UUID to all others. UUIDs with
        a z-score above the threshold are flagged as anomalous.

        Args:
            distance_matrix: Square distance matrix from compute_distance_matrix.
            threshold: Z-score threshold for anomaly detection.

        Returns:
            DataFrame with columns [uuid, anomaly_score, z_score, is_anomalous].
        """
        uuids = distance_matrix.index.tolist()
        n = len(uuids)

        # Mean distance to all other UUIDs
        mean_dists = distance_matrix.values.sum(axis=1) / max(n - 1, 1)

        global_mean = mean_dists.mean()
        global_std = mean_dists.std()
        if global_std < 1e-10:
            z_scores = np.zeros(n)
        else:
            z_scores = (mean_dists - global_mean) / global_std

        return pd.DataFrame({
            'uuid': uuids,
            'anomaly_score': mean_dists,
            'z_score': z_scores,
            'is_anomalous': z_scores > threshold,
        })

    @classmethod
    def detect_behavior_changes(
        cls,
        metric_profiles: pd.DataFrame,
        uuid_column: str = 'uuid',
        window_start_column: str = 'window_start',
        metric_columns: Optional[List[str]] = None,
        normalize: bool = True,
    ) -> pd.DataFrame:
        """Track how each UUID's metric profile changes between consecutive windows.

        Computes the Euclidean distance between consecutive window metric vectors
        for each UUID. Large change scores indicate regime changes.

        Args:
            metric_profiles: Output from compute_metric_profiles (must have windows).
            uuid_column: Column identifying each timeseries.
            window_start_column: Column with window start timestamps.
            metric_columns: Which metric columns to use. None auto-detects.
            normalize: Z-normalize metrics before computing change scores.

        Returns:
            DataFrame with columns [uuid, window_start, change_score].
        """
        cols = cls._get_metric_columns(metric_profiles, metric_columns)

        rows = []
        for uuid_val, group in metric_profiles.groupby(uuid_column):
            group = group.sort_values(window_start_column)
            matrix = group[cols].values.astype(float)
            matrix = np.nan_to_num(matrix, nan=0.0)

            if normalize and matrix.shape[0] > 1:
                col_std = matrix.std(axis=0)
                col_std[col_std < 1e-10] = 1.0
                matrix = (matrix - matrix.mean(axis=0)) / col_std

            windows = group[window_start_column].values
            for i in range(1, len(matrix)):
                dist = float(np.linalg.norm(matrix[i] - matrix[i - 1]))
                rows.append({
                    uuid_column: uuid_val,
                    window_start_column: windows[i],
                    'change_score': dist,
                })

        if not rows:
            return pd.DataFrame(columns=[uuid_column, window_start_column, 'change_score'])

        return pd.DataFrame(rows).reset_index(drop=True)

    @classmethod
    def find_similar_windows(
        cls,
        metric_profiles: pd.DataFrame,
        uuid_column: str = 'uuid',
        window_start_column: str = 'window_start',
        metric_columns: Optional[List[str]] = None,
        normalize: bool = True,
        top_k: int = 10,
    ) -> pd.DataFrame:
        """Find the most similar (UUID, window) pairs across all data.

        Args:
            metric_profiles: Output from compute_metric_profiles (must have windows).
            uuid_column: Column identifying each timeseries.
            window_start_column: Column with window start timestamps.
            metric_columns: Which metric columns to use. None auto-detects.
            normalize: Z-normalize metrics before computing distances.
            top_k: Number of closest pairs to return.

        Returns:
            DataFrame with columns [uuid_a, window_a, uuid_b, window_b, distance, rank].
        """
        cols = cls._get_metric_columns(metric_profiles, metric_columns)

        matrix = metric_profiles[cols].values.astype(float)
        matrix = np.nan_to_num(matrix, nan=0.0)

        if normalize and matrix.shape[0] > 1:
            col_std = matrix.std(axis=0)
            col_std[col_std < 1e-10] = 1.0
            matrix = (matrix - matrix.mean(axis=0)) / col_std

        uuids = metric_profiles[uuid_column].values
        windows = metric_profiles[window_start_column].values

        condensed = pdist(matrix, metric='euclidean')
        n = len(matrix)

        # Find top_k smallest distances
        if len(condensed) <= top_k:
            sorted_indices = np.argsort(condensed)
        else:
            sorted_indices = np.argpartition(condensed, top_k)[:top_k]
            sorted_indices = sorted_indices[np.argsort(condensed[sorted_indices])]

        rows = []
        for rank, idx in enumerate(sorted_indices, 1):
            # Convert condensed index to (i, j)
            i, j = cls._condensed_to_square(idx, n)
            rows.append({
                'uuid_a': uuids[i],
                'window_a': windows[i],
                'uuid_b': uuids[j],
                'window_b': windows[j],
                'distance': float(condensed[idx]),
                'rank': rank,
            })

        return pd.DataFrame(rows)

    @staticmethod
    def _condensed_to_square(idx: int, n: int):
        """Convert a condensed distance matrix index to (row, col) pair."""
        # The condensed index k corresponds to (i, j) where i < j
        i = int(n - 2 - np.floor(np.sqrt(-8 * idx + 4 * n * (n - 1) - 7) / 2.0 - 0.5))
        j = int(idx + i + 1 - n * (n - 1) // 2 + (n - i) * ((n - i) - 1) // 2)
        return i, j
