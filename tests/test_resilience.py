# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Testes de resiliência do rtn-fetcher contra quedas do sisweb e APEX."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from quantilica.core.exceptions import FetchError

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


def test_resolve_latest_serie_historica_fallback_thot_arquivos():
    """Quando o sisweb falha (503), o fallback para THOT-Arquivos / CDN é ativado."""
    mock_client = MagicMock()

    # Primeira chamada (sisweb) falha com erro 503
    def fake_head_or_get(url, *args, **kwargs):
        if "sisweb.tesouro.gov.br" in url:
            raise RuntimeError("503 Service Unavailable")
        if "thot-arquivos.tesouro.gov.br" in url:
            # Retorna 200 apontando para a CDN com Last-Modified
            return DummyResponse(
                status_code=200,
                headers={"Last-Modified": "Thu, 29 Oct 2026 18:31:33 GMT"},
                url="https://cdn.tesouro.gov.br/sistemas/serie_historica_set26.xlsx",
            )
        raise RuntimeError(f"Unexpected url {url}")

    mock_client.head_or_get.side_effect = fake_head_or_get

    url, mod_date, params = fetcher.resolve_latest_serie_historica(mock_client)
    assert "cdn.tesouro.gov.br" in url
    assert mod_date == dt.datetime(2026, 10, 29, 18, 31, 33)
    assert params is None


def test_resolve_latest_serie_historica_fallback_ckan():
    """Quando sisweb e THOT-Arquivos falham, o fallback para CKAN é ativado."""
    mock_client = MagicMock()

    def fake_head_or_get(url, *args, **kwargs):
        if "ckan" in url or "seriehistorica" in url:
            return DummyResponse(
                status_code=200,
                headers={"Last-Modified": "Thu, 27 Aug 2026 19:01:15 GMT"},
                url="https://www.tesourotransparente.gov.br/ckan/resource/download/seriehistoricajul26.xlsx",
            )
        raise RuntimeError("Service Unavailable")

    mock_client.head_or_get.side_effect = fake_head_or_get
    mock_client.get_json.return_value = {
        "result": {
            "resources": [
                {
                    "name": "Resultado do Tesouro Nacional - Série Histórica - Mensal",
                    "format": "XLSX",
                    "url": "https://www.tesourotransparente.gov.br/ckan/resource/download/seriehistoricajul26.xlsx",
                    "last_modified": "2026-08-27T19:01:15.000000",
                }
            ]
        }
    }

    url, mod_date, params = fetcher.resolve_latest_serie_historica(mock_client)
    assert "ckan" in url
    assert mod_date == dt.datetime(2026, 8, 27, 19, 1, 15)
    assert params is None


def test_resolve_latest_serie_historica_all_failed():
    """Quando todos os tiers falham, levanta FetchError acionável."""
    mock_client = MagicMock()
    mock_client.head_or_get.side_effect = RuntimeError("All servers down")
    mock_client.get_json.side_effect = RuntimeError("CKAN down")

    with pytest.raises(FetchError, match="todos os endpoints"):
        fetcher.resolve_latest_serie_historica(mock_client)


def test_download_latest_file_resilient(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """download_latest_file usa resolução resiliente e baixa o arquivo com manifesto."""
    mod_date = dt.datetime(2026, 10, 29, 18, 31, 33)
    fake_url = "https://cdn.tesouro.gov.br/serie_historica_set26.xlsx"

    mock_client = MagicMock()

    def fake_resolve(client):
        return fake_url, mod_date, None

    def fake_download(url, dest, **kwargs):
        dest.write_bytes(b"PK fake excel bytes")
        return dest

    monkeypatch.setattr(fetcher, "resolve_latest_serie_historica", fake_resolve)
    monkeypatch.setattr(fetcher, "_get_client", lambda: mock_client)
    mock_client.download_with_manifest.side_effect = fake_download

    dest = fetcher.download_latest_file(tmp_path)
    assert dest.exists()
    assert dest.name == "rtn@20261029T183133.xlsx"
    mock_client.download_with_manifest.assert_called_once()


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
