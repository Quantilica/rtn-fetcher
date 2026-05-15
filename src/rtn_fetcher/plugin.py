# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import asyncio
import json
import sqlite3
from pathlib import Path
from typing import Annotated

import typer
from bs4 import BeautifulSoup
from rich.console import Console

from rtn_fetcher import (
    download_latest_file,
    extract_publication_metadata,
    fetch_publications_metadata,
    read_all_sheets,
)
from rtn_fetcher.cli import (
    DATA_COLUMNS,
    _bounded_download,
    get_column_names,
    get_hierarchy_columns,
    make_period_date,
    write_header,
)

app = typer.Typer(help="Relatório de Transferências da União (RTN).")
fetch_sub = typer.Typer(help="Buscar metadados e baixar arquivos RTN.")
export_sub = typer.Typer(help="Exportar dados RTN para diferentes formatos.")
app.add_typer(fetch_sub, name="fetch")
app.add_typer(export_sub, name="export")

_DEFAULT_OUTPUT = Path("/data/rtn")
console = Console()

# Tabela de contas RTN usa 10 colunas de hierarquia (P_1..P_10).
HIERARCHY_COLUMNS = get_hierarchy_columns(10)


@fetch_sub.command("metadata")
def cmd_metadata(
    output: Annotated[
        Path,
        typer.Option(
            "-o",
            "--output",
            help="Diretório para metadata.html e metadata.json",
        ),
    ] = _DEFAULT_OUTPUT,
    encoding: Annotated[str, typer.Option("--encoding")] = "utf-8",
    force: Annotated[
        bool, typer.Option("--force", help="Rebaixar HTML mesmo se já existir")
    ] = False,
) -> None:
    """Buscar metadados HTML e gerar metadata.json."""
    out_html = output / "metadata.html"
    out_json = output / "metadata.json"

    if out_html.exists() and not force:
        metadata_html = out_html.read_text(encoding=encoding)
    else:
        with console.status("[cyan]Buscando metadados RTN...[/cyan]"):
            metadata_html = fetch_publications_metadata()
        out_html.parent.mkdir(parents=True, exist_ok=True)
        out_html.write_text(metadata_html, encoding=encoding)

    soup = BeautifulSoup(metadata_html, "html.parser")
    publications = extract_publication_metadata(soup)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(publications, ensure_ascii=False, indent=2),
        encoding=encoding,
    )
    console.print(
        f"[green]✓[/green] Salvas [bold]{len(publications)}[/bold] "
        f"publicações em [bold]{out_json}[/bold]"
    )


@fetch_sub.command("download")
def cmd_download(
    metadata: Annotated[
        Path, typer.Option("--metadata", help="Caminho do JSON de metadados")
    ] = _DEFAULT_OUTPUT / "metadata.json",
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de destino")
    ] = _DEFAULT_OUTPUT,
    encoding: Annotated[str, typer.Option("--encoding")] = "utf-8",
    concurrency: Annotated[
        int, typer.Option("--concurrency", help="Downloads simultâneos")
    ] = 4,
) -> None:
    """Baixar arquivos referenciados no metadata.json."""
    from quantilica_core.http import BROWSER_HEADERS, AsyncHttpClient

    if not metadata.exists():
        console.print(
            f"[red]Metadados não encontrados:[/red] {metadata}", stderr=True
        )
        raise typer.Exit(2)

    publications = json.loads(metadata.read_text(encoding=encoding))

    async def _run() -> None:
        semaphore = asyncio.Semaphore(concurrency)
        client = AsyncHttpClient(timeout=600.0, headers=BROWSER_HEADERS)
        tasks = [
            _bounded_download(
                pub, filename, url, client, output, encoding, semaphore
            )
            for pub in publications
            for filename, url in pub.get("links", {}).items()
        ]
        if tasks:
            await asyncio.gather(*tasks)

    with console.status("[cyan]Baixando arquivos RTN...[/cyan]"):
        asyncio.run(_run())


@fetch_sub.command("latest")
def cmd_latest(
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório de destino")
    ] = _DEFAULT_OUTPUT,
) -> None:
    """Baixar o arquivo RTN mais recente."""
    output.mkdir(parents=True, exist_ok=True)
    with console.status("[cyan]Baixando arquivo RTN mais recente...[/cyan]"):
        filepath = download_latest_file(output)
    console.print(
        f"[green]✓[/green] Arquivo RTN mais recente: [bold]{filepath}[/bold]"
    )


@export_sub.command("excel")
def cmd_export_excel(
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório com arquivos RTN")
    ] = _DEFAULT_OUTPUT,
    save_as: Annotated[
        Path, typer.Option("--save-as", help="Arquivo Excel de saída")
    ] = Path("rtn_processed.xlsx"),
) -> None:
    """Exportar dados RTN para Excel."""
    from openpyxl import Workbook

    output.mkdir(parents=True, exist_ok=True)
    with console.status("[cyan]Baixando e processando dados RTN...[/cyan]"):
        filepath = download_latest_file(output)
        results = read_all_sheets(filepath)

    wb = Workbook()
    wb.remove(wb.active)
    ws_data = wb.create_sheet(title="rtn_data")
    write_header(ws_data, DATA_COLUMNS)
    ws_acc = wb.create_sheet(title="rtn_accounts")
    write_header(ws_acc, HIERARCHY_COLUMNS)

    data_row = acc_row = 2
    for sheet_name, (data_tbl, accounts_tbl, sheet_title) in results.items():
        data_header = get_column_names(data_tbl)
        for row in data_tbl.iter_rows():
            if row == data_header:
                continue
            rd = dict(zip(data_header, row, strict=False))
            period_date = make_period_date(
                rd.get("year"), rd.get("month"), rd.get("quarter")
            )
            for col_idx, value in enumerate(
                [
                    f"{sheet_name}|{rd.get('account')}",
                    period_date,
                    rd.get("value"),
                ],
                1,
            ):
                ws_data.cell(row=data_row, column=col_idx, value=value)
            data_row += 1

        acc_header = get_column_names(accounts_tbl)
        for row in accounts_tbl.iter_rows():
            if row == acc_header:
                continue
            rd = dict(zip(acc_header, row, strict=False))
            account_code = rd.get("account_code")
            p_values = [rd.get(f"P_{i}") for i in range(1, 11)]
            for col_idx, value in enumerate(
                [
                    f"{sheet_name}|{account_code}",
                    sheet_name,
                    sheet_title,
                    account_code,
                    rd.get("account_name"),
                    rd.get("account_level"),
                    *p_values,
                ],
                1,
            ):
                ws_acc.cell(row=acc_row, column=col_idx, value=value)
            acc_row += 1

    wb.save(save_as)
    console.print(f"[green]✓[/green] Salvo em [bold]{save_as}[/bold]")


@export_sub.command("sqlite")
def cmd_export_sqlite(
    output: Annotated[
        Path, typer.Option("-o", "--output", help="Diretório com arquivos RTN")
    ] = _DEFAULT_OUTPUT,
    save_as: Annotated[
        Path, typer.Option("--save-as", help="Arquivo SQLite de saída")
    ] = Path("rtn_data.db"),
) -> None:
    """Exportar dados RTN para SQLite."""
    output.mkdir(parents=True, exist_ok=True)
    with console.status("[cyan]Baixando e processando dados RTN...[/cyan]"):
        filepath = download_latest_file(output)
        results = read_all_sheets(filepath)

    if save_as.exists():
        save_as.unlink()

    conn = sqlite3.connect(save_as)
    cursor = conn.cursor()
    hierarchy_cols = [f"P_{i}" for i in range(1, 11)]
    cols_sql = ", ".join(f"{col} TEXT" for col in hierarchy_cols)
    cursor.execute("CREATE TABLE rtn_data (key TEXT, date TEXT, value REAL)")
    cursor.execute(
        "CREATE TABLE rtn_accounts (key TEXT, sheet TEXT, sheet_title TEXT, "
        "account_code TEXT, account_name TEXT, account_level INTEGER, "
        f"{cols_sql})"
    )

    for sheet_name, (data_tbl, accounts_tbl, sheet_title) in results.items():
        data_header = get_column_names(data_tbl)
        for row in data_tbl.iter_rows():
            if row == data_header:
                continue
            rd = dict(zip(data_header, row, strict=False))
            period_date = make_period_date(
                rd.get("year"), rd.get("month"), rd.get("quarter")
            )
            cursor.execute(
                "INSERT INTO rtn_data VALUES (?, ?, ?)",
                (
                    f"{sheet_name}|{rd.get('account')}",
                    period_date,
                    rd.get("value"),
                ),
            )

        acc_header = get_column_names(accounts_tbl)
        for row in accounts_tbl.iter_rows():
            if row == acc_header:
                continue
            rd = dict(zip(acc_header, row, strict=False))
            account_code = rd.get("account_code")
            p_values = [rd.get(f"P_{i}") for i in range(1, 11)]
            placeholders = ", ".join(["?"] * 10)
            cursor.execute(
                "INSERT INTO rtn_accounts (key, sheet, sheet_title, "
                "account_code, account_name, account_level, "
                f"{', '.join(hierarchy_cols)}) "
                f"VALUES (?, ?, ?, ?, ?, ?, {placeholders})",
                [
                    f"{sheet_name}|{account_code}",
                    sheet_name,
                    sheet_title,
                    account_code,
                    rd.get("account_name"),
                    rd.get("account_level"),
                    *p_values,
                ],
            )

    conn.commit()
    conn.close()
    console.print(
        f"[green]✓[/green] Banco de dados salvo em [bold]{save_as}[/bold]"
    )
