# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Testes de resiliência do rtn-fetcher contra quedas do sisweb e APEX."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from quantilica.core.exceptions import FetchError, InvalidPayloadSignatureError
from quantilica.core.http import HttpStatusError

from rtn_fetcher import catalog, fetcher
from rtn_fetcher.constants import (
    HTTP_DATE_FORMAT,
    KNOWN_SERIE_HISTORICA_ANEXOS,
    RTN_FILE_BASE_URL,
    RTN_THOT_ARQUIVOS_BASE_URL,
)


class DummyResponse:
    def __init__(
        self,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        url: str = "https://cdn.tesouro.gov.br/dummy.xlsx",
    ):
        self.status_code = status_code
        self.headers = headers or {}
        self.url = url


def test_resolve_latest_serie_historica_sisweb_success():
    """Quando o permalink sisweb responde 200, ele é utilizado diretamente."""
    mock_client = MagicMock()
    now_str = "Thu, 29 Oct 2026 18:31:33 GMT"
    mock_client.head_or_get.return_value = DummyResponse(
        status_code=200,
        headers={"Last-Modified": now_str},
        url=RTN_FILE_BASE_URL,
    )

    url, mod_date, params = fetcher.resolve_latest_serie_historica(mock_client)
    assert url == RTN_FILE_BASE_URL
    assert mod_date == dt.datetime.strptime(now_str, HTTP_DATE_FORMAT)
    assert params == {"conteudo": "cdn"}


LM = "Thu, 29 Oct 2026 18:31:33 GMT"
CATALOG_URL = f"{RTN_THOT_ARQUIVOS_BASE_URL}/publicacao-anexo/29770"
XLSX_BYTES = b"PK\x03\x04 fake excel bytes"


def _entry(ano, mes, anexo_id, ext="xlsx"):
    nome = f"serie_historica_{mes}{str(ano)[2:]}.{ext}"
    return {
        "group": "rtn",
        "id": nome,
        "url": f"{RTN_THOT_ARQUIVOS_BASE_URL}/publicacao-anexo/{anexo_id}",
        "ano_publicacao": str(ano),
        "mes_publicacao": str(mes),
        "filename": nome,
        "ext": ext,
    }


@pytest.fixture
def catalog_lista(monkeypatch: pytest.MonkeyPatch):
    """Catálogo com várias edições fora de ordem; a mais nova é out/2026."""
    entradas = [
        _entry(2026, 9, 29566),
        _entry(2026, 10, 29770),
        _entry(2025, 12, 27000),
        _entry(2026, 2, 27964),
        _entry(2026, 11, 29999, ext="csv"),  # outro formato: ignorado
    ]
    monkeypatch.setattr(catalog, "list_datasets", lambda group=None: entradas)
    return entradas


def _client_com_link(link_falha, *, download_falha_no_link=False):
    """Cliente falso: o link curto reage como `link_falha`; o catálogo responde 200."""
    client = MagicMock()

    def head_or_get(url, *args, **kwargs):
        if url == RTN_FILE_BASE_URL:
            return link_falha()
        return DummyResponse(
            headers={"Last-Modified": LM, "Content-Type": "application/octet-stream"},
            url=url,
        )

    def download(url, dest, **kwargs):
        if url == RTN_FILE_BASE_URL and download_falha_no_link:
            raise InvalidPayloadSignatureError("HTML no lugar do xlsx")
        dest.write_bytes(XLSX_BYTES)
        return dest

    client.head_or_get.side_effect = head_or_get
    client.download_with_manifest.side_effect = download
    return client


def _http500():
    raise HttpStatusError(RTN_FILE_BASE_URL, 500)


def _timeout():
    raise TimeoutError("tempo esgotado")


def _html200():
    return DummyResponse(
        headers={"Last-Modified": LM, "Content-Type": "text/html; charset=utf-8"},
        url=RTN_FILE_BASE_URL,
    )


def test_download_link_ok_nao_consulta_catalogo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalog_lista
):
    """Link respondendo: usa o link, com assinatura xlsx exigida, sem catálogo."""
    client = _client_com_link(
        lambda: DummyResponse(
            headers={"Last-Modified": LM, "Content-Type": "application/vnd.ms-excel"},
            url=RTN_FILE_BASE_URL,
        )
    )
    monkeypatch.setattr(fetcher, "_get_client", lambda: client)
    consultas = []
    monkeypatch.setattr(catalog, "list_datasets", lambda g=None: consultas.append(g))

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == "rtn@20261029T183133.xlsx"
    args, kwargs = client.download_with_manifest.call_args
    assert args[0] == RTN_FILE_BASE_URL
    assert kwargs["params"] == {"conteudo": "cdn"}
    assert kwargs["expected_format"] == "xlsx"
    assert consultas == []


@pytest.mark.parametrize(
    "link_falha",
    [_http500, _timeout, _html200],
    ids=["http-500", "tempo-esgotado", "html-com-200"],
)
def test_download_link_falha_cai_no_catalogo(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    catalog_lista,
    link_falha,
):
    client = _client_com_link(link_falha)
    monkeypatch.setattr(fetcher, "_get_client", lambda: client)
    caplog.set_level("INFO", logger="rtn_fetcher.fetcher")

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.exists()
    assert dest.name == "rtn@20261029T183133.xlsx"
    args, kwargs = client.download_with_manifest.call_args
    assert args[0] == CATALOG_URL  # a edição mais nova do catálogo (out/2026)
    assert kwargs["params"] is None
    assert kwargs["expected_format"] == "xlsx"
    log = caplog.text
    assert "link curto da fonte" in log  # por que o link foi abandonado
    assert "pelo caminho 'catálogo'" in log  # qual caminho foi usado


def test_download_link_devolve_html_no_corpo_cai_no_catalogo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalog_lista
):
    """O cabeçalho parece bom mas o corpo não é xlsx: a validação do download barra."""
    client = _client_com_link(
        lambda: DummyResponse(headers={"Last-Modified": LM}, url=RTN_FILE_BASE_URL),
        download_falha_no_link=True,
    )
    monkeypatch.setattr(fetcher, "_get_client", lambda: client)

    dest = fetcher.download_latest_file(tmp_path)

    urls = [c.args[0] for c in client.download_with_manifest.call_args_list]
    assert urls == [RTN_FILE_BASE_URL, CATALOG_URL]
    assert dest.read_bytes() == XLSX_BYTES


def test_download_escolhe_o_mais_recente_do_catalogo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalog_lista
):
    client = _client_com_link(_http500)
    monkeypatch.setattr(fetcher, "_get_client", lambda: client)
    fetcher.download_latest_file(tmp_path)
    assert client.download_with_manifest.call_args.args[0] == CATALOG_URL
    assert catalog.latest_serie_historica_entry()["filename"] == (
        "serie_historica_10" + "26.xlsx"
    )


def test_download_todos_os_caminhos_falham_diz_as_causas(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    client = MagicMock()
    client.head_or_get.side_effect = HttpStatusError(RTN_FILE_BASE_URL, 500)
    client.get_json.side_effect = RuntimeError("CKAN fora do ar")
    monkeypatch.setattr(fetcher, "_get_client", lambda: client)

    def catalogo_fora(group=None):
        raise RuntimeError("catalogo sem lista")

    monkeypatch.setattr(catalog, "list_datasets", catalogo_fora)

    with pytest.raises(FetchError) as info:
        fetcher.download_latest_file(tmp_path)

    msg = str(info.value)
    assert "link curto da fonte" in msg and "HTTP 500" in msg
    assert "catálogo" in msg and "catalogo sem lista" in msg
    assert "CKAN" in msg and "CKAN fora do ar" in msg
    client.download_with_manifest.assert_not_called()


def test_resolve_latest_serie_historica_usa_catalogo_e_ckan(
    monkeypatch: pytest.MonkeyPatch, catalog_lista
):
    client = _client_com_link(_http500)
    url, mod_date, params = fetcher.resolve_latest_serie_historica(client)
    assert url == CATALOG_URL
    assert mod_date == dt.datetime(2026, 10, 29, 18, 31, 33)
    assert params is None

    # catálogo sem XLSX da série -> CKAN
    monkeypatch.setattr(catalog, "list_datasets", lambda group=None: [])
    ckan_url = "https://www.tesourotransparente.gov.br/ckan/resource/serie.xlsx"
    client.get_json.return_value = {
        "result": {
            "resources": [
                {
                    "name": "RTN - Série Histórica",
                    "format": "XLSX",
                    "url": ckan_url,
                    "last_modified": "2026-08-27T19:01:15.000000",
                }
            ]
        }
    }
    url, mod_date, params = fetcher.resolve_latest_serie_historica(client)
    assert url == ckan_url


def test_resolve_latest_serie_historica_all_failed(
    monkeypatch: pytest.MonkeyPatch,
):
    def catalogo_fora(group=None):
        raise RuntimeError("catalogo fora")

    monkeypatch.setattr(catalog, "list_datasets", catalogo_fora)
    mock_client = MagicMock()
    mock_client.head_or_get.side_effect = RuntimeError("All servers down")
    mock_client.get_json.side_effect = RuntimeError("CKAN down")
    with pytest.raises(FetchError, match="nenhum caminho"):
        fetcher.resolve_latest_serie_historica(mock_client)


def test_catalog_fallback_when_apex_fails(monkeypatch: pytest.MonkeyPatch):
    """Quando fetch_publications_metadata falha, catalog.list_datasets usa fallback."""
    catalog.clear_cache()

    def fake_failing_fetch():
        raise RuntimeError("HTTP 503 APEX down")

    monkeypatch.setattr(catalog, "fetch_publications_metadata", fake_failing_fetch)

    entries = catalog.list_datasets("rtn")
    assert len(entries) == len(KNOWN_SERIE_HISTORICA_ANEXOS)
    filenames = [e["filename"] for e in entries]
    assert "serie_historica_set26.xlsx" in filenames
    assert "serie_historica_ago26.xlsx" in filenames
    assert "serie_historica_jul26.xlsx" in filenames

    # URLs devem apontar para THOT-Arquivos
    for e in entries:
        assert RTN_THOT_ARQUIVOS_BASE_URL in e["url"]

    catalog.clear_cache()
