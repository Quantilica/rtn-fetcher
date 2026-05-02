"""Data extraction from HTML metadata and Excel spreadsheets.

This module provides functions to extract RTN publication metadata from HTML
pages and account data from Excel spreadsheets.
"""

import re
from typing import Any

from bs4 import BeautifulSoup

from .account import (
    clean_account_name,
    generated_account_code,
    normalize_account_code,
    parse_account_name,
)
from .constants import HIERARCHY_SEPARATOR, MIN_ROW_CELLS, SPECIAL_ACCOUNT_MARKER
from .excel import Cell, Sheet, get_cell_indent
from .table import Matrix, Tbl


def deduplicate_account_rows(account_rows: list[list[Any]]) -> None:
    """Make repeated account codes unique while preserving first occurrences."""
    seen: dict[str, int] = {}

    for index, account_code in enumerate(account_rows[0][1:], start=1):
        count = seen.get(account_code, 0) + 1
        seen[account_code] = count

        if count == 1:
            continue

        unique_code = f"{account_code}#{count}"
        account_rows[0][index] = unique_code


def extract_available_periods(soup: BeautifulSoup) -> list[tuple[str, str]]:
    """Extract available year-month combinations from metadata page.

    Args:
        soup: BeautifulSoup object of the RTN metadata page.

    Returns:
        List of (year, month) tuples for available publications.
    """
    periods = []
    year_options = soup.select("select#filtro-ano option")
    month_options = soup.select("select#filtro-mes option")

    for year_option in year_options:
        year_text = year_option.text
        for month_option in month_options:
            years_attr = month_option.get("data-nr-ano", "")
            if isinstance(years_attr, str) and year_text in years_attr.split(":"):
                periods.append((year_text, month_option.text))

    return periods


def extract_publication_metadata(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Extract publication metadata from RTN HTML page.

    Parses the card elements containing publication information including
    titles, dates, summaries, and download links.

    Args:
        soup: BeautifulSoup object of the RTN publications page.

    Returns:
        List of dictionaries containing publication metadata:
        - id_publicacao: Publication ID
        - ano_publicacao: Publication year
        - mes_publicacao: Publication month (as number)
        - titulo: Publication title
        - resumo: Publication summary/description
        - links: Dict mapping link text to URLs
    """
    publications = []
    cards = soup.select("div.card-rtn")

    for card in cards:
        publication_id = card.get("data-id-publicacao", "")
        publication_year = card.get("data-nr-ano", "")
        publication_month = card.get("data-id-periodicidade-periodo", "")

        title_element = card.select_one("h3")
        title_text = ""
        if title_element:
            title_string = title_element.find(string=True, recursive=False)
            if title_string:
                title_text = title_string.strip(" \n")

        summary_element = card.select_one("p")
        summary_text = ""
        if summary_element:
            summary_text = re.sub("[ \n]+", " ", summary_element.text.strip())

        links = {}
        for link in card.select("a"):
            link_text = re.sub("[ \n]+", " ", link.text.strip(" \n"))
            link_href = link.get("href", "")
            if link_text and link_href:
                links[link_text] = link_href

        publication = {
            "id_publicacao": publication_id,
            "ano_publicacao": publication_year,
            "mes_publicacao": publication_month,
            "titulo": title_text,
            "resumo": summary_text,
            "links": links,
        }
        publications.append(publication)

    return publications


def extract_sheet_rows(
    sheet: Sheet,
    min_row: int = 1,
    max_row: int = 1_048_576,
    min_col: int = 1,
    max_col: int | None = None,
    min_filled_cells: int = MIN_ROW_CELLS,
) -> Matrix:
    """Extract non-empty rows from an Excel sheet.

    Filters out rows that are completely empty or have fewer than the minimum
    number of cells required.

    Args:
        sheet: Excel worksheet object.
        min_row: First row to read (1-indexed).
        max_row: Last row to read (1-indexed).

    Returns:
        List of rows, where each row is a list of Cell objects.
    """
    rows = []

    for row in sheet.iter_rows(
        min_row=min_row,
        max_row=max_row,
        min_col=min_col,
        max_col=max_col,
    ):
        if all(cell.value is None for cell in row):
            continue

        non_empty_cells = [cell for cell in row if cell.value is not None]
        if len(non_empty_cells) < min_filled_cells:
            continue

        rows.append(list(row))

    return rows


def build_account_data(account_cells: list[Cell]) -> Tbl:
    """Build hierarchical account data from Excel cells.

    Uses cell indentation to determine the hierarchical level of each account.
    Automatically generates hierarchical codes when they're not explicitly
    provided in the cell text.

    Args:
        account_cells: List of Excel cells containing account names.

    Returns:
        Table with columns [account_code, account_name, account_level].
        account_code uses "=>" as separator (e.g., "1=>2=>3").

    Examples:
        Cell with indent 0: "1. Receitas" -> code "1", level 1
        Cell with indent 1: "1.1 Receitas Correntes" -> code "1=>1", level 2
    """
    account_rows: list[list[Any]] = [
        ["account_code"],
        ["account_name"],
        ["account_level"],
    ]

    last_code_parts = (0,)
    indent_stack = (0.0,)

    for cell in account_cells:
        current_indent = get_cell_indent(cell)

        # Determine hierarchy level based on indentation changes
        if current_indent > indent_stack[-1]:
            # Going deeper in hierarchy
            indent_stack = (*indent_stack, current_indent)
            last_code_parts = (*last_code_parts, 0)
        elif cell.value and SPECIAL_ACCOUNT_MARKER in str(cell.value):
            # Special marker maintains same level
            indent_stack = (*indent_stack, current_indent)
            last_code_parts = (*last_code_parts, 0)
        elif current_indent < indent_stack[-1]:
            # Going back up in hierarchy
            while current_indent < indent_stack[-1]:
                indent_stack = indent_stack[:-1]
                last_code_parts = last_code_parts[:-1]

        # Increment counter at current level
        last_code_parts = last_code_parts[:-1] + (last_code_parts[-1] + 1,)

        # Parse account code and name from cell text
        cell_value = str(cell.value) if cell.value else ""
        account_code, account_name = parse_account_name(cell_value)

        # Generate code if not provided
        if not account_code:
            account_code = generated_account_code(last_code_parts)
            account_level = len(last_code_parts)
        else:
            account_level = len(account_code.split(HIERARCHY_SEPARATOR))

        account_rows[0].append(account_code)
        account_rows[1].append(account_name)
        account_rows[2].append(account_level)

    deduplicate_account_rows(account_rows)
    return Tbl(account_rows)


def build_account_data_from_columns(
    code_cells: list[Cell],
    name_cells: list[Cell],
) -> Tbl:
    """Build hierarchical account data from separate code and name columns."""
    account_rows: list[list[Any]] = [
        ["account_code"],
        ["account_name"],
        ["account_level"],
    ]

    last_code_parts = (0,)
    indent_stack = (0.0,)

    for code_cell, name_cell in zip(code_cells, name_cells):
        current_indent = get_cell_indent(name_cell)

        if current_indent > indent_stack[-1]:
            indent_stack = (*indent_stack, current_indent)
            last_code_parts = (*last_code_parts, 0)
        elif current_indent < indent_stack[-1]:
            while current_indent < indent_stack[-1]:
                indent_stack = indent_stack[:-1]
                last_code_parts = last_code_parts[:-1]

        last_code_parts = last_code_parts[:-1] + (last_code_parts[-1] + 1,)

        account_code = normalize_account_code(code_cell.value)
        account_name = clean_account_name(
            str(name_cell.value) if name_cell.value else ""
        )

        if not account_code:
            account_code = generated_account_code(last_code_parts)
            account_level = len(last_code_parts)
        else:
            account_level = len(account_code.split(HIERARCHY_SEPARATOR))

        account_rows[0].append(account_code)
        account_rows[1].append(account_name)
        account_rows[2].append(account_level)

    deduplicate_account_rows(account_rows)
    return Tbl(account_rows)
