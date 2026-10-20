"""Regressão: ``rtn sync`` sem grupo baixava todos os ~2.000 arquivos.

A página de publicações do RTN lista a série histórica mensal, planilhas de
anexos antigas e boletins em PDF/GIF/DOC desde 1995. Sem grupo, ``sync`` e
``check`` agora usam só o grupo ``rtn`` (planilhas da série histórica); os
demais exigem ``rtn-anexos``, ``rtn-publicacoes`` ou os aliases
``planilhas``/``todos``.
"""

from __future__ import annotations

import pytest

from rtn_fetcher import catalog

_HTML = """
<div class="card-rtn" data-id-publicacao="1" data-nr-ano="2026"
     data-id-periodicidade-periodo="8">
  <h3>RTN Agosto 2026</h3><p>Resumo</p>
  <a href="https://x/29326">serie_historica_ago26.xlsx</a>
  <a href="https://x/29327">RTN_ago26.pdf</a>
  <a href="http://apiapex/docs">API pública</a>
</div>
<div class="card-rtn" data-id-publicacao="2" data-nr-ano="2021"
     data-id-periodicidade-periodo="1">
  <h3>RTN Janeiro 2021</h3><p>Resumo</p>
  <a href="https://x/11876">serie_historica_jan21_nova estrutura.xlsx</a>
  <a href="https://x/11877">Série Histórica jan21.CSV</a>
</div>
<div class="card-rtn" data-id-publicacao="3" data-nr-ano="2015"
     data-id-periodicidade-periodo="3">
  <h3>RTN Março 2015</h3><p>Resumo</p>
  <a href="https://x/127">Anexos RTN mar_2015.xlsx</a>
</div>
<div class="card-rtn" data-id-publicacao="4" data-nr-ano="1996"
     data-id-periodicidade-periodo="1">
  <h3>RTN Janeiro 1996</h3><p>Resumo</p>
  <a href="https://x/1">Tabela1 - Série Histórica.xls</a>
  <a href="https://x/2">grafico1.gif</a>
  <a href="https://x/3">nota.doc</a>
</div>
"""


@pytest.fixture
def fake_page(monkeypatch):
    calls = []

    def _fetch() -> str:
        calls.append(1)
        return _HTML

    monkeypatch.setattr(catalog, "fetch_publications_metadata", _fetch)
    catalog.clear_cache()
    yield calls
    catalog.clear_cache()


def _ids(entries):
    return sorted(e["id"] for e in entries)


@pytest.mark.parametrize(
    ("filename", "group"),
    [
        ("serie_historica_ago26.xlsx", "rtn"),
        ("serie_historica_jan21_nova estrutura.xlsx", "rtn"),
        ("Série Histórica jan21.CSV", "rtn"),
        ("Anexos RTN mar_2015.xlsx", "rtn-anexos"),
        ("Tabela1 - Série Histórica.xls", "rtn-anexos"),
        ("RTN_ago26.pdf", "rtn-publicacoes"),
        ("grafico1.gif", "rtn-publicacoes"),
        ("nota.doc", "rtn-publicacoes"),
        ("API pública", "rtn-publicacoes"),
    ],
)
def test_classify_entry(filename, group):
    assert catalog.classify_entry(filename) == group


def test_grupo_padrao_so_tem_planilhas_da_serie_historica(fake_page):
    entries = catalog.list_datasets("rtn")
    assert _ids(entries) == [
        "Série Histórica jan21.CSV",
        "serie_historica_ago26.xlsx",
        "serie_historica_jan21_nova estrutura.xlsx",
    ]
    assert {e["ext"] for e in entries} <= {"xlsx", "csv"}


def test_demais_grupos_e_lista_completa(fake_page):
    assert _ids(catalog.list_datasets("rtn-anexos")) == [
        "Anexos RTN mar_2015.xlsx",
        "Tabela1 - Série Histórica.xls",
    ]
    publicacoes = catalog.list_datasets("rtn-publicacoes")
    assert _ids(publicacoes) == [
        "API pública",
        "RTN_ago26.pdf",
        "grafico1.gif",
        "nota.doc",
    ]
    # Link sem extensão não vira mais ".xlsx".
    api = next(e for e in publicacoes if e["id"] == "API pública")
    assert api["ext"] == "html"
    assert len(catalog.list_datasets()) == 9


def test_pagina_baixada_uma_vez_por_processo(fake_page):
    for group in (None, "rtn", "rtn-anexos", "rtn-publicacoes", "rtn"):
        catalog.list_datasets(group)
    assert len(fake_page) == 1


def test_grupo_desconhecido(fake_page):
    with pytest.raises(ValueError):
        catalog.list_datasets("xpto")


def test_sem_grupo_resolve_so_serie_historica():
    from rtn_fetcher.plugin import fetcher

    assert fetcher.resolve_groups(None) == ["rtn"]
    assert fetcher.resolve_groups([]) == ["rtn"]
    assert fetcher.resolve_groups(["rtn-publicacoes"]) == ["rtn-publicacoes"]
    assert fetcher.resolve_groups(["planilhas"]) == ["rtn", "rtn-anexos"]
    assert fetcher.resolve_groups(["todos"]) == [
        "rtn",
        "rtn-anexos",
        "rtn-publicacoes",
    ]


def test_sync_dry_run_sem_grupo_nao_lista_pdf_nem_gif(fake_page):
    from typer.testing import CliRunner

    from rtn_fetcher.plugin import app

    result = CliRunner().invoke(app, ["sync", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "3 arquivo(s) listado(s)" in result.output
    assert ".pdf" not in result.output
    assert ".gif" not in result.output

    result = CliRunner().invoke(app, ["sync", "todos", "--dry-run"])
    assert result.exit_code == 0, result.output
    assert "9 arquivo(s) listado(s)" in result.output
