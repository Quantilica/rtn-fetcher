# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Testes para DataRepository do rtn-fetcher."""

import datetime as dt
from pathlib import Path

from rtn_fetcher.storage import DataRepository


def test_path_for_entry_serie_historica_with_timestamp(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path)
    entry = {
        "group": "rtn",
        "ano_publicacao": 2025,
        "mes_publicacao": 8,
        "filename": "serie_historica_ago25.xlsx",
        "ext": "xlsx",
    }
    path = repo.path_for_entry(entry, last_modified=dt.date(2025, 9, 28))
    expected = tmp_path / "serie-historica" / "rtn_2025-08@20250928.xlsx"
    assert path == expected


def test_path_for_entry_serie_historica_without_timestamp(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path)
    entry = {
        "group": "rtn",
        "ano_publicacao": 2024,
        "mes_publicacao": 12,
        "filename": "serie_historica.xlsx",
    }
    path = repo.path_for_entry(entry)
    # A7 sources: fallback to today when last_modified is None (ADR 2026-10-30)
    today = dt.date.today()
    expected = tmp_path / "serie-historica" / f"rtn_2024-12@{today:%Y%m%d}.xlsx"
    assert path == expected


def test_path_for_entry_anexos(tmp_path: Path) -> None:
    repo = DataRepository(tmp_path)
    entry = {
        "group": "rtn-anexos",
        "ano_publicacao": 2024,
        "mes_publicacao": 5,
        "filename": "Anexo_RTN_Mai_2024.xlsx",
    }
    path = repo.path_for_entry(entry, last_modified=dt.date(2024, 6, 1))
    expected = tmp_path / "rtn-anexos" / "Anexo_RTN_Mai_2024_2024-05@20240601.xlsx"
    assert path == expected
