"""Tests for the optional lake inventory (``LakeConverter.inventory``)."""

from __future__ import annotations

from pathlib import Path

import openpyxl
import pytest

pytest.importorskip("quantilica.analytics.lake")

core_lake = pytest.importorskip("quantilica.core.lake")
if not hasattr(core_lake, "Planned"):
    pytest.skip(
        "quantilica-core ainda sem o contrato do inventário (Planned)",
        allow_module_level=True,
    )

from rtn_fetcher.lake import converter  # noqa: E402
from tests.test_lake import _build_synthetic_rtn_workbook  # noqa: E402

Planned = core_lake.Planned
converter_inventory = core_lake.converter_inventory


def _write(path: Path, content: bytes = b"") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _by_path(items: list[Planned]) -> dict[Path, Planned]:
    return {Path(item.path): item for item in items}


def test_inventory_routes_the_latest_workbook_to_its_datasets(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    wb = raw / "2026-09" / "serie_historica_set26.xlsx"
    wb.parent.mkdir(parents=True)
    _build_synthetic_rtn_workbook(wb)

    assert converter.inventory(raw) == [Planned(wb, dataset="tabela-1-2-b")]


def test_inventory_lists_one_item_per_sheet(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    wb = _build_synthetic_rtn_workbook(raw / "serie_historica_set26.xlsx")
    workbook = openpyxl.load_workbook(wb)
    workbook.create_sheet("2.1")
    workbook.save(wb)

    items = converter.inventory(raw)

    assert [item.dataset for item in items] == ["tabela-1-2-b", "tabela-2-1"]
    assert {item.path for item in items} == {wb}


def test_inventory_marks_twins_older_versions_and_non_tabular(
    tmp_path: Path,
) -> None:
    raw = tmp_path / "raw"
    newer = raw / "2026-09" / "serie_historica_set26.xlsx"
    older = raw / "2026-08" / "serie_historica_ago26.xlsx"
    for path in (newer, older):
        path.parent.mkdir(parents=True, exist_ok=True)
        _build_synthetic_rtn_workbook(path)
    twin = _write(raw / "2026-09" / "serie_historica_set26.csv")
    pdf = _write(raw / "2026-09" / "RTN_set26.pdf", b"%PDF-1.4\n")
    gif = _write(raw / "1995-08" / "ago1995anexoI.gif", b"GIF89a")
    page = _write(raw / "2026-09" / "api pública", b"<html></html>")
    sidecar = _write(raw / "2026-09" / "serie_historica_set26.xlsx.manifest.json")
    temp = _write(raw / "2026-09" / "serie_historica_set26.xlsx.tmp", b"resto")

    items = _by_path(converter.inventory(raw))

    assert items[newer].dataset == "tabela-1-2-b"
    assert items[newer].skip_reason is None
    # Série de outro mês: o conversor fica com a mais recente.
    assert items[older].skip_reason == "superado"
    # Mesmo conteúdo em outro formato da planilha escolhida.
    assert items[twin].skip_reason == "gemeo"
    assert items[pdf].skip_reason == "nao_tabular"
    assert items[gif].skip_reason == "nao_tabular"
    # Link sem extensão vira página HTML na árvore bruta.
    assert items[page].skip_reason == "nao_tabular"
    assert sidecar not in items
    assert temp not in items


def test_inventory_without_a_workbook_flags_tabular_gaps(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    csv = _write(raw / "2021-01" / "serie_historica_jan21.csv", b"a;b\n")
    pdf = _write(raw / "2021-01" / "RTN_jan21.pdf", b"%PDF-1.4\n")

    items = _by_path(converter.inventory(raw))

    # Sem planilha, o conversor não grava nada: o tabular fica sem destino
    # para a auditoria apontar a lacuna, e o documento é não tabular.
    assert items[csv].dataset is None
    assert items[csv].skip_reason is None
    assert items[pdf].skip_reason == "nao_tabular"


def test_inventory_unreadable_workbook_has_no_dataset(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    bad = _write(raw / "serie_historica_set26.xlsx", b"nao e xlsx")

    assert converter.inventory(raw) == [Planned(bad)]


def test_inventory_matches_convert(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    wb = raw / "2026-09" / "serie_historica_set26.xlsx"
    wb.parent.mkdir(parents=True)
    _build_synthetic_rtn_workbook(wb)
    _write(raw / "2026-09" / "serie_historica_set26.csv")
    _write(raw / "2026-09" / "RTN_set26.pdf", b"%PDF-1.4\n")
    lake = tmp_path / "lake"

    planned = {item.dataset for item in converter.inventory(raw) if item.dataset}
    res = converter.convert(raw, lake)

    assert not res.errors, res.errors
    written = {p.name for p in (lake / "rtn").iterdir() if p.is_dir()}
    assert planned == written == {"tabela-1-2-b"}


def test_inventory_is_the_optional_contract_member(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    raw.mkdir()
    wb = _build_synthetic_rtn_workbook(raw / "serie_historica_set26.xlsx")

    items = converter_inventory(converter, raw)

    assert items is not None
    assert [Path(item.path) for item in items] == [wb]


def test_inventory_of_missing_directory_is_empty(tmp_path: Path) -> None:
    assert converter.inventory(tmp_path / "nao-existe") == []
