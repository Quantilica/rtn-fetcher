"""Account hierarchy processing for RTN data.

This module handles the parsing and expansion of hierarchical account codes
and names from RTN (Resultado do Tesouro Nacional) spreadsheets.
"""

import re
from typing import Any

from .constants import ACCOUNT_SEPARATOR, HIERARCHY_SEPARATOR
from .table import Tbl, transpose

# Regex patterns for account parsing
ACCOUNT_CODE_PATTERN = re.compile(
    r"^\s*((?:[A-Za-z]?\d+[A-Za-z]?|[A-Za-z])"
    r"(?:\.(?:[A-Za-z]?\d+[A-Za-z]?|[A-Za-z]))*\.?)"
)
MULTIPLE_SPACES_PATTERN = re.compile(r" +")
TRAILING_NUMBER_PATTERN = re.compile(r"\s*\d+/$")
AUTO_ACCOUNT_PREFIX = "auto"


def extract_account_column(data: Tbl) -> list[Any]:
    """Extract the account names column from table data.

    Args:
        data: Table containing account data.

    Returns:
        List of account names (first element of each column after the first).
    """
    return [col[0] for col in data.data[1:]]


def clean_account_name(name: str) -> str:
    """Clean and normalize account name.

    Removes multiple spaces, trailing numbers with slashes, and
    leading/trailing hyphens and spaces.

    Args:
        name: Raw account name.

    Returns:
        Cleaned account name.
    """
    name = MULTIPLE_SPACES_PATTERN.sub(" ", name)
    name = TRAILING_NUMBER_PATTERN.sub("", name)
    name = name.strip(" -")
    return name


def _looks_like_account_code(code: str) -> bool:
    """Return whether a regex match is likely an account code."""
    code = code.strip().strip(ACCOUNT_SEPARATOR)
    return bool(code) and (
        any(char.isdigit() for char in code) or ACCOUNT_SEPARATOR in code
    )


def normalize_account_code(code: Any) -> str:
    """Normalize account code to package hierarchy separator."""
    if code is None:
        return ""

    if isinstance(code, float) and code.is_integer():
        code = int(code)

    text = str(code).strip().strip(ACCOUNT_SEPARATOR)
    if not text:
        return ""

    if ACCOUNT_SEPARATOR in text:
        parts = [part for part in text.split(ACCOUNT_SEPARATOR) if part]
    elif text.isdigit() and len(text) > 1:
        parts = list(text)
    elif re.fullmatch(r"\d+[A-Za-z]", text):
        parts = [*text[:-1], text[-1]]
    else:
        parts = [text]

    return HIERARCHY_SEPARATOR.join(parts)


def generated_account_code(parts: tuple[int, ...]) -> str:
    """Build a non-colliding generated code for rows without explicit codes."""
    generated_parts = (AUTO_ACCOUNT_PREFIX, *(str(part) for part in parts))
    return HIERARCHY_SEPARATOR.join(generated_parts)


def parse_account_name(name: str) -> tuple[str, str]:
    """Parse account code and name from a combined string.

    RTN accounts are formatted as "1.2.3 Account Name" where "1.2.3" is the
    hierarchical code and "Account Name" is the description.

    Args:
        name: Combined account code and name string.

    Returns:
        Tuple of (account_code, account_name) where account_code uses
        "=>" separator (e.g., "1=>2=>3") and account_name is cleaned.

    Examples:
        >>> parse_account_name("1.2.3 Receitas Correntes")
        ('1=>2=>3', 'Receitas Correntes')
        >>> parse_account_name("Outras Receitas")
        ('', 'Outras Receitas')
    """
    account_code = ""
    account_name = ""

    match = ACCOUNT_CODE_PATTERN.match(name)
    if match and _looks_like_account_code(match.group(1)):
        account_code = match.group(1).strip()

    account_name = clean_account_name(name[match.end() :] if account_code else name)
    account_code = normalize_account_code(account_code)

    return account_code, account_name


def expand_account_hierarchy(accounts_data: Tbl) -> Tbl:
    """Expand account hierarchy into separate columns for each level.

    Transforms hierarchical account codes into a flat structure with one column
    per hierarchy level. Each row contains the full account information plus
    the part names at each level.

    Args:
        accounts_data: Table with [account_code, account_name,
            account_level] columns.

    Returns:
        Table with expanded hierarchy: [account_code, account_name,
        account_level, P_1, P_2, ..., P_N] where P_i contains the
        account part at level i.

    Examples:
        Input row: ('1=>2=>3', 'Despesas de Pessoal', 3)
        Output row: ('1=>2=>3', '1.2.3 Despesas de Pessoal', 3,
                     'Despesas', 'Correntes', 'Despesas de Pessoal')
    """
    account_levels = accounts_data["account_level"][1:]
    max_level = max((int(level) for level in account_levels), default=1)

    part_columns = [f"P_{i}" for i in range(1, max_level + 1)]
    header = ["account_code", "account_name", "account_level", *part_columns]
    expanded_rows = [header]

    last_parts = [None] * max_level

    rows_iterator = accounts_data.iter_rows()
    next(rows_iterator)  # Skip header

    for account_code, account_name, account_level in rows_iterator:
        code_parts = str(account_code).split(HIERARCHY_SEPARATOR)
        level = int(account_level)

        if code_parts[0] == AUTO_ACCOUNT_PREFIX:
            full_account_name = account_name
        else:
            full_account_name = f"{ACCOUNT_SEPARATOR.join(code_parts)} {account_name}"

        row_parts = (
            last_parts[: level - 1] + [account_name] + [None] * (max_level - level)
        )
        row = [account_code, full_account_name, account_level, *row_parts]

        expanded_rows.append(row)
        last_parts = row_parts

    return Tbl(transpose(expanded_rows))
