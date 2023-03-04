from typing import Any
from pathlib import Path
import openpyxl

Workbook = openpyxl.workbook.workbook.Workbook
Sheet = openpyxl.worksheet.worksheet.Worksheet
Cell = openpyxl.cell.cell.Cell


def openwb(filepath: Path) -> Workbook:
    wb = openpyxl.load_workbook(filepath)
    return wb


def get_indent(cell: Cell) -> float:
    return cell.alignment.indent


def to_value(cell: Cell) -> Any:
    return cell.value if isinstance(cell, Cell) else cell
