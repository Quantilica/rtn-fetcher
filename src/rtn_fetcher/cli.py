#!/usr/bin/env python3
"""Unified CLI tool for RTN data fetching and export operations.

Provides these subcommand groups:
- fetch: metadata, download, latest
- export: excel, sqlite

Usage examples:
  rtn-fetcher fetch metadata
  rtn-fetcher fetch download
  rtn-fetcher fetch latest
  rtn-fetcher export excel
  rtn-fetcher export sqlite
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sqlite3
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from quantilica_core.http import BROWSER_HEADERS, AsyncHttpClient
from quantilica_core.logging import configure_cli_logging

from rtn_fetcher import (
    Tbl,
    download_latest_file,
    extract_publication_metadata,
    fetch_publications_metadata,
    logger,
    read_all_sheets,
)
from rtn_fetcher.fetcher import download_publication_link

DEFAULT_DATA_DIR = Path("/data/rtn")

HEADER_FONT = Font(bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(fill_type="solid", fgColor="1F4E79")

DATA_COLUMNS = ["key", "date", "value"]


def get_hierarchy_columns(p_column_count: int) -> list[str]:
    """Build the hierarchy column headers based on the number of P_ columns."""
    return [
        "key",
        "sheet",
        "sheet_title",
        "account_code",
        "account_name",
        "account_level",
        *(f"P_{i}" for i in range(1, p_column_count + 1)),
    ]


def make_period_date(year, month, quarter) -> date | None:
    if year is None:
        return None
    if quarter is not None:
        return date(int(year), (int(quarter) - 1) * 3 + 1, 1)
    if month is not None:
        return date(int(year), int(month), 1)
    return date(int(year), 1, 1)


def write_header(ws, columns: list[str]) -> None:
    for col_idx, name in enumerate(columns, start=1):
        cell = ws.cell(row=1, column=col_idx, value=name)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL


def get_column_names(table: Tbl) -> list[str]:
    return [col[0] for col in table.data]


def get_p_column_count(columns: list[str]) -> int:
    """Count how many P_i hierarchy columns exist in the column list."""
    count = 0
    for i in range(1, 11):
        if f"P_{i}" in columns:
            count += 1
        else:
            break
    return count


def cmd_metadata(args: argparse.Namespace) -> int:
    """Fetch metadata HTML and generate metadata.json."""
    dest = args.output
    out_html = dest / "metadata.html"
    out_json = dest / "metadata.json"

    if out_html.exists() and not args.force:
        with out_html.open("r", encoding=args.encoding) as f:
            metadata_html = f.read()
    else:
        metadata_html = fetch_publications_metadata()
        out_html.parent.mkdir(parents=True, exist_ok=True)
        with out_html.open("w", encoding=args.encoding) as f:
            f.write(metadata_html)

    soup = BeautifulSoup(metadata_html, "html.parser")
    publications = extract_publication_metadata(soup)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with out_json.open("w", encoding=args.encoding) as f:
        json.dump(publications, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(publications)} publications to {out_json}")
    return 0


async def _bounded_download(
    pub: dict,
    filename: str,
    url: str,
    client: AsyncHttpClient,
    dest_root: Path,
    encoding: str,
    semaphore: asyncio.Semaphore,
    state: dict,
) -> None:
    """Download one publication link, gated by ``semaphore``."""
    ano = pub.get("ano_publicacao")
    mes = pub.get("mes_publicacao")
    dest_dir = dest_root / f"{ano}-{mes:0>2}"
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_file = dest_dir / filename
    if dest_file.exists():
        state["count"] += 1
        logger.info(f"[{state['count']}/{state['total']}] Skipped {filename} (already exists)")
        return

    async with semaphore:
        state["count"] += 1
        current = state["count"]
        logger.info(f"[{current}/{state['total']}] Downloading {filename}...")
        try:
            await download_publication_link(
                client, url, dest_file, text_encoding=encoding
            )
        except Exception as exc:
            logger.error(f"[{current}/{state['total']}] Failed to download {url}: {exc}")


def cmd_download(args: argparse.Namespace) -> int:
    """Download files referenced in metadata.json."""
    metadata_path = args.output / "metadata.json"
    if not metadata_path.exists():
        logger.error(f"Metadata file not found: {metadata_path}")
        return 2

    with metadata_path.open("r", encoding=args.encoding) as f:
        publications = json.load(f)

    total = sum(len(pub.get("links", {})) for pub in publications)
    state = {"count": 0, "total": total}

    async def _run_async_downloads() -> None:
        semaphore = asyncio.Semaphore(args.concurrency)
        client = AsyncHttpClient(timeout=600.0, headers=BROWSER_HEADERS)
        tasks = [
            _bounded_download(
                pub,
                filename,
                url,
                client,
                args.output,
                args.encoding,
                semaphore,
                state,
            )
            for pub in publications
            for filename, url in pub.get("links", {}).items()
        ]
        if tasks:
            await asyncio.gather(*tasks)

    asyncio.run(_run_async_downloads())
    return 0


def cmd_latest(args: argparse.Namespace) -> int:
    """Download latest single file."""
    dest = args.output
    dest.mkdir(parents=True, exist_ok=True)
    filepath = download_latest_file(dest)
    logger.info(f"Latest RTN file: {filepath}")
    return 0


def cmd_export_excel(args: argparse.Namespace) -> int:
    """Export RTN data to Excel."""
    data_dir = args.output
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Checking for latest RTN file...")
    filepath = download_latest_file(data_dir)
    logger.info(f"Using file: {filepath}")

    logger.info(f"Reading all sheets from {filepath}...")
    results = read_all_sheets(filepath)

    # Detect max hierarchy depth across all sheets
    max_p_columns = 0
    for _, (_, accounts_tbl, _) in results.items():
        acc_header = get_column_names(accounts_tbl)
        p_count = get_p_column_count(acc_header)
        max_p_columns = max(max_p_columns, p_count)

    output_path = Path(args.save_as)
    wb = Workbook()
    wb.remove(wb.active)

    ws_data = wb.create_sheet(title="rtn_data")
    write_header(ws_data, DATA_COLUMNS)
    data_row = 2

    ws_acc = wb.create_sheet(title="rtn_accounts")
    hierarchy_columns = get_hierarchy_columns(max_p_columns)
    write_header(ws_acc, hierarchy_columns)
    acc_row = 2

    for sheet_name, (data_tbl, accounts_tbl, sheet_title) in results.items():
        logger.info(f"Processing sheet {sheet_name}...")

        data_header = get_column_names(data_tbl)
        for row in data_tbl.iter_rows():
            if row == data_header:
                continue
            row_dict = dict(zip(data_header, row, strict=False))
            account = row_dict.get("account")
            period_date = make_period_date(
                row_dict.get("year"),
                row_dict.get("month"),
                row_dict.get("quarter"),
            )
            data_values = [
                f"{sheet_name}|{account}",
                period_date,
                row_dict.get("value"),
            ]
            for col_idx, value in enumerate(data_values, start=1):
                ws_data.cell(row=data_row, column=col_idx, value=value)
            data_row += 1

        acc_header = get_column_names(accounts_tbl)
        p_column_count = get_p_column_count(acc_header)
        for row in accounts_tbl.iter_rows():
            if row == acc_header:
                continue
            row_dict = dict(zip(acc_header, row, strict=False))
            account_code = row_dict.get("account_code")
            p_values = [
                row_dict.get(f"P_{i}") for i in range(1, p_column_count + 1)
            ]
            for col_idx, value in enumerate(
                [
                    f"{sheet_name}|{account_code}",
                    sheet_name,
                    sheet_title,
                    account_code,
                    row_dict.get("account_name"),
                    row_dict.get("account_level"),
                    *p_values,
                ],
                start=1,
            ):
                ws_acc.cell(row=acc_row, column=col_idx, value=value)
            acc_row += 1

    wb.save(output_path)
    logger.info(f"Saved to {output_path}")
    return 0


def cmd_export_sqlite(args: argparse.Namespace) -> int:
    """Export RTN data to SQLite database."""
    data_dir = args.output
    data_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Checking for latest RTN file...")
    filepath = download_latest_file(data_dir)
    logger.info(f"Using file: {filepath}")

    logger.info(f"Reading all sheets from {filepath}...")
    results = read_all_sheets(filepath)

    db_path = Path(args.save_as)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE rtn_data (
            key   TEXT,
            date  TEXT,
            value REAL
        )
    """
    )

    # Detect max hierarchy depth across all sheets
    max_p_columns = 0
    for _, (_, accounts_tbl, _) in results.items():
        acc_header = get_column_names(accounts_tbl)
        p_count = get_p_column_count(acc_header)
        max_p_columns = max(max_p_columns, p_count)

    hierarchy_cols = [f"P_{i}" for i in range(1, max_p_columns + 1)]
    cols_sql = ", ".join(f"{col} TEXT" for col in hierarchy_cols)
    cursor.execute(
        f"""
        CREATE TABLE rtn_accounts (
            key           TEXT,
            sheet         TEXT,
            sheet_title   TEXT,
            account_code  TEXT,
            account_name  TEXT,
            account_level INTEGER,
            {cols_sql}
        )
    """
    )

    for sheet_name, (data_tbl, accounts_tbl, sheet_title) in results.items():
        logger.info(f"Processing sheet {sheet_name}...")

        data_header = get_column_names(data_tbl)
        for row in data_tbl.iter_rows():
            if row == data_header:
                continue
            row_dict = dict(zip(data_header, row, strict=False))
            account = row_dict.get("account")
            period_date = make_period_date(
                row_dict.get("year"),
                row_dict.get("month"),
                row_dict.get("quarter"),
            )
            cursor.execute(
                "INSERT INTO rtn_data (key, date, value) VALUES (?, ?, ?)",
                (
                    f"{sheet_name}|{account}",
                    period_date,
                    row_dict.get("value"),
                ),
            )

        acc_header = get_column_names(accounts_tbl)
        p_column_count = get_p_column_count(acc_header)
        for row in accounts_tbl.iter_rows():
            if row == acc_header:
                continue
            row_dict = dict(zip(acc_header, row, strict=False))
            account_code = row_dict.get("account_code")
            p_values = [
                row_dict.get(f"P_{i}") for i in range(1, p_column_count + 1)
            ]
            # Pad with None to match the max_p_columns for consistency
            p_values.extend([None] * (max_p_columns - p_column_count))
            placeholders = ", ".join(["?"] * max_p_columns)
            cursor.execute(
                f"INSERT INTO rtn_accounts (key, sheet, sheet_title, "
                f"account_code, account_name, account_level, "
                f"{', '.join(hierarchy_cols)}) "
                f"VALUES (?, ?, ?, ?, ?, ?, {placeholders})",
                [
                    f"{sheet_name}|{account_code}",
                    sheet_name,
                    sheet_title,
                    account_code,
                    row_dict.get("account_name"),
                    row_dict.get("account_level"),
                    *p_values,
                ],
            )

    conn.commit()
    conn.close()
    logger.info(f"Database saved to {db_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rtn-fetcher",
        description="RTN data helper CLI - fetch and export utilities",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Exibir logs detalhados (DEBUG)",
    )
    sub = parser.add_subparsers(dest="group", required=True)

    p_fetch = sub.add_parser("fetch", help="Fetch metadata and download files")
    fetch_sub = p_fetch.add_subparsers(dest="command", required=True)

    p_meta = fetch_sub.add_parser(
        "metadata",
        help="Fetch metadata HTML and generate metadata.json",
    )
    p_meta.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Output directory for metadata (default: {DEFAULT_DATA_DIR})",
    )
    p_meta.add_argument("--encoding", default="utf-8", help="File encoding")
    p_meta.add_argument(
        "--force",
        action="store_true",
        help="Refetch HTML even if it exists",
    )
    p_meta.set_defaults(func=cmd_metadata)

    p_dl = fetch_sub.add_parser(
        "download",
        help="Download files referenced in metadata.json",
    )
    p_dl.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Destination root directory (default: {DEFAULT_DATA_DIR})",
    )
    p_dl.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding for HTML files",
    )
    p_dl.add_argument(
        "--concurrency",
        type=int,
        default=4,
        help="Maximum concurrent downloads (default: 4)",
    )
    p_dl.set_defaults(func=cmd_download)

    p_latest = fetch_sub.add_parser(
        "latest", help="Download latest single file"
    )
    p_latest.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Destination directory (default: {DEFAULT_DATA_DIR})",
    )
    p_latest.set_defaults(func=cmd_latest)

    p_export = sub.add_parser(
        "export", help="Export RTN data to various formats"
    )
    export_sub = p_export.add_subparsers(dest="command", required=True)

    p_excel = export_sub.add_parser("excel", help="Export RTN data to Excel")
    p_excel.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Directory containing RTN files (default: {DEFAULT_DATA_DIR})",
    )
    p_excel.add_argument(
        "--save-as",
        dest="save_as",
        type=Path,
        default=Path("rtn_processed.xlsx"),
        help="Output Excel file path (default: rtn_processed.xlsx)",
    )
    p_excel.set_defaults(func=cmd_export_excel)

    p_sqlite = export_sub.add_parser(
        "sqlite", help="Export RTN data to SQLite"
    )
    p_sqlite.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"Directory containing RTN files (default: {DEFAULT_DATA_DIR})",
    )
    p_sqlite.add_argument(
        "--save-as",
        dest="save_as",
        type=Path,
        default=Path("rtn_data.db"),
        help="Output SQLite database path (default: rtn_data.db)",
    )
    p_sqlite.set_defaults(func=cmd_export_sqlite)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    configure_cli_logging(verbose=args.verbose)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
