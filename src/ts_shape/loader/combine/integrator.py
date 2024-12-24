import pandas as pd  # type: ignore
from typing import List, Dict, Union, Optional


class DataIntegratorHybrid:
    """
    A flexible utility class to integrate data from various sources, including:
    - API instances (e.g., DatapointAPI)
    - Direct raw data (e.g., UUID list, metadata, timeseries DataFrame)
    - Hybrid approaches (combination of instances and raw data)
    """

    @classmethod
    def combine_data(
        cls,
        timeseries_sources: Optional[List[Union[pd.DataFrame, object]]] = None,
        metadata_sources: Optional[List[Union[pd.DataFrame, object]]] = None,
        uuids: Optional[List[str]] = None,
        join_key: str = "uuid",
        merge_how: str = "left",
    ) -> pd.DataFrame:
        """
        Combine timeseries and metadata from various sources.
        
        :param timeseries_sources: List of timeseries sources (DataFrame or instances with `fetch_data_as_dataframe`).
        :param metadata_sources: List of metadata sources (DataFrame or instances with `fetch_metadata`).
        :param uuids: Optional list of UUIDs to filter the combined data.
        :param join_key: Key column to use for merging, default is "uuid".
        :param merge_how: Merge strategy ('left', 'inner', etc.), default is "left".
        :return: A combined DataFrame.
        """
        # Retrieve and combine timeseries data
        timeseries_data = cls._combine_timeseries(timeseries_sources, join_key)

        if timeseries_data.empty:
            print("No timeseries data found.")
            return pd.DataFrame()

        # Retrieve and combine metadata
        metadata = cls._combine_metadata(metadata_sources, join_key)

        if metadata.empty:
            print("No metadata found.")
            return timeseries_data

        # Merge timeseries data with metadata
        combined_data = pd.merge(timeseries_data, metadata, on=join_key, how=merge_how)

        # Optionally filter the combined data by UUIDs
        if uuids:
            combined_data = combined_data[combined_data[join_key].isin(uuids)]

        return combined_data

    @classmethod
    def _combine_timeseries(cls, sources: Optional[List[Union[pd.DataFrame, object]]], join_key: str) -> pd.DataFrame:
        """
        Combine timeseries data from multiple sources.
        
        :param sources: List of sources (DataFrame or instances with `fetch_data_as_dataframe`).
        :param join_key: Key column to use for merging.
        :return: A combined timeseries DataFrame.
        """
        if not sources:
            return pd.DataFrame()

        frames = []
        for source in sources:
            if isinstance(source, pd.DataFrame):
                frames.append(source)
            elif hasattr(source, "fetch_data_as_dataframe"):
                frames.append(source.fetch_data_as_dataframe())
            else:
                print(f"Unsupported timeseries source: {source}")

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    @classmethod
    def _combine_metadata(cls, sources: Optional[List[Union[pd.DataFrame, object]]], join_key: str) -> pd.DataFrame:
        """
        Combine metadata from multiple sources.
        
        :param sources: List of sources (DataFrame or instances with `fetch_metadata`).
        :param join_key: Key column to use for merging.
        :return: A combined metadata DataFrame.
        """
        if not sources:
            return pd.DataFrame()

        frames = []
        for source in sources:
            if isinstance(source, pd.DataFrame):
                frames.append(source)
            elif hasattr(source, "fetch_metadata"):
                frames.append(source.fetch_metadata())
            else:
                print(f"Unsupported metadata source: {source}")

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()