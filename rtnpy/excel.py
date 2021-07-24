import os
from typing import Union
import pathlib
import openpyxl

Filepath = Union[pathlib.Path, str, os.PathLike]
Workbook = openpyxl.workbook.workbook.Workbook
Sheet = openpyxl.worksheet.worksheet.Worksheet
Cell = openpyxl.cell.cell.Cell


def openwb(filepath: Filepath) -> Workbook:
    wb = openpyxl.load_workbook(filepath)
    return wb


def get_indent(cell: Cell) -> float:
    return cell.alignment.indent


def to_value(cell):
    return cell.value if isinstance(cell, Cell) else cell
