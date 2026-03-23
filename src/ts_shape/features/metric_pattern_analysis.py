import logging
import pandas as pd  # type: ignore
import numpy as np  # type: ignore
from typing import Optional, List, Dict, Union

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
    """Pattern recognition across multiple timeseries (UUIDs) using metric profiles.

    Designed for production environments where a categorical signal (e.g. order
    number, part number) defines time ranges that should be applied to process
    parameter UUIDs for per-segment analysis.

    Workflow:
    1. extract_time_ranges: Detect when a categorical signal changes and extract
       time ranges per unique value (order, part number, etc.).
    2. apply_ranges: Filter other UUIDs' data using those time ranges.
    3. compute_metric_profiles: Compute statistical metrics per UUID per segment.
    4. Use distance/clustering/anomaly methods to compare segments and UUIDs.

    Methods:
    - extract_time_ranges: Extract time ranges from a categorical signal.
    - apply_ranges: Filter process parameter data by extracted time ranges.
    - compute_metric_profiles: Compute statistical metrics per UUID per segment.
    - compute_distance_matrix: Pairwise distance between metric profile vectors.
    - cluster_uuids: Group UUIDs by metric similarity (hierarchical clustering).
    - find_similar_uuids: Find UUIDs most similar to a target.
    - detect_anomalous_uuids: Detect UUIDs with unusual metric profiles.
    - detect_behavior_changes: Track metric profile changes across segments.
    - find_similar_windows: Find similar (UUID, segment) pairs across all data.
    """

    @classmethod
    def extract_time_ranges(
        cls,
        dataframe: pd.DataFrame,
        segment_uuid: str,
        uuid_column: str = 'uuid',
        value_column: str = 'value_string',
        time_column: str = 'systime',
        min_duration: Optional[str] = None,
    ) -> pd.DataFrame:
        """Extract time ranges from a categorical signal that changes over time.

        Given a signal (e.g. order number or part number) whose value changes
        over time, detects transitions and produces one row per contiguous
        segment with its start time, end time, and the active value.

        Args:
            dataframe: Input DataFrame in long format.
            segment_uuid: The UUID of the categorical signal to segment by
                (e.g. 'order_number', 'part_number').
            uuid_column: Column identifying each timeseries.
            value_column: Column containing the categorical values.
                Use 'value_string' for string signals, 'value_integer' for int, etc.
            time_column: Column containing timestamps.
            min_duration: Optional minimum segment duration (e.g. '10s', '1min').
                Segments shorter than this are dropped.

        Returns:
            DataFrame with columns:
            - segment_value: The active value during this range (order/part number).
            - segment_start: Start timestamp of the range.
            - segment_end: End timestamp of the range.
            - segment_duration: Duration as Timedelta.
            - segment_index: Sequential index of the segment.
        """
        cls._validate_column(dataframe, uuid_column)
        cls._validate_column(dataframe, value_column)
        cls._validate_column(dataframe, time_column)

        # Filter to the segment signal only
        signal = dataframe[dataframe[uuid_column] == segment_uuid].copy()
        if signal.empty:
            logger.warning(f"No data found for UUID '{segment_uuid}'.")
            return pd.DataFrame(columns=[
                'segment_value', 'segment_start', 'segment_end',
                'segment_duration', 'segment_index',
            ])

        signal = signal.sort_values(time_column).reset_index(drop=True)
        signal[time_column] = pd.to_datetime(signal[time_column])

        # Detect value changes
        values = signal[value_column]
        changed = values.ne(values.shift())
        group_ids = changed.cumsum()

        rows = []
        for group_id, group in signal.groupby(group_ids):
            seg_value = group[value_column].iloc[0]
            # Skip null/empty segments
            if pd.isna(seg_value) or (isinstance(seg_value, str) and seg_value.strip() == ''):
                continue
            seg_start = group[time_column].iloc[0]
            seg_end = group[time_column].iloc[-1]
            rows.append({
                'segment_value': seg_value,
                'segment_start': seg_start,
                'segment_end': seg_end,
                'segment_duration': seg_end - seg_start,
                'segment_index': len(rows),
            })

        if not rows:
            return pd.DataFrame(columns=[
                'segment_value', 'segment_start', 'segment_end',
                'segment_duration', 'segment_index',
            ])

        result = pd.DataFrame(rows)

        if min_duration is not None:
            min_td = pd.Timedelta(min_duration)
            result = result[result['segment_duration'] >= min_td].reset_index(drop=True)
            result['segment_index'] = range(len(result))

        logger.info(
            f"Extracted {len(result)} segments from UUID '{segment_uuid}' "
            f"with {result['segment_value'].nunique()} unique values."
        )
        return result

    @classmethod
    def apply_ranges(
        cls,
        dataframe: pd.DataFrame,
        time_ranges: pd.DataFrame,
        uuid_column: str = 'uuid',
        time_column: str = 'systime',
        target_uuids: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Filter process parameter data by extracted time ranges.

        For each time range (segment), selects the rows from the main DataFrame
        that fall within [segment_start, segment_end] and annotates them with
        the segment value and index.

        Args:
            dataframe: Input DataFrame with process parameter data (all UUIDs).
            time_ranges: Output from extract_time_ranges.
            uuid_column: Column identifying each timeseries.
            time_column: Column containing timestamps.
            target_uuids: Optional list of UUIDs to include. None keeps all.

        Returns:
            Input DataFrame filtered to the time ranges, with added columns:
            - segment_value: The active order/part number for each row.
            - segment_index: The sequential segment index.
        """
        cls._validate_column(dataframe, time_column)

        if time_ranges.empty:
            logger.warning("No time ranges provided.")
            result = dataframe.iloc[:0].copy()
            result['segment_value'] = pd.Series(dtype='object')
            result['segment_index'] = pd.Series(dtype='int64')
            return result

        df = dataframe.copy()
        df[time_column] = pd.to_datetime(df[time_column])

        if target_uuids is not None:
            df = df[df[uuid_column].isin(target_uuids)]

        # Assign segments via interval lookup
        segments = []
        for _, seg in time_ranges.iterrows():
            mask = (df[time_column] >= seg['segment_start']) & (df[time_column] <= seg['segment_end'])
            matched = df[mask].copy()
            matched['segment_value'] = seg['segment_value']
            matched['segment_index'] = seg['segment_index']
            segments.append(matched)

        if not segments:
            logger.warning("No data matched any time range.")
            result = dataframe.iloc[:0].copy()
            result['segment_value'] = pd.Series(dtype='object')
            result['segment_index'] = pd.Series(dtype='int64')
            return result

        result = pd.concat(segments, ignore_index=True)
        logger.info(
            f"Applied {len(time_ranges)} ranges: {len(result)} rows across "
            f"{result[uuid_column].nunique()} UUIDs."
        )
        return result

    @classmethod
    def compute_metric_profiles(
        cls,
        dataframe: pd.DataFrame,
        uuid_column: str = 'uuid',
        value_column: str = 'value_double',
        group_column: str = 'segment_value',
        metrics: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """Compute statistical metrics per UUID per segment.

        Typically called on the output of apply_ranges, where each row is
        annotated with a segment_value (order/part number). Computes metrics
        per (UUID, segment) pair using NumericStatistics.

        Args:
            dataframe: Input DataFrame (output of apply_ranges or similar).
            uuid_column: Column identifying each timeseries.
            value_column: Column containing numeric values.
            group_column: Column to group segments by (e.g. 'segment_value',
                'segment_index'). Use 'segment_value' to aggregate all ranges
                of the same order, or 'segment_index' for individual ranges.
            metrics: Subset of metric names to compute. None uses all 19 metrics.

        Returns:
            DataFrame with columns [uuid, <group_column>, metric_1, metric_2, ...].
        """
        cls._validate_column(dataframe, uuid_column)
        cls._validate_column(dataframe, value_column)
        cls._validate_column(dataframe, group_column)

        if metrics is not None:
            invalid = set(metrics) - set(ALL_METRICS)
            if invalid:
                raise ValueError(f"Unknown metrics: {invalid}. Available: {ALL_METRICS}")

        rows = []
        for (uuid_val, group_val), group in dataframe.groupby([uuid_column, group_column]):
            numeric_data = group[value_column].dropna()
            if len(numeric_data) < 2:
                continue

            stats = NumericStatistics.summary_as_dict(group, value_column)
            if metrics is not None:
                stats = {k: v for k, v in stats.items() if k in metrics}
            stats[uuid_column] = uuid_val
            stats[group_column] = group_val
            stats['sample_count'] = len(numeric_data)
            rows.append(stats)

        if not rows:
            return pd.DataFrame()

        result = pd.DataFrame(rows)
        leading = [uuid_column, group_column, 'sample_count']
        metric_cols = [c for c in result.columns if c not in leading]
        return result[leading + metric_cols].reset_index(drop=True)

    @classmethod
    def _get_metric_columns(
        cls,
        df: pd.DataFrame,
        metric_columns: Optional[List[str]] = None,
    ) -> List[str]:
        """Identify numeric metric columns from a profiles DataFrame."""
        non_metric = {'uuid', 'segment_value', 'segment_index', 'window_start',
                      'window_end', 'sample_count'}
        available = [c for c in df.columns
                     if c not in non_metric and pd.api.types.is_numeric_dtype(df[c])]
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
        group_column: str = 'uuid',
        metric_columns: Optional[List[str]] = None,
        distance_metric: str = 'euclidean',
        normalize: bool = True,
    ) -> pd.DataFrame:
        """Compute pairwise distance matrix between metric profile vectors.

        Can compare UUIDs (group_column='uuid') or segments
        (group_column='segment_value'). When multiple rows exist per group,
        metrics are averaged.

        Args:
            metric_profiles: Output from compute_metric_profiles.
            group_column: Column to group by ('uuid' or 'segment_value').
            metric_columns: Which metric columns to use. None auto-detects.
            distance_metric: 'euclidean', 'cosine', or 'manhattan'.
            normalize: Z-normalize metrics before computing distances.

        Returns:
            Square DataFrame indexed by group values with pairwise distances.
        """
        cols = cls._get_metric_columns(metric_profiles, metric_columns)
        agg = metric_profiles.groupby(group_column)[cols].mean()
        labels = agg.index.tolist()
        matrix = agg.values.astype(float)
        matrix = np.nan_to_num(matrix, nan=0.0)

        if normalize and matrix.shape[0] > 1:
            col_std = matrix.std(axis=0)
            col_std[col_std < 1e-10] = 1.0
            matrix = (matrix - matrix.mean(axis=0)) / col_std

        metric_map = {
            'euclidean': 'euclidean',
            'cosine': 'cosine',
            'manhattan': 'cityblock',
        }
        if distance_metric not in metric_map:
            raise ValueError(
                f"Unknown distance_metric: {distance_metric}. "
                f"Use 'euclidean', 'cosine', or 'manhattan'."
            )

        condensed = pdist(matrix, metric=metric_map[distance_metric])
        dist_matrix = squareform(condensed)
        return pd.DataFrame(dist_matrix, index=labels, columns=labels)

    @classmethod
    def cluster_uuids(
        cls,
        distance_matrix: pd.DataFrame,
        n_clusters: int = 3,
        distance_threshold: Optional[float] = None,
        linkage_method: str = 'average',
    ) -> pd.DataFrame:
        """Group items by metric similarity using hierarchical clustering.

        Args:
            distance_matrix: Square distance matrix from compute_distance_matrix.
            n_clusters: Number of clusters. Ignored if distance_threshold is set.
            distance_threshold: Cut dendrogram at this distance. Overrides n_clusters.
            linkage_method: 'average', 'complete', 'single', or 'ward'.

        Returns:
            DataFrame with columns [uuid, cluster].
        """
        labels = distance_matrix.index.tolist()
        condensed = squareform(distance_matrix.values, checks=False)
        Z = linkage(condensed, method=linkage_method)

        if distance_threshold is not None:
            clusters = fcluster(Z, t=distance_threshold, criterion='distance')
        else:
            clusters = fcluster(Z, t=n_clusters, criterion='maxclust')

        return pd.DataFrame({'uuid': labels, 'cluster': clusters.astype(int)})

    @classmethod
    def find_similar_uuids(
        cls,
        distance_matrix: pd.DataFrame,
        target_uuid: str,
        top_k: int = 5,
    ) -> pd.DataFrame:
        """Find items most similar to a target based on metric profiles.

        Args:
            distance_matrix: Square distance matrix from compute_distance_matrix.
            target_uuid: Item to find similarities for.
            top_k: Number of similar items to return.

        Returns:
            DataFrame with columns [uuid, distance, rank] sorted by distance.
        """
        if target_uuid not in distance_matrix.index:
            raise ValueError(f"'{target_uuid}' not found in distance matrix.")

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
        """Detect items with unusual metric profiles.

        Computes the mean distance from each item to all others. Items whose
        z-score exceeds the threshold are flagged as anomalous.

        Args:
            distance_matrix: Square distance matrix from compute_distance_matrix.
            threshold: Z-score threshold for anomaly detection.

        Returns:
            DataFrame with columns [uuid, anomaly_score, z_score, is_anomalous].
        """
        labels = distance_matrix.index.tolist()
        n = len(labels)
        mean_dists = distance_matrix.values.sum(axis=1) / max(n - 1, 1)

        global_mean = mean_dists.mean()
        global_std = mean_dists.std()
        if global_std < 1e-10:
            z_scores = np.zeros(n)
        else:
            z_scores = (mean_dists - global_mean) / global_std

        return pd.DataFrame({
            'uuid': labels,
            'anomaly_score': mean_dists,
            'z_score': z_scores,
            'is_anomalous': z_scores > threshold,
        })

    @classmethod
    def detect_behavior_changes(
        cls,
        metric_profiles: pd.DataFrame,
        uuid_column: str = 'uuid',
        group_column: str = 'segment_index',
        metric_columns: Optional[List[str]] = None,
        normalize: bool = True,
    ) -> pd.DataFrame:
        """Track how each UUID's metrics change across consecutive segments.

        Computes the Euclidean distance between consecutive segment metric
        vectors for each UUID. Large change scores indicate process shifts.

        Args:
            metric_profiles: Output from compute_metric_profiles.
            uuid_column: Column identifying each timeseries.
            group_column: Column ordering the segments (e.g. 'segment_index').
            metric_columns: Which metric columns to use. None auto-detects.
            normalize: Z-normalize metrics before computing change scores.

        Returns:
            DataFrame with columns [uuid, <group_column>, change_score].
        """
        cols = cls._get_metric_columns(metric_profiles, metric_columns)
        rows = []

        for uuid_val, group in metric_profiles.groupby(uuid_column):
            group = group.sort_values(group_column)
            matrix = group[cols].values.astype(float)
            matrix = np.nan_to_num(matrix, nan=0.0)

            if normalize and matrix.shape[0] > 1:
                col_std = matrix.std(axis=0)
                col_std[col_std < 1e-10] = 1.0
                matrix = (matrix - matrix.mean(axis=0)) / col_std

            segments = group[group_column].values
            for i in range(1, len(matrix)):
                dist = float(np.linalg.norm(matrix[i] - matrix[i - 1]))
                rows.append({
                    uuid_column: uuid_val,
                    group_column: segments[i],
                    'change_score': dist,
                })

        if not rows:
            return pd.DataFrame(columns=[uuid_column, group_column, 'change_score'])
        return pd.DataFrame(rows).reset_index(drop=True)

    @classmethod
    def find_similar_windows(
        cls,
        metric_profiles: pd.DataFrame,
        uuid_column: str = 'uuid',
        group_column: str = 'segment_value',
        metric_columns: Optional[List[str]] = None,
        normalize: bool = True,
        top_k: int = 10,
    ) -> pd.DataFrame:
        """Find the most similar (UUID, segment) pairs across all data.

        Useful for finding which process parameters behave similarly across
        different orders or part numbers.

        Args:
            metric_profiles: Output from compute_metric_profiles.
            uuid_column: Column identifying each timeseries.
            group_column: Column identifying each segment.
            metric_columns: Which metric columns to use. None auto-detects.
            normalize: Z-normalize metrics before computing distances.
            top_k: Number of closest pairs to return.

        Returns:
            DataFrame with columns [uuid_a, group_a, uuid_b, group_b, distance, rank].
        """
        cols = cls._get_metric_columns(metric_profiles, metric_columns)
        matrix = metric_profiles[cols].values.astype(float)
        matrix = np.nan_to_num(matrix, nan=0.0)

        if normalize and matrix.shape[0] > 1:
            col_std = matrix.std(axis=0)
            col_std[col_std < 1e-10] = 1.0
            matrix = (matrix - matrix.mean(axis=0)) / col_std

        uuids = metric_profiles[uuid_column].values
        groups = metric_profiles[group_column].values

        condensed = pdist(matrix, metric='euclidean')
        n = len(matrix)

        k = min(top_k, len(condensed))
        if k == 0:
            return pd.DataFrame(columns=[
                'uuid_a', 'group_a', 'uuid_b', 'group_b', 'distance', 'rank',
            ])

        if len(condensed) <= top_k:
            sorted_indices = np.argsort(condensed)
        else:
            sorted_indices = np.argpartition(condensed, k)[:k]
            sorted_indices = sorted_indices[np.argsort(condensed[sorted_indices])]

        rows = []
        for rank, idx in enumerate(sorted_indices, 1):
            i, j = cls._condensed_to_square(idx, n)
            rows.append({
                'uuid_a': uuids[i],
                'group_a': groups[i],
                'uuid_b': uuids[j],
                'group_b': groups[j],
                'distance': float(condensed[idx]),
                'rank': rank,
            })

        return pd.DataFrame(rows)

    @staticmethod
    def _condensed_to_square(idx: int, n: int):
        """Convert a condensed distance matrix index to (row, col) pair."""
        i = int(n - 2 - np.floor(np.sqrt(-8 * idx + 4 * n * (n - 1) - 7) / 2.0 - 0.5))
        j = int(idx + i + 1 - n * (n - 1) // 2 + (n - i) * ((n - i) - 1) // 2)
        return i, j
