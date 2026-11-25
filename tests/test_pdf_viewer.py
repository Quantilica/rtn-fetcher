# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Anexos PDF do Tesouro: a página visualizadora vira o PDF real (sem rede)."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import httpx2
import pytest
from quantilica.core.exceptions import FetchError, InvalidPayloadSignatureError
from quantilica.core.http import HttpClient

from rtn_fetcher import fetcher
from rtn_fetcher.catalog import GROUP_ALIASES, GROUPS, list_datasets
from rtn_fetcher.plugin import RtnFetcherApp, path_builder

VIEWER_URL = "https://thot-arquivos.tesouro.gov.br/publicacao/55921"
CDN_URL = (
    "https://cdn.tesouro.gov.br/sistemas-internos/apex/producao/sistemas/thot/"
    "arquivos/publicacoes/55921_1803160/boletim_ago26.pdf"
)
PDF_BODY = b"%PDF-1.7\n" + b"x" * 2048 + b"\n%%EOF\n"


def _viewer(src: str) -> str:
    return (
        "\n    <html>\n    <head>\n        <title>Visualização de PDF</title>\n"
        "    </head>\n    <body>\n"
        f"        <iframe src='{src}'></iframe>\n    </body>\n    </html>\n    "
    )


def _html(body: str) -> httpx2.Response:
    return httpx2.Response(
        200, content=body.encode(), headers={"Content-Type": "text/html; charset=utf-8"}
    )


def _make_handler(routes: dict[str, httpx2.Response], calls: list[str]):
    def handler(request: httpx2.Request) -> httpx2.Response:
        url = str(request.url)
        calls.append(f"{request.method} {url}")
        if request.method == "HEAD" and url.startswith("https://thot-arquivos"):
            return httpx2.Response(405)
        if url in routes:
            return routes[url]
        return httpx2.Response(404)

    return handler


def _app(handler) -> RtnFetcherApp:
    client = HttpClient(attempts=1, transport=httpx2.MockTransport(handler))
    return RtnFetcherApp(
        "rtn-fetcher",
        groups_dict=GROUPS,
        aliases_dict=GROUP_ALIASES,
        list_datasets=list_datasets,
        path_builder=path_builder,
        source_id="rtn",
        client=client,
        build_default_commands=False,
    )


def _entry(url: str = VIEWER_URL, filename: str = "boletim_ago26.pdf") -> dict:
    return {
        "group": "rtn-publicacoes",
        "id": filename,
        "url": url,
        "ano_publicacao": "2026",
        "mes_publicacao": "8",
        "filename": filename,
        "ext": filename.rsplit(".", 1)[-1],
    }


def _cdn_pdf(body: bytes = PDF_BODY) -> httpx2.Response:
    return httpx2.Response(
        200,
        content=body,
        headers={
            "Content-Type": "application/pdf",
            "Last-Modified": "Tue, 29 Sep 2026 13:15:10 GMT",
        },
    )


def test_viewer_resolves_to_real_pdf(tmp_path: Path):
    calls: list[str] = []
    app = _app(
        _make_handler({VIEWER_URL: _html(_viewer(CDN_URL)), CDN_URL: _cdn_pdf()}, calls)
    )
    out = app.download_entry(_entry(), tmp_path)

    assert out.read_bytes() == PDF_BODY
    assert out.name.startswith("boletim_ago26") and out.suffix == ".pdf"
    assert "20260929" in out.name  # carimbo = Last-Modified do PDF real
    assert any(c.endswith(CDN_URL) and c.startswith("GET") for c in calls)


def test_direct_pdf_is_downloaded(tmp_path: Path):
    calls: list[str] = []
    app = _app(_make_handler({VIEWER_URL: _cdn_pdf()}, calls))
    out = app.download_entry(_entry(), tmp_path)
    assert out.read_bytes() == PDF_BODY


def test_html_without_iframe_is_refused(tmp_path: Path):
    app = _app(_make_handler({VIEWER_URL: _html("<html><body>erro</body></html>")}, []))
    with pytest.raises(FetchError, match="iframe"):
        app.download_entry(_entry(), tmp_path)
    assert not list(tmp_path.rglob("*.pdf"))


def test_iframe_to_foreign_host_is_refused(tmp_path: Path):
    evil = "https://evil.example.com/tesouro.gov.br/boletim.pdf"
    calls: list[str] = []
    app = _app(_make_handler({VIEWER_URL: _html(_viewer(evil))}, calls))
    with pytest.raises(FetchError, match="fora do domínio"):
        app.download_entry(_entry(), tmp_path)
    assert not any("evil.example.com" in c for c in calls)
    assert not list(tmp_path.rglob("*.pdf"))


@pytest.mark.parametrize(
    "src",
    [
        "http://cdn.tesouro.gov.br/x.pdf",
        "https://cdn.tesouro.gov.br.evil.com/x.pdf",
        "https://nottesouro.gov.br/x.pdf",
        "https://user:pw@cdn.tesouro.gov.br/x.pdf",
        "https://cdn.tesouro.gov.br:8443/x.pdf",
        "/publicacao/1.pdf",
    ],
)
def test_validate_pdf_url_rejects(src: str):
    with pytest.raises(FetchError):
        fetcher.validate_pdf_url(src)


def test_validate_pdf_url_accepts_tesouro_hosts():
    assert fetcher.validate_pdf_url(CDN_URL) == CDN_URL
    assert fetcher.validate_pdf_url("https://tesouro.gov.br/a.PDF")


def test_non_pdf_body_never_replaces_existing_file(tmp_path: Path):
    """O iframe aponta para o host certo, mas o corpo não é PDF: recusa e preserva."""
    calls: list[str] = []
    app = _app(
        _make_handler(
            {
                VIEWER_URL: _html(_viewer(CDN_URL)),
                CDN_URL: httpx2.Response(
                    200,
                    content=b"<html><body>manutencao</body></html>",
                    headers={
                        "Content-Type": "text/html",
                        "Last-Modified": "Tue, 29 Sep 2026 13:15:10 GMT",
                    },
                ),
            },
            calls,
        )
    )
    dest = app.path_builder(tmp_path, _entry(), dt.date(2026, 9, 29))
    dest.parent.mkdir(parents=True)
    dest.write_bytes(PDF_BODY)
    with pytest.raises(InvalidPayloadSignatureError):
        app.download_entry(_entry(), tmp_path, force=True)
    assert dest.read_bytes() == PDF_BODY


def test_non_pdf_entries_are_not_touched(tmp_path: Path):
    app = _app(_make_handler({}, []))
    entry = _entry(filename="serie_historica_ago26.xlsx")
    assert app._resolve_pdf_entry(entry) is entry


def test_check_entry_uses_real_pdf(tmp_path: Path):
    calls: list[str] = []
    app = _app(
        _make_handler({VIEWER_URL: _html(_viewer(CDN_URL)), CDN_URL: _cdn_pdf()}, calls)
    )
    item = app.check_entry(_entry(), tmp_path)
    assert item.url == CDN_URL
    assert item.action == "download"
    assert item.entry["expected_format"] == "pdf"


def test_entry_already_pointing_to_cdn_is_not_resolved_again():
    calls: list[str] = []
    app = _app(_make_handler({}, calls))
    entry = _entry(url=CDN_URL)
    assert app._resolve_pdf_entry(entry) is entry
    assert calls == []
