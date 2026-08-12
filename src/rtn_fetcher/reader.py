"""RTN Excel file reader and data transformation.

Handles reading specific sheets from RTN Excel files and transforming them
into normalized long-format tables.
"""

import csv
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Literal

from quantilica.core.exceptions import ParseError
from quantilica.core.logging import get_logger, log_step

from .account import expand_account_hierarchy, extract_account_column
from .constants import (
    ACCOUNT_COLUMN,
    DATE_COLUMN,
    MILLION_MULTIPLIER,
    MISSING_VALUE_LABELS,
    MONTH_COLUMN,
    QUARTER_COLUMN,
    SHEET_CONFIGS,
    VALUE_COLUMN,
    YEAR_COLUMN,
)
from .excel import Sheet, cell_to_value, open_workbook
from .extract import (
    build_account_data,
    build_account_data_from_columns,
)
from .table import Tbl, apply, get_header

logger = get_logger(__name__)

PeriodType = Literal["monthly", "yearly", "quarterly"]

QUARTER_PATTERN = re.compile(r"^(?P<year>\d{4})-(?P<quarter>I|II|III|IV|[1-4])$")
ROMAN_QUARTERS = {"I": 1, "II": 2, "III": 3, "IV": 4}


def convert_cells_to_values(data: Tbl) -> Tbl:
    """Convert all Cell objects in table to their Python values.

    Args:
        data: Table containing Excel Cell objects.

    Returns:
        Table with Cell objects converted to values.
    """
    return Tbl([apply(column, cell_to_value) for column in data.data])


def convert_to_millions(value: Any) -> int | None:
    """Convert a value expressed in R$ millions to reais.

    Args:
        value: Value to convert (expected to be numeric or a missing marker).

    Returns:
        Value multiplied by 1,000,000, or None if value is missing.
    """
    converted = convert_value(value, MILLION_MULTIPLIER)
    return None if converted is None else int(converted)


def convert_value(value: Any, multiplier: int = 1) -> int | float | str | None:
    """Normalize spreadsheet values and apply the unit multiplier.

    Args:
        value: Value to convert.
        multiplier: Multiplier to apply to numeric values.

    Returns:
        Normalized value.
    """
    if value is None:
        return None

    if isinstance(value, str):
        stripped = value.strip()
        folded = stripped.casefold()
        if folded in MISSING_VALUE_LABELS or folded.startswith("n\u00e3o disp"):
            return None
        value = stripped

    if multiplier == MILLION_MULTIPLIER:
        return int(round(float(value) * multiplier))

    return value


def split_date_column(data: Tbl, column_name: str) -> Tbl:
    """Split datetime column into separate year and month columns.

    Args:
        data: Table with datetime column.
        column_name: Name of the datetime column to split.

    Returns:
        Table with datetime column replaced by year and month columns.
    """
    new_data = data.data.copy()
    header = get_header(new_data)
    column_index = header.index(column_name)

    dates_column = new_data[column_index]
    year_column = [YEAR_COLUMN] + [date.year for date in dates_column[1:]]
    month_column = [MONTH_COLUMN] + [date.month for date in dates_column[1:]]

    new_data[column_index] = year_column
    new_data.insert(column_index + 1, month_column)

    return Tbl(new_data)


def split_quarter_column(data: Tbl, column_name: str) -> Tbl:
    """Split quarter labels like "2024-I" into year and quarter columns.

    Args:
        data: Table with quarter column.
        column_name: Name of the quarter column to split.

    Returns:
        Table with quarter column split into year and quarter.
    """
    new_data = data.data.copy()
    header = get_header(new_data)
    column_index = header.index(column_name)

    years = [YEAR_COLUMN]
    quarters = [QUARTER_COLUMN]

    for period in new_data[column_index][1:]:
        year, quarter = parse_quarter(period)
        years.append(year)
        quarters.append(quarter)

    new_data[column_index] = years
    new_data.insert(column_index + 1, quarters)

    return Tbl(new_data)


def parse_quarter(value: Any) -> tuple[int, int]:
    """Parse RTN quarter labels such as "2024-I" or "2024-1".

    Args:
        value: Quarter label string.

    Returns:
        Tuple of (year, quarter).

    Raises:
        ParseError: If the quarter label format is invalid.
    """
    match = QUARTER_PATTERN.match(str(value).strip())
    if not match:
        raise ParseError(f"Invalid quarterly period: {value!r}")

    quarter_text = match.group("quarter")
    quarter = (
        ROMAN_QUARTERS[quarter_text]
        if quarter_text in ROMAN_QUARTERS
        else int(quarter_text)
    )
    return int(match.group("year")), quarter


def is_period_value(value: Any, period: PeriodType) -> bool:
    """Return whether a cell value looks like a period header.

    Args:
        value: Cell value to check.
        period: Period type ("monthly", "yearly", or "quarterly").

    Returns:
        True if the value matches the period type format.
    """
    if period == "monthly":
        return isinstance(value, date | datetime)
    if period == "yearly":
        return (
            isinstance(value, int | float)
            and not isinstance(value, bool)
            and float(value).is_integer()
            and 1900 <= int(value) <= 2200
        )
    if period == "quarterly":
        return bool(QUARTER_PATTERN.match(str(value).strip()))
    return False


def find_header_row(sheet: Sheet, period: PeriodType, account_columns: int) -> int:
    """Find the row containing the period headers.

    Args:
        sheet: Excel worksheet.
        period: Expected period type.
        account_columns: Number of leading columns before periods.

    Returns:
        Row index of the header row (1-indexed).

    Raises:
        ParseError: If no header row is found.
    """
    period_start_index = account_columns

    for row in sheet.iter_rows():
        values = [cell.value for cell in row]
        period_count = sum(
            is_period_value(value, period) for value in values[period_start_index:]
        )
        if period_count >= 3:
            return row[0].row

    raise ParseError(f"Could not find period header row in sheet '{sheet.title}'")


def find_period_bounds(
    sheet: Sheet,
    header_row: int,
    period: PeriodType,
    account_columns: int,
) -> tuple[int, int]:
    """Find the first and last columns containing period headers.

    Args:
        sheet: Excel worksheet.
        header_row: Row index of the header.
        period: Expected period type.
        account_columns: Number of leading columns.

    Returns:
        Tuple of (first_column, last_column) indices.

    Raises:
        ParseError: If period columns cannot be found.
    """
    first_period_col = account_columns + 1
    period_columns = []

    for column in range(first_period_col, sheet.max_column + 1):
        value = sheet.cell(header_row, column).value
        if is_period_value(value, period):
            period_columns.append(column)
        elif period_columns:
            break

    if not period_columns:
        raise ParseError(f"Could not find period columns in sheet '{sheet.title}'")

    return period_columns[0], period_columns[-1]


def is_metadata_row(row: list[Any], account_columns: int) -> bool:
    """Identify note/source/section-header rows that are not observations.

    Args:
        row: Row data as a list of cells or values.
        account_columns: Number of leading columns for accounts.

    Returns:
        True if the row is metadata.
    """
    account_values = [cell.value for cell in row[:account_columns]]
    account_text = " ".join(str(value).strip() for value in account_values if value)
    account_text_lower = account_text.casefold()

    if not account_text:
        return True

    # "Deflator - IPCA base <mês/ano>" é uma linha de rodapé com a razão de
    # deflação usada nas abas de valores constantes (1.1-A, 1.2-A, 1.2-B,
    # 1.3-A, 1.4-A, 1.5-A) — não tem código hierárquico e seus valores são
    # razões (~1-6), não R$; sem este filtro ela virava uma pseudo-conta de
    # primeiro nível na árvore de contas.
    metadata_prefixes = ("obs.", "fonte:", "memorando", "memorando:", "deflator")
    if account_text_lower.startswith(metadata_prefixes):
        return True

    if "pib nominal" in account_text_lower:
        return True

    return bool(re.match(r"^\d+/", account_text_lower))


def extract_data_rows(
    sheet: Sheet,
    period: PeriodType,
    account_columns: int,
) -> list[list[Any]]:
    """Extract the header row and data rows for a configured RTN sheet.

    Args:
        sheet: Excel worksheet.
        period: Period type.
        account_columns: Number of leading columns.

    Returns:
        List of data rows including header row.

    Raises:
        ParseError: If no data rows can be found.
    """
    header_row = find_header_row(sheet, period, account_columns)
    _, last_period_col = find_period_bounds(
        sheet=sheet,
        header_row=header_row,
        period=period,
        account_columns=account_columns,
    )

    rows = [
        [sheet.cell(header_row, column) for column in range(1, last_period_col + 1)]
    ]

    for row_index in range(header_row + 1, sheet.max_row + 1):
        row = [
            sheet.cell(row_index, column) for column in range(1, last_period_col + 1)
        ]
        period_values = [cell.value for cell in row[account_columns:]]

        if is_metadata_row(row, account_columns):
            continue
        if not any(value is not None for value in period_values):
            continue

        rows.append(row)

    if len(rows) == 1:
        raise ParseError(f"No data rows found in sheet '{sheet.title}'")

    return rows


def detect_value_multiplier(sheet: Sheet) -> int:
    """Infer whether values should be converted from R$ millions to reais.

    Args:
        sheet: Excel worksheet.

    Returns:
        Multiplier value (e.g. 1,000,000 or 1).
    """
    unit_text = str(sheet.cell(3, 1).value or "").casefold()
    if "r$" in unit_text and "milh" in unit_text:
        return MILLION_MULTIPLIER
    return 1


def build_wide_table(
    rows: list[list[Any]],
    account_columns: int,
) -> tuple[Tbl, Tbl]:
    """Build a wide table and account hierarchy from worksheet rows.

    Args:
        rows: Extracted rows from the worksheet.
        account_columns: Number of leading account columns.

    Returns:
        Tuple of (wide_data_table, account_hierarchy_table).
    """
    if account_columns == 1:
        raw_data = Tbl(rows)
        raw_data.data[0][0] = DATE_COLUMN

        account_cells = extract_account_column(raw_data)
        accounts_data = build_account_data(account_cells)

        account_codes = accounts_data["account_code"][1:]
        for column, account_code in zip(raw_data.data[1:], account_codes, strict=False):
            column[0] = account_code

        return raw_data, expand_account_hierarchy(accounts_data)

    header_row = rows[0]
    data_rows = rows[1:]
    raw_columns = [[DATE_COLUMN, *header_row[account_columns:]]]

    accounts_data = build_account_data_from_columns(
        code_cells=[row[0] for row in data_rows],
        name_cells=[row[1] for row in data_rows],
    )

    for row, account_code in zip(
        data_rows, accounts_data["account_code"][1:], strict=False
    ):
        raw_columns.append([account_code, *row[account_columns:]])

    return Tbl(raw_columns), expand_account_hierarchy(accounts_data)


def read_sheet_data(
    sheet: Sheet,
    period: PeriodType,
    account_columns: int = 1,
) -> tuple[Tbl, Tbl]:
    """Read and transform data from an Excel sheet.

    Performs the complete data transformation pipeline:
    1. Detect the period header and data rows
    2. Build account hierarchy
    3. Convert cells to values
    4. Melt to long format
    5. Split period into year/month or year/quarter when needed

    Args:
        sheet: Excel worksheet object.
        period: Period type ("monthly", "yearly", or "quarterly").
        account_columns: Number of leading columns used to identify accounts.

    Returns:
        Tuple of (data_table, account_hierarchy_table).
    """
    # Extract raw data and build account hierarchy
    rows = extract_data_rows(sheet, period=period, account_columns=account_columns)
    raw_data, account_hierarchy = build_wide_table(rows, account_columns)

    # Convert Cell objects to values
    data = convert_cells_to_values(raw_data)

    # Transform to long format
    data = data.melt(
        id_cols=[DATE_COLUMN], var_name=ACCOUNT_COLUMN, value_name=VALUE_COLUMN
    )

    # Handle period-specific transformations
    if period == "monthly":
        data = split_date_column(data, DATE_COLUMN)
    elif period == "yearly":
        data = data.rename(**{DATE_COLUMN: YEAR_COLUMN})
    elif period == "quarterly":
        data = split_quarter_column(data, DATE_COLUMN)

    return data, account_hierarchy


def read_sheet(filepath: Path, sheet_name: str) -> tuple[Tbl, Tbl]:
    """Read a specific sheet from RTN Excel file.

    Args:
        filepath: Path to the Excel file.
        sheet_name: Name of the sheet to read.

    Returns:
        Tuple of (data_table, account_hierarchy_table).

    Raises:
        ParseError: If the sheet name is unknown.
    """
    if sheet_name not in SHEET_CONFIGS:
        available_sheets = ", ".join(SHEET_CONFIGS.keys())
        raise ParseError(f"Unknown sheet '{sheet_name}'. Available: {available_sheets}")

    with log_step(logger, "read-rtn-sheet", filepath=filepath.name, sheet=sheet_name):
        workbook = open_workbook(filepath)
        return read_workbook_sheet(workbook, sheet_name)


def read_workbook_sheet(workbook: Any, sheet_name: str) -> tuple[Tbl, Tbl]:
    """Read a configured sheet from an already opened workbook.

    Args:
        workbook: Opened Excel workbook object.
        sheet_name: Name of the sheet to read.

    Returns:
        Tuple of (data_table, account_hierarchy_table).
    """
    config = SHEET_CONFIGS[sheet_name]
    sheet = workbook[sheet_name]

    data, account_hierarchy = read_sheet_data(
        sheet=sheet,
        period=config["period"],
        account_columns=config["account_columns"],
    )

    # Convert values according to the unit declared in the sheet.
    multiplier = detect_value_multiplier(sheet)
    data = data.assign(
        value=apply(
            data[VALUE_COLUMN][1:],
            lambda value: convert_value(value, multiplier),
        )
    )

    return data, account_hierarchy


def _normalize_index_code(code: str) -> str:
    """Normalize an Índice sheet code to match SHEET_CONFIGS keys.

    Strips trailing dots and dots before dashes:
    "1.1." -> "1.1", "1.5.-A" -> "1.5-A"
    """
    code = re.sub(r"\.(?=-)", "", code)
    return code.rstrip(".")


def _read_index_titles(workbook: Any) -> dict[str, str]:
    """Read sheet titles from workbook's Índice sheet."""
    index_sheet_name = next(
        (name for name in workbook.sheetnames if "ndice" in name), None
    )
    if index_sheet_name is None:
        return {}

    ws = workbook[index_sheet_name]
    titles: dict[str, str] = {}

    for row in ws.iter_rows(values_only=True):
        code_raw = row[0]
        description = row[1] if len(row) > 1 else None
        if not code_raw or not description:
            continue
        code = _normalize_index_code(str(code_raw).strip())
        if code in SHEET_CONFIGS:
            titles[code] = str(description).strip()

    return titles


def read_all_sheets(filepath: Path) -> dict[str, tuple[Tbl, Tbl, str | None]]:
    """Read all configured sheets from RTN Excel file.

    Args:
        filepath: Path to the Excel file.

    Returns:
        Dictionary mapping sheet names to (data_table, hierarchy_table, title)
        tuples.
    """
    workbook = open_workbook(filepath)
    titles = _read_index_titles(workbook)
    results = {}
    for sheet_name in SHEET_CONFIGS:
        if sheet_name not in workbook.sheetnames:
            continue
        data, accounts = read_workbook_sheet(workbook, sheet_name)
        results[sheet_name] = (data, accounts, titles.get(sheet_name))
    return results


def write_table_to_csv(data: Tbl, filepath: Path) -> None:
    """Write table to CSV file.

    Args:
        data: Table to write.
        filepath: Destination file path.
    """
    with filepath.open("w", encoding="utf-8", newline="\n") as file:
        writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_ALL)
        for row in data.transpose().iter_rows():
            writer.writerow(row)
