"""Package-wide constants and configuration.

This module contains all configuration values, URLs, and constants used
throughout the rtnpy package.
"""

# API Configuration
RTN_API_BASE_URL = "https://apiapex.tesouro.gov.br/aria//v1/thot/custom/rtn"
RTN_FILE_BASE_URL = (
    "http://sisweb.tesouro.gov.br/apex/cosis/thot/link/rtn/serie-historica"
)

# HTTP Settings
HTTP_REQUEST_TIMEOUT = 60
HTTP_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S %Z"

# Account Hierarchy
HIERARCHY_SEPARATOR = "=>"
ACCOUNT_SEPARATOR = "."
SPECIAL_ACCOUNT_MARKER = "d/q"

# Data Processing
MIN_ROW_CELLS = 3
MILLION_MULTIPLIER = 1_000_000
NA_VALUE = "n.a."
MAX_DISPLAY_ROWS = 10

# Column Names
DATE_COLUMN = "date"
YEAR_COLUMN = "year"
MONTH_COLUMN = "month"
ACCOUNT_COLUMN = "account"
VALUE_COLUMN = "value"
ACCOUNT_CODE_COLUMN = "account_code"
ACCOUNT_NAME_COLUMN = "account_name"
ACCOUNT_LEVEL_COLUMN = "account_level"

# Sheet Configurations
# Format: {sheet_name: {min_row, max_row, drop_cols, period}}
SHEET_CONFIGS = {
    "1.2": {"min_row": 5, "max_row": 162, "drop_cols": [], "period": "monthly"},
    "1.3": {"min_row": 5, "max_row": 65, "drop_cols": [1], "period": "monthly"},
    "1.6": {"min_row": 5, "max_row": 24, "drop_cols": [], "period": "monthly"},
    "2.2-A": {"min_row": 5, "max_row": 162, "drop_cols": [], "period": "yearly"},
}

AVAILABLE_SHEETS = list(SHEET_CONFIGS.keys())
