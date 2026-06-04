"""Parquet writer for RTN tables.

Bridges the internal ``Tbl`` representation to quantilica-io's
standardized Parquet output with manifest-backed provenance metadata.
"""

from __future__ import annotations

from pathlib import Path

from quantilica.analytics.writer import to_parquet
from quantilica.core.manifests import DownloadManifest

from .constants import SHEET_CONFIGS
from .dataframe import to_polars
from .schema import build_contract
from .table import Tbl


def write_table_to_parquet(
    data: Tbl,
    filepath: Path,
    sheet_name: str,
    *,
    manifest: DownloadManifest | None = None,
    compression: str = "zstd",
) -> Path:
    """Write an RTN long-format table to Parquet.

    The output is cast to the contract derived from ``SHEET_CONFIGS``
    and the manifest's provenance is embedded in the Parquet header.
    """
    if sheet_name not in SHEET_CONFIGS:
        available = ", ".join(SHEET_CONFIGS.keys())
        raise ValueError(f"Unknown sheet '{sheet_name}'. Available: {available}")

    contract = build_contract(sheet_name, SHEET_CONFIGS[sheet_name])
    df = contract.cast(to_polars(data))
    return to_parquet(
        df,
        Path(filepath),
        manifest=manifest,
        compression=compression,
    )
