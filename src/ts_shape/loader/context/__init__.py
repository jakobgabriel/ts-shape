"""Context Loaders

Helpers for enriching timeseries data with contextual metadata.

Classes:
- ContextEnricher: Merge timeseries with metadata context (tolerances,
  descriptions, units) using UUID-based lookups.
  - enrich_with_metadata: Join metadata columns onto timeseries by UUID.
  - enrich_with_tolerances: Attach tolerance limits from a tolerance DataFrame.
  - enrich_with_mapping: Apply value mappings from a mapping DataFrame.
"""

from .context_enricher import ContextEnricher

__all__ = [
    "ContextEnricher",
]
