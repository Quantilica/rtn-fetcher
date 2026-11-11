"""Package-wide constants and configuration.

This module contains all configuration values, URLs, and constants used
throughout the rtn-fetcher package.
"""

from __future__ import annotations

from typing import Any

# API Configuration
RTN_API_BASE_URL = "https://apiapex.tesouro.gov.br/aria//v1/thot/custom/rtn"
RTN_FILE_BASE_URL = (
    "http://sisweb.tesouro.gov.br/apex/cosis/thot/link/rtn/serie-historica"
)
RTN_THOT_ARQUIVOS_BASE_URL = "https://thot-arquivos.tesouro.gov.br"
RTN_CDN_BASE_URL = "https://cdn.tesouro.gov.br"
RTN_CKAN_PACKAGE_URL = (
    "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show"
    "?id=ab56485b-9c40-4efb-8563-9ce3e1973c4b"
)

# Semente de anexos conhecidos da Série Histórica no THOT
# Chave: (ano, mes) -> meta do anexo
KNOWN_SERIE_HISTORICA_ANEXOS: dict[tuple[int, int], dict[str, Any]] = {
    (2026, 9): {
        "pub_id": 56116,
        "anexo_id": 29566,
        "filename": "serie_historica_set26.xlsx",
    },
    (2026, 8): {
        "pub_id": 55921,
        "anexo_id": 29326,
        "filename": "serie_historica_ago26.xlsx",
    },
    (2026, 7): {
        "pub_id": 55499,
        "anexo_id": 29032,
        "filename": "serie_historica_jul26.xlsx",
    },
}

# HTTP Settings
HTTP_REQUEST_TIMEOUT = 60
HTTP_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"

# Account Hierarchy
HIERARCHY_SEPARATOR = "."
ACCOUNT_SEPARATOR = "."
SPECIAL_ACCOUNT_MARKER = "d/q"

# Data Processing
MIN_ROW_CELLS = 3
MILLION_MULTIPLIER = 1_000_000
NA_VALUE = "n.a."
MISSING_VALUE_LABELS = {"", "-", "n.a.", "n.d.", "n\u00e3o disp", "na", "nd"}
MAX_DISPLAY_ROWS = 10

# Column Names
DATE_COLUMN = "date"
YEAR_COLUMN = "year"
MONTH_COLUMN = "month"
QUARTER_COLUMN = "quarter"
ACCOUNT_COLUMN = "account"
VALUE_COLUMN = "value"
ACCOUNT_CODE_COLUMN = "account_code"
ACCOUNT_NAME_COLUMN = "account_name"
ACCOUNT_LEVEL_COLUMN = "account_level"

# Sheet Configurations
# Format: {sheet_name: {period, account_columns}}
SHEET_CONFIGS = {
    "1.1": {"period": "monthly", "account_columns": 1},
    "1.1-A": {"period": "monthly", "account_columns": 1},
    "1.2": {"period": "monthly", "account_columns": 1},
    "1.2-A": {"period": "monthly", "account_columns": 1},
    "1.2-B": {"period": "monthly", "account_columns": 1},
    "1.3": {"period": "monthly", "account_columns": 1},
    "1.3-A": {"period": "monthly", "account_columns": 1},
    "1.4": {"period": "monthly", "account_columns": 1},
    "1.4-A": {"period": "monthly", "account_columns": 1},
    "1.5": {"period": "monthly", "account_columns": 1},
    "1.5-A": {"period": "monthly", "account_columns": 1},
    "1.6": {"period": "monthly", "account_columns": 1},
    "2.1": {"period": "yearly", "account_columns": 1},
    "2.1-A": {"period": "yearly", "account_columns": 1},
    "2.2": {"period": "yearly", "account_columns": 1},
    "2.2-A": {"period": "yearly", "account_columns": 1},
    "2.3": {"period": "yearly", "account_columns": 1},
    "2.3-A": {"period": "yearly", "account_columns": 1},
    "2.4": {"period": "yearly", "account_columns": 1},
    "2.4-A": {"period": "yearly", "account_columns": 1},
    "2.5": {"period": "yearly", "account_columns": 1},
    "2.5-A": {"period": "yearly", "account_columns": 1},
    "4.1": {"period": "quarterly", "account_columns": 2},
    "4.2": {"period": "quarterly", "account_columns": 2},
}

AVAILABLE_SHEETS = list(SHEET_CONFIGS.keys())
