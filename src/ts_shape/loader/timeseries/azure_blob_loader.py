from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from typing import Iterable, List, Optional, Set, Dict

import pandas as pd  # type: ignore
 


class AzureBlobParquetLoader:
    """
    Load parquet files from an Azure Blob Storage container filtered by a list of UUIDs.

    Optimized for speed by:
    - Using server-side prefix filtering when provided
    - Streaming blob listings and filtering client-side by UUID containment
    - Downloading and parsing parquet files concurrently
    """

    def __init__(
        self,
        container_name: str,
        *,
        connection_string: Optional[str] = None,
        account_url: Optional[str] = None,
        credential: Optional[object] = None,
        prefix: str = "",
        max_workers: int = 8,
    ) -> None:
        """
        Initialize the loader with Azure connection details.

        Args:
            connection_string: Azure Storage connection string.
            container_name: Target container name.
            prefix: Optional path prefix to narrow listing (e.g. "year/month/").
            max_workers: Max concurrent downloads/reads.
        """
        try:
            from azure.storage.blob import ContainerClient  # type: ignore
        except Exception as exc:  # pragma: no cover - import guard
            raise ImportError(
                "azure-storage-blob is required for AzureBlobParquetLoader. "
                "Install with `pip install azure-storage-blob`."
            ) from exc

        self._ContainerClient = ContainerClient
        # Prefer AAD credential path if account_url provided or credential is given
        if account_url or (credential is not None and not connection_string):
            if not account_url:
                raise ValueError("account_url must be provided when using AAD credential auth")
            if credential is None:
                raise ValueError("credential must be provided when using AAD credential auth")
            self.container_client = ContainerClient(account_url=account_url, container_name=container_name, credential=credential)
        else:
            if not connection_string:
                raise ValueError("Either connection_string or (account_url + credential) must be provided")
            self.container_client = ContainerClient.from_connection_string(
                conn_str=connection_string, container_name=container_name
            )
        self.prefix = prefix
        self.max_workers = max_workers if max_workers > 0 else 1

    @classmethod
    def from_account_name(
        cls,
        account_name: str,
        container_name: str,
        *,
        credential: Optional[object] = None,
        endpoint_suffix: str = "blob.core.windows.net",
        prefix: str = "",
        max_workers: int = 8,
    ) -> "AzureBlobParquetLoader":
        """
        Construct a loader using AAD credentials with an account name.

        Args:
            account_name: Storage account name.
            container_name: Target container.
            credential: Optional Azure credential (DefaultAzureCredential if None).
            endpoint_suffix: DNS suffix for the blob endpoint (e.g., for sovereign clouds).
            prefix: Optional listing prefix (e.g., "parquet/").
            max_workers: Concurrency for downloads.
        """
        account_url = f"https://{account_name}.{endpoint_suffix}"
        if credential is None:
            raise ValueError("credential must be provided when using AAD credential auth")
        return cls(
            container_name=container_name,
            account_url=account_url,
            credential=credential,
            prefix=prefix,
            max_workers=max_workers,
        )

    def _iter_matching_blob_names(self, uuids: Set[str]) -> Iterable[str]:
        """
        Iterate over blob names that end with .parquet and contain any of the given UUIDs.

        Uses server-side prefix filtering when `self.prefix` is provided to reduce listing.
        """
        # Stream listing to handle large containers efficiently
        blob_iter = self.container_client.list_blobs(name_starts_with=self.prefix or None)
        for blob in blob_iter:  # type: ignore[attr-defined]
            name: str = blob.name  # type: ignore[attr-defined]
            if not name.endswith(".parquet"):
                continue
            # Fast path: check containment against UUID set
            # Assumes filenames or paths contain the UUID as substring
            if any(u in name for u in uuids):
                yield name

    def _download_parquet(self, blob_name: str) -> Optional[pd.DataFrame]:
        """
        Download a parquet blob and return a DataFrame. Returns None if not found.
        """
        try:
            downloader = self.container_client.download_blob(blob_name)
            data = downloader.readall()
            return pd.read_parquet(BytesIO(data))
        except Exception:
            # Swallow individual blob errors to keep batch resilient
            return None

    # ---- Helpers for time-structured containers parquet/YYYY/MM/DD/HH ----
    @staticmethod
    def _hourly_slots(start_timestamp: str | pd.Timestamp, end_timestamp: str | pd.Timestamp) -> Iterable[pd.Timestamp]:
        start = pd.to_datetime(start_timestamp)
        end = pd.to_datetime(end_timestamp)
        # Ensure inclusive range per hour
        return pd.date_range(start=start, end=end, freq="h")

    def _hour_prefix(self, ts: pd.Timestamp) -> str:
        # Builds e.g. "parquet/2024/01/31/09/" if prefix="parquet/"
        y = str(ts.year)
        m = str(ts.month).zfill(2)
        d = str(ts.day).zfill(2)
        h = str(ts.hour).zfill(2)
        base = self.prefix or ""
        if base and not base.endswith("/"):
            base += "/"
        return f"{base}{y}/{m}/{d}/{h}/"

    def load_all_files(self) -> pd.DataFrame:
        """
        Load all parquet blobs in the container (optionally under `prefix`).

        Returns:
            A concatenated DataFrame of all parquet blobs. Returns an empty DataFrame
            if none are found.
        """
        # List all parquet blob names using optional prefix for server-side filtering
        blob_iter = self.container_client.list_blobs(name_starts_with=self.prefix or None)
        blob_names = [b.name for b in blob_iter if str(b.name).endswith(".parquet")]  # type: ignore[attr-defined]
        if not blob_names:
            return pd.DataFrame()

        frames: List[pd.DataFrame] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_name = {executor.submit(self._download_parquet, name): name for name in blob_names}
            for future in as_completed(future_to_name):
                df = future.result()
                if df is not None and not df.empty:
                    frames.append(df)

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def load_by_time_range(self, start_timestamp: str | pd.Timestamp, end_timestamp: str | pd.Timestamp) -> pd.DataFrame:
        """
        Load all parquet blobs under hourly folders within [start, end].

        Assumes container structure: prefix/year/month/day/hour/{file}.parquet
        Listing is constrained per-hour for speed.
        """
        hour_prefixes = [self._hour_prefix(ts) for ts in self._hourly_slots(start_timestamp, end_timestamp)]
        blob_names: List[str] = []
        for pfx in hour_prefixes:
            blob_iter = self.container_client.list_blobs(name_starts_with=pfx)
            blob_names.extend([b.name for b in blob_iter if str(b.name).endswith(".parquet")])  # type: ignore[attr-defined]

        if not blob_names:
            return pd.DataFrame()

        frames: List[pd.DataFrame] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_name = {executor.submit(self._download_parquet, name): name for name in blob_names}
            for future in as_completed(future_to_name):
                df = future.result()
                if df is not None and not df.empty:
                    frames.append(df)

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def load_files_by_time_range_and_uuids(
        self,
        start_timestamp: str | pd.Timestamp,
        end_timestamp: str | pd.Timestamp,
        uuid_list: List[str],
    ) -> pd.DataFrame:
        """
        Load parquet blobs for given UUIDs within [start, end] hours.

        Strategy:
        1) Construct direct blob paths assuming pattern prefix/YYYY/MM/DD/HH/{uuid}.parquet
           (fast path, no listing).
        2) For robustness, also list each hour prefix and include any blob whose basename
           equals one of the requested UUID variants (handles case differences and extra
           subfolders below the hour level).
        """
        if not uuid_list:
            return pd.DataFrame()

        # Sanitize and deduplicate UUIDs while preserving order
        def _clean_uuid(u: object) -> str:
            s = str(u).strip().strip("{}").strip()
            return s

        raw = [_clean_uuid(u) for u in uuid_list]
        # Include lowercase variants to be tolerant of case differences in filenames
        variants_ordered: List[str] = []
        seen: Set[str] = set()
        for u in raw:
            for v in (u, u.lower()):
                if v and v not in seen:
                    seen.add(v)
                    variants_ordered.append(v)

        hour_prefixes = [self._hour_prefix(ts) for ts in self._hourly_slots(start_timestamp, end_timestamp)]

        # 1) Fast path: build direct blob names
        direct_names = [f"{pfx}{u}.parquet" for pfx in hour_prefixes for u in variants_ordered]

        # 2) Robust path: list each hour prefix and filter by basename match
        basenames = {f"{u}.parquet" for u in variants_ordered}
        listed_names: List[str] = []
        try:
            for pfx in hour_prefixes:
                blob_iter = self.container_client.list_blobs(name_starts_with=pfx)
                for b in blob_iter:  # type: ignore[attr-defined]
                    name = str(b.name)
                    if not name.endswith(".parquet"):
                        continue
                    base = name.rsplit("/", 1)[-1]
                    if base in basenames:
                        listed_names.append(name)
        except Exception:
            # If listing fails for any reason, continue with direct names only
            pass

        # Merge and preserve order, avoid duplicates
        all_blob_names = list(dict.fromkeys([*direct_names, *listed_names]))

        if not all_blob_names:
            return pd.DataFrame()

        frames: List[pd.DataFrame] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_name = {executor.submit(self._download_parquet, name): name for name in all_blob_names}
            for future in as_completed(future_to_name):
                df = future.result()
                if df is not None and not df.empty:
                    frames.append(df)

        return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

    def list_structure(self, parquet_only: bool = True, limit: Optional[int] = None) -> Dict[str, List[str]]:
        """
        List folder prefixes (hours) and blob names under the configured `prefix`.

        Args:
            parquet_only: If True, only include blobs ending with .parquet.
            limit: Optional cap on number of files collected for quick inspection.

        Returns:
            A dict with:
            - folders: Sorted unique hour-level prefixes like 'parquet/YYYY/MM/DD/HH/'
            - files: Sorted blob names (full paths) matching the filter
        """
        folders: Set[str] = set()
        files: List[str] = []
        collected = 0

        blob_iter = self.container_client.list_blobs(name_starts_with=self.prefix or None)
        for b in blob_iter:
            name = str(b.name)
            if parquet_only and not name.endswith(".parquet"):
                continue
            files.append(name)
            # Derive hour-level folder prefix
            if "/" in name:
                folders.add(name.rsplit("/", 1)[0].rstrip("/") + "/")
            collected += 1
            if limit is not None and collected >= limit:
                break

        return {
            "folders": sorted(folders),
            "files": sorted(files),
        }
