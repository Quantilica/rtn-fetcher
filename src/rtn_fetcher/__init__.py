"""rtn-fetcher - Biblioteca Python para processamento de dados do Resultado do Tesouro Nacional (RTN).

Este pacote fornece ferramentas para baixar, extrair e transformar dados fiscais
publicados pelo Tesouro Nacional do Brasil.
"""

from importlib.metadata import PackageNotFoundError, version

from quantilica_core.logging import get_logger

try:
    __version__ = version("rtn-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

logger = get_logger(__name__)


# Public API - Main functionality
from .fetcher import download_latest_file, fetch_publications_metadata
from .reader import read_all_sheets, read_sheet, write_table_to_csv
from .table import Tbl

# Public API - Data extraction (advanced use)
from .extract import (
    build_account_data,
    extract_publication_metadata,
    extract_sheet_rows,
)

# Public API - Account processing (advanced use)
from .account import expand_account_hierarchy, parse_account_name

# Public API - DataFrame conversion (optional, requires pandas/polars)
from .dataframe import to_pandas, to_polars

# Public API - Parquet output with quantilica-io
from .schema import build_contract
from .writer import write_table_to_parquet

__all__ = [
    # Version
    "__version__",
    # Main data structures
    "Tbl",
    # High-level functions
    "download_latest_file",
    "fetch_publications_metadata",
    "read_sheet",
    "read_all_sheets",
    "write_table_to_csv",
    "write_table_to_parquet",
    # Data extraction
    "extract_publication_metadata",
    "extract_sheet_rows",
    "build_account_data",
    # Account processing
    "parse_account_name",
    "expand_account_hierarchy",
    # DataFrame conversion (optional)
    "to_pandas",
    "to_polars",
    # Schema / contracts
    "build_contract",
]
