"""Account hierarchy processing for RTN data.

This module handles the parsing and expansion of hierarchical account codes
and names from RTN (Resultado do Tesouro Nacional) spreadsheets.
"""

import re

from .constants import ACCOUNT_SEPARATOR, HIERARCHY_SEPARATOR
from .table import Tbl, transpose

# Regex patterns for account parsing
ACCOUNT_CODE_PATTERN = re.compile(r"^\d+((\.\ d+)+|\.)")
MULTIPLE_SPACES_PATTERN = re.compile(r" +")
TRAILING_NUMBER_PATTERN = re.compile(r" \d+/$")


def extract_account_column(data: Tbl) -> list[str]:
    """Extract the account names column from table data.

    Args:
        data: Table containing account data.

    Returns:
        List of account names (first element of each column after the first).
    """
    return [col[0] for col in data.data[1:]]


def clean_account_name(name: str) -> str:
    """Clean and normalize account name.

    Removes multiple spaces, trailing numbers with slashes, and leading/trailing
    hyphens and spaces.

    Args:
        name: Raw account name.

    Returns:
        Cleaned account name.
    """
    name = MULTIPLE_SPACES_PATTERN.sub(" ", name)
    name = TRAILING_NUMBER_PATTERN.sub("", name)
    name = name.strip(" -")
    return name


def parse_account_name(name: str) -> tuple[str, str]:
    """Parse account code and name from a combined string.

    RTN accounts are formatted as "1.2.3 Account Name" where "1.2.3" is the
    hierarchical code and "Account Name" is the description.

    Args:
        name: Combined account code and name string.

    Returns:
        Tuple of (account_code, account_name) where account_code uses "=>"
        as separator (e.g., "1=>2=>3") and account_name is the cleaned description.

    Examples:
        >>> parse_account_name("1.2.3 Receitas Correntes")
        ('1=>2=>3', 'Receitas Correntes')
        >>> parse_account_name("Outras Receitas")
        ('', 'Outras Receitas')
    """
    account_code = ""
    account_name = ""

    match = ACCOUNT_CODE_PATTERN.match(name)
    if match:
        account_code = match.group().strip()

    account_name = clean_account_name(name.replace(account_code, ""))
    account_code = account_code.strip(ACCOUNT_SEPARATOR).replace(
        ACCOUNT_SEPARATOR, HIERARCHY_SEPARATOR
    )

    return account_code, account_name


def expand_account_hierarchy(accounts_data: Tbl) -> Tbl:
    """Expand account hierarchy into separate columns for each level.

    Transforms hierarchical account codes into a flat structure with one column
    per hierarchy level. Each row contains the full account information plus
    the part names at each level.

    Args:
        accounts_data: Table with columns [account_code, account_name, account_level].

    Returns:
        Table with expanded hierarchy: [account_code, account_name, account_level,
        P_1, P_2, ..., P_N] where P_i contains the account part at level i.

    Examples:
        Input row: ('1=>2=>3', 'Despesas de Pessoal', 3)
        Output row: ('1=>2=>3', '1.2.3 Despesas de Pessoal', 3,
                     'Despesas', 'Correntes', 'Despesas de Pessoal')
    """
    account_codes = accounts_data["account_code"][1:]
    max_level = max(len(code.split(HIERARCHY_SEPARATOR)) for code in account_codes)

    part_columns = [f"P_{i}" for i in range(1, max_level + 1)]
    header = ["account_code", "account_name", "account_level", *part_columns]
    expanded_rows = [header]

    last_parts = [None] * max_level

    rows_iterator = accounts_data.iter_rows()
    next(rows_iterator)  # Skip header

    for account_code, account_name, account_level in rows_iterator:
        code_parts = account_code.split(HIERARCHY_SEPARATOR)
        level = len(code_parts)

        full_account_name = f"{ACCOUNT_SEPARATOR.join(code_parts)} {account_name}"

        row_parts = (
            last_parts[: level - 1] + [account_name] + [None] * (max_level - level)
        )
        row = [account_code, full_account_name, account_level, *row_parts]

        expanded_rows.append(row)
        last_parts = row_parts

    return Tbl(transpose(expanded_rows))
