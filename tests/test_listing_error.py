"""Falha de descoberta do catálogo não pode sumir atrás da lista fixa (sem rede)."""

from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import httpx2
import pytest
from quantilica.cli.sdk import CheckPlan, plan_listing_errors
from quantilica.core.exceptions import FetchError
from quantilica.core.http import HttpClient
from typer.testing import CliRunner

from rtn_fetcher import catalog
from rtn_fetcher.constants import (
    KNOWN_SERIE_HISTORICA_ANEXOS,
    RTN_THOT_ARQUIVOS_BASE_URL,
)
from rtn_fetcher.plugin import app, fetcher

runner = CliRunner()


def _xlsx_like() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", "<Types/>")
        zf.writestr("xl/workbook.xml", "<workbook/>" + "x" * 2000)
    return buf.getvalue()


_BODY = _xlsx_like()
_HEADERS = {
    "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "Last-Modified": "Tue, 29 Sep 2026 13:15:10 GMT",
    "Content-Length": str(len(_BODY)),
}
_RESERVA_URLS = {
    f"{RTN_THOT_ARQUIVOS_BASE_URL}/publicacao-anexo/{m['anexo_id']}"
    for m in KNOWN_SERIE_HISTORICA_ANEXOS.values()
}


def _handler(request: httpx2.Request) -> httpx2.Response:
    if str(request.url) in _RESERVA_URLS:
        if request.method == "HEAD":
            return httpx2.Response(200, headers=_HEADERS)
        return httpx2.Response(200, content=_BODY, headers=_HEADERS)
    return httpx2.Response(404)


@pytest.fixture(params=["api-503", "pagina-sem-cards"])
def catalogo_quebrado(request, monkeypatch):
    def api_fora() -> str:
        raise RuntimeError("HTTP 503 APEX down")

    monkeypatch.setattr(
        catalog,
        "fetch_publications_metadata",
        api_fora if request.param == "api-503" else lambda: "<html>layout novo</html>",
    )
    monkeypatch.setattr(
        fetcher,
        "client",
        HttpClient(attempts=1, transport=httpx2.MockTransport(_handler)),
    )
    catalog.clear_cache()
    yield
    catalog.clear_cache()


def test_sync_direto_baixa_a_reserva_mas_sai_3_com_o_erro(
    catalogo_quebrado, tmp_path: Path
) -> None:
    result = runner.invoke(app, ["sync", "-o", str(tmp_path)])

    assert result.exit_code == 3, result.output
    assert "rtn-catalogo" in result.output
    assert "catálogo do RTN indisponível" in result.output
    assert len(list(tmp_path.rglob("*.xlsx"))) == len(KNOWN_SERIE_HISTORICA_ANEXOS)


def test_check_registra_listing_error_e_sai_0_e_o_plano_falha_no_sync(
    catalogo_quebrado, tmp_path: Path
) -> None:
    plano_arq = tmp_path / "plano.json"
    result = runner.invoke(
        app, ["check", "-o", str(tmp_path / "bruto"), "--out", str(plano_arq)]
    )
    assert result.exit_code == 0, result.output

    plano = CheckPlan.from_json(plano_arq.read_text(encoding="utf-8"))
    (erro,) = plan_listing_errors(plano)
    assert erro[0] == "rtn-catalogo"
    item = next(i for i in plano.items if i.id == "rtn-catalogo")
    assert (item.action, item.reason) == ("skip-unavailable", "listing-error")
    assert item.entry["error_class"] and item.entry["error"]
    # A reserva segue no plano: as edições conhecidas ainda são baixadas.
    assert sum(i.action == "download" for i in plano.items) == len(
        KNOWN_SERIE_HISTORICA_ANEXOS
    )

    saida = tmp_path / "bruto"
    com_reserva = runner.invoke(
        app, ["sync", "-o", str(saida), "--from-plan", str(plano_arq)]
    )
    assert com_reserva.exit_code == 3, com_reserva.output
    assert "rtn-catalogo" in com_reserva.output

    # Só a sentinela no plano (nada a baixar): sai 1, nunca 0.
    so_erro = tmp_path / "so-erro.json"
    dados = json.loads(plano_arq.read_text(encoding="utf-8"))
    dados["items"] = [i for i in dados["items"] if i["id"] == "rtn-catalogo"]
    so_erro.write_text(json.dumps(dados), encoding="utf-8")
    sem_nada = runner.invoke(
        app, ["sync", "-o", str(saida), "--from-plan", str(so_erro)]
    )
    assert sem_nada.exit_code == 1, sem_nada.output


def test_download_da_sentinela_levanta_fetch_error(catalogo_quebrado, tmp_path: Path):
    (sentinela,) = [e for e in catalog.list_datasets("rtn") if e.get("listing_error")]
    with pytest.raises(FetchError, match="catálogo do RTN indisponível"):
        fetcher.download_entry(sentinela, tmp_path)


def test_segunda_rodada_com_reserva_em_dia_continua_com_erro(
    catalogo_quebrado, tmp_path: Path
) -> None:
    primeira = runner.invoke(app, ["sync", "-o", str(tmp_path)])
    assert primeira.exit_code == 3, primeira.output
    segunda = runner.invoke(app, ["sync", "-o", str(tmp_path)])
    assert segunda.exit_code == 3, segunda.output
    assert "rtn-catalogo" in segunda.output
