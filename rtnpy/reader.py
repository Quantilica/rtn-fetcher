"""RTN Excel file reader and data transformation.

This module handles reading specific sheets from RTN Excel files and transforming
them into normalized long-format tables.
"""

import csv
from pathlib import Path
from typing import Any, Literal

from .account import expand_account_hierarchy, extract_account_column
from .constants import (
    ACCOUNT_COLUMN,
    DATE_COLUMN,
    MILLION_MULTIPLIER,
    MONTH_COLUMN,
    NA_VALUE,
    SHEET_CONFIGS,
    VALUE_COLUMN,
    YEAR_COLUMN,
)
from .excel import Sheet, open_workbook, cell_to_value
from .extract import build_account_data, extract_sheet_rows
from .table import Tbl, apply, get_header

PeriodType = Literal["monthly", "yearly"]


def convert_cells_to_values(data: Tbl) -> Tbl:
    """Convert all Cell objects in table to their Python values.

    Args:
        data: Table containing Excel Cell objects.

    Returns:
        Table with Cell objects converted to values.
    """
    return Tbl([apply(column, cell_to_value) for column in data.data])


def convert_to_millions(value: Any) -> int | None:
    """Convert numeric value to millions.

    Args:
        value: Value to convert (expected to be numeric or "n.a.").

    Returns:
        Value multiplied by 1,000,000, or None if value is "n.a.".
    """
    if value == NA_VALUE:
        return None
    return int(value) * MILLION_MULTIPLIER


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


def read_sheet_data(
    sheet: Sheet,
    min_row: int,
    max_row: int,
    drop_cols: list[int],
    period: PeriodType,
) -> tuple[Tbl, Tbl]:
    """Read and transform data from an Excel sheet.

    Performs the complete data transformation pipeline:
    1. Extract rows from sheet
    2. Remove unnecessary columns
    3. Rename first column to "date"
    4. Build account hierarchy
    5. Convert cells to values
    6. Melt to long format
    7. Split date into year/month (if monthly)

    Args:
        sheet: Excel worksheet object.
        min_row: First row to read.
        max_row: Last row to read.
        drop_cols: Indices of columns to drop.
        period: Period type ("monthly" or "yearly").

    Returns:
        Tuple of (data_table, account_hierarchy_table).
    """
    # Extract raw data
    raw_data = Tbl(extract_sheet_rows(sheet, min_row, max_row))

    # Remove unnecessary columns
    if drop_cols:
        raw_data = raw_data.drop_cols(drop_cols)

    # Rename first column to standard name
    raw_data.data[0][0] = DATE_COLUMN

    # Build account hierarchy
    account_cells = extract_account_column(raw_data)
    accounts_data = build_account_data(account_cells)
    account_hierarchy = expand_account_hierarchy(accounts_data)

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

    return data, account_hierarchy


def read_sheet(filepath: Path, sheet_name: str) -> tuple[Tbl, Tbl]:
    """Read a specific sheet from RTN Excel file.

    Args:
        filepath: Path to the Excel file.
        sheet_name: Name of the sheet to read (must be in SHEET_CONFIGS).

    Returns:
        Tuple of (data_table, account_hierarchy_table).

    Raises:
        ValueError: If sheet_name is not configured.
        KeyError: If sheet doesn't exist in workbook.
    """
    if sheet_name not in SHEET_CONFIGS:
        available_sheets = ", ".join(SHEET_CONFIGS.keys())
        raise ValueError(f"Unknown sheet '{sheet_name}'. Available: {available_sheets}")

    config = SHEET_CONFIGS[sheet_name]
    workbook = open_workbook(filepath)
    sheet = workbook[sheet_name]

    data, account_hierarchy = read_sheet_data(
        sheet=sheet,
        min_row=config["min_row"],
        max_row=config["max_row"],
        drop_cols=config["drop_cols"],
        period=config["period"],
    )

    # Convert values to millions
    data = data.assign(value=apply(data[VALUE_COLUMN][1:], convert_to_millions))

    return data, account_hierarchy


def read_all_sheets(filepath: Path) -> dict[str, tuple[Tbl, Tbl]]:
    """Read all configured sheets from RTN Excel file.

    Args:
        filepath: Path to the Excel file.

    Returns:
        Dictionary mapping sheet names to (data_table, account_hierarchy_table) tuples.
    """
    results = {}
    for sheet_name in SHEET_CONFIGS:
        results[sheet_name] = read_sheet(filepath, sheet_name)
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
