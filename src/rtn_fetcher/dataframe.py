"""Conversion utilities for pandas and polars DataFrames.

This module provides functions to convert Tbl objects to pandas DataFrames
and polars DataFrames for seamless integration with data analysis workflows.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl

from .table import Tbl


def to_pandas(tbl: Tbl) -> "pd.DataFrame":
    """Convert Tbl to pandas DataFrame.

    pandas is not a dependency of rtn-fetcher; install it separately:
        pip install pandas

    Args:
        tbl: Tbl object to convert.

    Returns:
        pandas DataFrame with same data and column names.

    Raises:
        ImportError: If pandas is not installed.

    Example:
        >>> from rtn_fetcher import read_sheet, to_pandas
        >>> data, accounts = read_sheet(filepath, "1.2")
        >>> df = to_pandas(data)
        >>> df.head()
    """
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError(
            "pandas is required to use to_pandas(). "
            "Install it with: pip install pandas"
        ) from e

    header = tbl.get_header()
    columns = {
        col_name: col_data[1:]
        for col_name, col_data in zip(header, tbl.data, strict=False)
    }
    return pd.DataFrame(columns)


def to_polars(tbl: Tbl) -> "pl.DataFrame":
    """Convert Tbl to polars DataFrame.

    polars is available via the quantilica-io dependency — no extra required.

    Args:
        tbl: Tbl object to convert.

    Returns:
        polars DataFrame with same data and column names.

    Example:
        >>> from rtn_fetcher import read_sheet, to_polars
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
