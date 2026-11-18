"""O build do lake pula, sem abrir nem ler a planilha, o que já está em dia."""

from __future__ import annotations

from pathlib import Path

import openpyxl
import pytest

pytest.importorskip("quantilica.analytics.lake")
pytest.importorskip("duckdb")

import rtn_fetcher.lake as lake_mod  # noqa: E402
from rtn_fetcher.lake import converter  # noqa: E402
from tests.test_lake import _build_synthetic_rtn_workbook  # noqa: E402


@pytest.fixture
def leituras(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Registra cada abertura e leitura da planilha."""
    vistas: list[str] = []

    def espia(nome: str, original):  # noqa: ANN001, ANN202
        def _f(*args, **kwargs):  # noqa: ANN002, ANN003
            vistas.append(nome)
            return original(*args, **kwargs)

        return _f

    for nome in ("open_workbook", "read_workbook_sheet", "to_polars"):
        monkeypatch.setattr(lake_mod, nome, espia(nome, getattr(lake_mod, nome)))
    monkeypatch.setattr(
        openpyxl, "load_workbook", espia("load_workbook", openpyxl.load_workbook)
    )
    return vistas


def _bruto(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    raw.mkdir()
    _build_synthetic_rtn_workbook(raw / "serie_historica_2026.xlsx")
    return raw


def test_segunda_rodada_com_alvo_nao_abre_a_planilha(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    res = converter.convert(raw, lake, datasets=["tabela-1-2-b"])
    assert not res.errors, res.errors
    assert (res.converted, res.skipped) == (1, 0)
    assert "open_workbook" in leituras

    leituras.clear()
    res2 = converter.convert(raw, lake, datasets=["tabela-1-2-b"])
    assert (res2.converted, res2.skipped, res2.errors) == (0, 1, [])
    assert leituras == []


def test_segunda_rodada_sem_alvo_nao_le_nenhuma_aba(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    res = converter.convert(raw, lake)
    assert (res.converted, res.skipped, res.errors) == (1, 0, [])

    leituras.clear()
    res2 = converter.convert(raw, lake)
    assert (res2.converted, res2.skipped, res2.errors) == (0, 1, [])
    # sem alvo é preciso listar as abas, mas nenhuma é lida nem convertida
    assert "read_workbook_sheet" not in leituras
    assert "to_polars" not in leituras


def test_alvo_ausente_da_planilha_abre_mas_nao_le_a_aba_em_dia(
    tmp_path: Path, leituras: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    alvos = ["tabela-1-2-b", "tabela-1-1"]  # a 1.1 não existe na planilha
    converter.convert(raw, lake, datasets=alvos)

    leituras.clear()
    res = converter.convert(raw, lake, datasets=alvos)
    assert (res.converted, res.skipped, res.errors) == (0, 1, [])
    assert "read_workbook_sheet" not in leituras
    assert "to_polars" not in leituras


def test_force_reconverte_lendo_a_planilha(tmp_path: Path, leituras: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tabela-1-2-b"])

    leituras.clear()
    res = converter.convert(raw, lake, datasets=["tabela-1-2-b"], force=True)
    assert (res.converted, res.skipped, res.errors) == (1, 0, [])
    assert "open_workbook" in leituras and "read_workbook_sheet" in leituras


def test_planilha_nova_e_convertida(tmp_path: Path, leituras: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tabela-1-2-b"])
    _build_synthetic_rtn_workbook(raw / "serie_historica_2026.xlsx")
    wb = openpyxl.load_workbook(raw / "serie_historica_2026.xlsx")
    wb["1.2-B"]["B6"] = 1.0  # mesmo nome, conteúdo novo
    wb.save(raw / "serie_historica_2026.xlsx")

    leituras.clear()
    res = converter.convert(raw, lake, datasets=["tabela-1-2-b"])
    assert (res.converted, res.skipped, res.errors) == (1, 0, [])
    assert "read_workbook_sheet" in leituras
