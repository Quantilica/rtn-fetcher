"""Conversion utilities for polars DataFrames."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import polars as pl

from .table import Tbl


def to_polars(tbl: Tbl) -> "pl.DataFrame":
    """Convert Tbl to polars DataFrame.

    Requer extra 'analysis' instalado via quantilica-analytics.

    Args:
        tbl: Tbl object to convert.

    Returns:
        polars DataFrame with same data and column names.

    Example:
        >>> from rtn_fetcher import read_sheet
        >>> from rtn_fetcher.dataframe import to_polars
        >>> data, accounts = read_sheet(filepath, "1.2")
        >>> df = to_polars(data)
        >>> df.head()
    """
    import polars as pl

    header = tbl.get_header()
    columns = {
        col_name: col_data[1:]
        for col_name, col_data in zip(header, tbl.data, strict=False)
    }
    return pl.DataFrame(columns)
