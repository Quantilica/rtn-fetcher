"""Excel file handling utilities.

This module provides abstraction over openpyxl for reading Excel workbooks
and extracting cell data.
"""

from pathlib import Path
from typing import Any

import openpyxl
from openpyxl.cell.cell import Cell
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet as Sheet

__all__ = [
    "Cell",
    "Sheet",
    "Workbook",
    "cell_to_value",
    "get_cell_indent",
    "open_workbook",
]


def open_workbook(filepath: Path) -> Workbook:
    """Open an Excel workbook from a file.

    Args:
        filepath: Path to the Excel file.

    Returns:
        Loaded workbook object.

    Raises:
        FileNotFoundError: If the file doesn't exist.
        openpyxl.utils.exceptions.InvalidFileException: If the file is invalid.
    """
    return openpyxl.load_workbook(filepath, data_only=True)


def get_cell_indent(cell: Cell) -> float:
    """Extract the indentation level of a cell.

    This is used to determine the hierarchical level of account names
    in RTN spreadsheets.

    Args:
        cell: Excel cell object.

    Returns:
        Indentation level as a float.
    """
    return cell.alignment.indent if cell.alignment else 0.0


def cell_to_value(cell: Cell | Any) -> Any:
    """Convert cell object to its Python value.

    Args:
        cell: Excel cell object or any value.

    Returns:
        Cell value if it's a Cell object, otherwise returns the input as-is.
    """
    return cell.value if isinstance(cell, Cell) else cell
