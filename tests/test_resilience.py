# Copyright (c) 2026 Komesu, D.K.
# Licensed under the MIT License.

"""Testes de resiliência do rtn-fetcher contra quedas do sisweb e APEX."""

from __future__ import annotations

import datetime as dt
import io
import zipfile

import httpx2
import pytest
from quantilica.core.exceptions import FetchError
from quantilica.core.http import HttpClient, HttpStatusError

from rtn_fetcher import catalog, fetcher
from rtn_fetcher.constants import (
    KNOWN_SERIE_HISTORICA_ANEXOS,
    RTN_CKAN_PACKAGE_URL,
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


LM_OLD = "Thu, 29 Oct 2026 18:31:33 GMT"  # setembro (a edição antiga)
LM_NEW = "Fri, 27 Nov 2026 13:39:14 GMT"  # outubro (a mais nova)
STAMP_OLD = "rtn@20261029T183133.xlsx"
STAMP_NEW = "rtn@20261127T133914.xlsx"
SEP_URL = f"{RTN_THOT_ARQUIVOS_BASE_URL}/publicacao-anexo/29566"
OUT_URL = f"{RTN_THOT_ARQUIVOS_BASE_URL}/publicacao-anexo/29770"
CKAN_RES = "https://www.tesourotransparente.gov.br/ckan/resource/serie.xlsx"
XLSX_BYTES = b"PK\x03\x04 conteudo de teste"


def _ok(lm: str, url: str = "https://cdn.tesouro.gov.br/x.xlsx") -> DummyResponse:
    return DummyResponse(
        headers={"Last-Modified": lm, "Content-Type": "application/octet-stream"},
        url=url,
    )


def _http500(*_a, **_k):
    raise HttpStatusError(RTN_FILE_BASE_URL, 500)


def _timeout(*_a, **_k):
    raise TimeoutError("tempo esgotado")


def _html200():
    return DummyResponse(
        headers={"Last-Modified": LM_NEW, "Content-Type": "text/html; charset=utf-8"},
        url=RTN_FILE_BASE_URL,
    )


def _entry(ano, mes, anexo_id, ext="xlsx", synthetic=False, nome=None):
    nome = nome or f"serie_historica_{mes}{str(ano)[2:]}.{ext}"
    entry = {
        "group": "rtn",
        "id": nome,
        "url": f"{RTN_THOT_ARQUIVOS_BASE_URL}/publicacao-anexo/{anexo_id}",
        "ano_publicacao": str(ano),
        "mes_publicacao": str(mes),
        "filename": nome,
        "ext": ext,
    }
    if synthetic:
        entry["synthetic"] = True
    return entry


class FakeClient:
    """Cliente falso: `head` mapeia URL -> resposta (ou função que levanta)."""

    def __init__(self, head, *, ckan=None, fail_downloads=()):
        self.head = head
        self.ckan = ckan
        self.fail_downloads = set(fail_downloads)
        self.head_urls: list[str] = []
        self.downloads: list[tuple[str, dict]] = []

    def head_or_get(self, url, *args, **kwargs):
        self.head_urls.append(url)
        if url not in self.head:
            raise HttpStatusError(url, 404)
        value = self.head[url]
        if callable(value):
            value = value()
        return value

    def get_json(self, url, *args, **kwargs):
        if self.ckan is None:
            raise RuntimeError("CKAN fora do ar")
        return self.ckan

    def download_with_manifest(self, url, dest, **kwargs):
        self.downloads.append((url, kwargs))
        if url in self.fail_downloads:
            raise FetchError(f"download de {url} falhou")
        dest.write_bytes(XLSX_BYTES)
        return dest


@pytest.fixture
def catalogo(monkeypatch: pytest.MonkeyPatch):
    """Catálogo real (fora de ordem): a edição mais nova é out/2026."""
    entradas = [
        _entry(2026, 9, 29566),
        _entry(2026, 10, 29770),
        _entry(2025, 12, 27000),
        _entry(2026, 2, 27964),
        _entry(2026, 11, 29999, ext="csv"),  # outro formato: ignorado
    ]
    monkeypatch.setattr(catalog, "list_datasets", lambda group=None: entradas)
    return entradas


def _usa(monkeypatch, client):
    monkeypatch.setattr(fetcher, "_get_client", lambda: client)


def _link_e_catalogo(link):
    return {RTN_FILE_BASE_URL: link, OUT_URL: _ok(LM_NEW, OUT_URL)}


# --- link curto x catálogo -------------------------------------------------


def test_link_igual_ao_catalogo_vence_o_empate(tmp_path, monkeypatch, catalogo):
    client = FakeClient(
        {RTN_FILE_BASE_URL: _ok(LM_NEW, RTN_FILE_BASE_URL), OUT_URL: _ok(LM_NEW)}
    )
    _usa(monkeypatch, client)

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == STAMP_NEW
    url, kwargs = client.downloads[0]
    assert url == RTN_FILE_BASE_URL
    assert kwargs["params"] == {"conteudo": "cdn"}
    assert kwargs["expected_format"] == "xlsx"
    assert len(client.downloads) == 1


def test_link_ok_mas_mais_antigo_que_o_catalogo_usa_o_catalogo(
    tmp_path, monkeypatch, catalogo, caplog
):
    client = FakeClient(_link_e_catalogo(_ok(LM_OLD, RTN_FILE_BASE_URL)))
    _usa(monkeypatch, client)

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == STAMP_NEW
    assert [u for u, _ in client.downloads] == [OUT_URL]
    assert "Link curto abandonado" in caplog.text


def test_link_mais_novo_que_o_catalogo_usa_o_link(tmp_path, monkeypatch, catalogo):
    client = FakeClient(
        {RTN_FILE_BASE_URL: _ok(LM_NEW, RTN_FILE_BASE_URL), OUT_URL: _ok(LM_OLD)}
    )
    _usa(monkeypatch, client)
    fetcher.download_latest_file(tmp_path)
    assert client.downloads[0][0] == RTN_FILE_BASE_URL


def test_link_ok_e_catalogo_fora_vale_o_link(tmp_path, monkeypatch):
    def catalogo_fora(group=None):
        raise RuntimeError("API de metadados fora")

    monkeypatch.setattr(catalog, "list_datasets", catalogo_fora)
    client = FakeClient({RTN_FILE_BASE_URL: _ok(LM_OLD, RTN_FILE_BASE_URL)})
    _usa(monkeypatch, client)

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == STAMP_OLD
    assert [u for u, _ in client.downloads] == [RTN_FILE_BASE_URL]


@pytest.mark.parametrize(
    "link_falha",
    [_http500, _timeout, _html200],
    ids=["http-500", "tempo-esgotado", "html-com-200"],
)
def test_link_falha_cai_no_catalogo(
    tmp_path, monkeypatch, caplog, catalogo, link_falha
):
    client = FakeClient(_link_e_catalogo(link_falha))
    _usa(monkeypatch, client)
    caplog.set_level("INFO", logger="rtn_fetcher.fetcher")

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == STAMP_NEW
    url, kwargs = client.downloads[0]
    assert url == OUT_URL  # a edição mais nova do catálogo (out/2026)
    assert kwargs["params"] is None
    assert kwargs["expected_format"] == "xlsx"
    assert "link curto da fonte" in caplog.text  # por que o link foi abandonado
    assert "pelo caminho 'catálogo'" in caplog.text  # qual caminho foi usado


def test_download_do_escolhido_falha_tenta_o_outro(tmp_path, monkeypatch, catalogo):
    client = FakeClient(
        {RTN_FILE_BASE_URL: _ok(LM_OLD, RTN_FILE_BASE_URL), OUT_URL: _ok(LM_NEW)},
        fail_downloads={OUT_URL},
    )
    _usa(monkeypatch, client)

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == STAMP_OLD
    assert [u for u, _ in client.downloads] == [OUT_URL, RTN_FILE_BASE_URL]


def test_arquivo_ja_existente_nao_baixa_de_novo(tmp_path, monkeypatch, catalogo):
    existente = tmp_path / STAMP_NEW
    existente.write_bytes(XLSX_BYTES)
    client = FakeClient(_link_e_catalogo(_http500))
    _usa(monkeypatch, client)

    dest = fetcher.download_latest_file(tmp_path)

    assert dest == existente
    assert client.downloads == []


# --- catálogo: sintético, período, empate ----------------------------------


def test_fallback_do_catalogo_marca_entradas_sinteticas(monkeypatch):
    catalog.clear_cache()

    def api_fora():
        raise RuntimeError("HTTP 503 APEX down")

    monkeypatch.setattr(catalog, "fetch_publications_metadata", api_fora)
    entradas = catalog.list_datasets("rtn")
    assert entradas and all(e["synthetic"] is True for e in entradas)
    with pytest.raises(FetchError, match="catálogo real está indisponível"):
        catalog.latest_serie_historica_entries()
    catalog.clear_cache()


def test_catalogo_sintetico_e_recusado_no_download(tmp_path, monkeypatch):
    """API fora: a lista fixa (set/2026) não vira 'a mais recente'."""
    entradas = [_entry(2026, 9, 29566, synthetic=True)]
    monkeypatch.setattr(catalog, "list_datasets", lambda group=None: entradas)
    client = FakeClient({RTN_FILE_BASE_URL: _http500, SEP_URL: _ok(LM_OLD)})
    _usa(monkeypatch, client)

    with pytest.raises(FetchError) as info:
        fetcher.download_latest_file(tmp_path)

    msg = str(info.value)
    assert "catálogo real está indisponível" in msg
    assert "link curto da fonte" in msg
    assert client.downloads == []
    assert SEP_URL not in client.head_urls


def test_catalogo_sintetico_com_ckan_segue_para_o_ckan(tmp_path, monkeypatch):
    entradas = [_entry(2026, 9, 29566, synthetic=True)]
    monkeypatch.setattr(catalog, "list_datasets", lambda group=None: entradas)
    ckan = {
        "result": {
            "resources": [
                {
                    "name": "RTN - Série Histórica",
                    "format": "XLSX",
                    "url": CKAN_RES,
                    "last_modified": "2026-11-27T13:39:14",
                }
            ]
        }
    }
    client = FakeClient({RTN_FILE_BASE_URL: _http500, CKAN_RES: _ok(LM_NEW)}, ckan=ckan)
    _usa(monkeypatch, client)

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == STAMP_NEW
    assert [u for u, _ in client.downloads] == [CKAN_RES]


def test_escolhe_o_maior_ano_mes_e_ignora_mes_invalido(monkeypatch):
    entradas = [
        _entry(2025, 12, 1),
        _entry(2026, 10, 2),
        _entry(2026, 9, 3),
        _entry(2027, 13, 4, nome="serie_historica_x.xlsx"),  # mês fora de 1..12
        _entry(2027, 1, 5, ext="xls"),  # não é XLSX
    ]
    monkeypatch.setattr(catalog, "list_datasets", lambda group=None: entradas)
    escolhidas = catalog.latest_serie_historica_entries()
    assert [e["id"] for e in escolhidas] == ["serie_historica_1026.xlsx"]


def test_empate_de_periodo_vence_a_modificada_mais_recente(
    tmp_path, monkeypatch, caplog
):
    original = _entry(2026, 10, 100, nome="serie_historica_out26.xlsx")
    revisada = _entry(2026, 10, 101, nome="serie_historica_out26_revisada.xlsx")
    monkeypatch.setattr(
        catalog,
        "list_datasets",
        lambda group=None: [original, _entry(2026, 9, 99), revisada],
    )
    url_o, url_r = original["url"], revisada["url"]
    client = FakeClient(
        {RTN_FILE_BASE_URL: _http500, url_o: _ok(LM_OLD), url_r: _ok(LM_NEW)}
    )
    _usa(monkeypatch, client)

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == STAMP_NEW
    assert [u for u, _ in client.downloads] == [url_r]
    assert SEP_URL not in client.head_urls  # set/2026 nem foi consultado


# --- CKAN -----------------------------------------------------------------


def _ckan(*recursos):
    return {"result": {"resources": list(recursos)}}


def _res(url, data=None, nome="RTN - Série Histórica"):
    r = {"name": nome, "format": "XLSX", "url": url}
    if data:
        r["last_modified"] = data
    return r


def test_ckan_tenta_o_proximo_recurso_quando_o_primeiro_falha(monkeypatch):
    a, b = "https://x.gov.br/a.xlsx", "https://x.gov.br/b.xlsx"
    client = FakeClient(
        {a: _http500, b: _ok(LM_NEW)},
        ckan=_ckan(_res(a, "2026-11-27T00:00:00"), _res(b, "2026-10-01T00:00:00")),
    )
    url, mod, _ = fetcher._resolve_via_ckan(client)
    assert url == b and client.head_urls == [a, b]


def test_ckan_escolhe_o_mais_recente_pela_data_do_recurso():
    velho, novo = "https://x.gov.br/velho.xlsx", "https://x.gov.br/novo.xlsx"
    client = FakeClient(
        {velho: _ok(LM_OLD), novo: _ok(LM_NEW)},
        ckan=_ckan(
            _res(velho, "2026-09-01T00:00:00"), _res(novo, "2026-11-01T00:00:00")
        ),
    )
    url, _, _ = fetcher._resolve_via_ckan(client)
    assert url == novo and client.head_urls == [novo]


def test_ckan_sem_datas_segue_a_ordem_da_fonte_e_registra(caplog):
    a, b = "https://x.gov.br/a.xlsx", "https://x.gov.br/b.xlsx"
    client = FakeClient({a: _ok(LM_OLD), b: _ok(LM_NEW)}, ckan=_ckan(_res(a), _res(b)))
    caplog.set_level("INFO", logger="rtn_fetcher.fetcher")
    url, _, _ = fetcher._resolve_via_ckan(client)
    assert url == a
    assert "ordem da fonte" in caplog.text


# --- falhas gerais ----------------------------------------------------------


def test_todos_os_caminhos_falham_diz_as_causas(tmp_path, monkeypatch):
    def catalogo_fora(group=None):
        raise RuntimeError("catalogo sem lista")

    monkeypatch.setattr(catalog, "list_datasets", catalogo_fora)
    client = FakeClient({RTN_FILE_BASE_URL: _http500}, ckan=None)
    _usa(monkeypatch, client)

    with pytest.raises(FetchError) as info:
        fetcher.download_latest_file(tmp_path)

    msg = str(info.value)
    assert "link curto da fonte" in msg and "HTTP 500" in msg
    assert "catálogo" in msg and "catalogo sem lista" in msg
    assert "CKAN" in msg and "CKAN fora do ar" in msg
    assert client.downloads == []


def test_resolve_latest_serie_historica_escolhe_a_mais_nova(monkeypatch, catalogo):
    client = FakeClient(_link_e_catalogo(_ok(LM_OLD, RTN_FILE_BASE_URL)))
    url, mod_date, params = fetcher.resolve_latest_serie_historica(client)
    assert url == OUT_URL
    assert mod_date == dt.datetime(2026, 11, 27, 13, 39, 14)
    assert params is None


def test_resolve_latest_serie_historica_all_failed(monkeypatch):
    def catalogo_fora(group=None):
        raise RuntimeError("catalogo fora")

    monkeypatch.setattr(catalog, "list_datasets", catalogo_fora)
    client = FakeClient({RTN_FILE_BASE_URL: _http500})
    with pytest.raises(FetchError, match="nenhum caminho"):
        fetcher.resolve_latest_serie_historica(client)


# --- validação real da assinatura (HttpClient com transporte simulado) -----


def _xlsx_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
    return buf.getvalue()


def _http_client(handler) -> HttpClient:
    return HttpClient(
        attempts=1,
        retry_base_delay=0.0,
        transport=httpx2.MockTransport(handler),
    )


def test_cabecalho_bom_corpo_html_cai_no_catalogo_pela_validacao_real(
    tmp_path, monkeypatch, catalogo
):
    """O link responde 200 e Last-Modified bons, mas o corpo é HTML."""
    planilha = _xlsx_zip()

    def handler(request: httpx2.Request) -> httpx2.Response:
        url = str(request.url)
        if url.startswith(RTN_FILE_BASE_URL):
            headers = {
                "Last-Modified": LM_NEW,
                "Content-Type": "application/octet-stream",
            }
            body = b"<!DOCTYPE html><html><body>Erro</body></html>"
        elif url == OUT_URL:
            headers = {
                "Last-Modified": LM_NEW,
                "Content-Type": "application/octet-stream",
            }
            body = planilha
        else:
            return httpx2.Response(404)
        content = b"" if request.method == "HEAD" else body
        return httpx2.Response(200, headers=headers, content=content)

    _usa(monkeypatch, _http_client(handler))

    dest = fetcher.download_latest_file(tmp_path)

    assert dest.name == STAMP_NEW
    assert dest.read_bytes() == planilha
    # nada do HTML ficou gravado em lugar nenhum
    assert sorted(p.name for p in tmp_path.iterdir() if p.suffix == ".xlsx") == [
        STAMP_NEW
    ]


def test_corpo_que_nao_e_zip_nao_vira_arquivo(tmp_path, monkeypatch, catalogo):
    """Nenhum caminho entrega um ZIP válido: erro, sem arquivo no destino."""

    def handler(request: httpx2.Request) -> httpx2.Response:
        headers = {"Last-Modified": LM_NEW, "Content-Type": "application/octet-stream"}
        content = b"" if request.method == "HEAD" else b"PK\x03\x04 truncado"
        if str(request.url).startswith(RTN_CKAN_PACKAGE_URL):
            return httpx2.Response(404)
        return httpx2.Response(200, headers=headers, content=content)

    _usa(monkeypatch, _http_client(handler))

    with pytest.raises(FetchError):
        fetcher.download_latest_file(tmp_path)

    assert not [p for p in tmp_path.iterdir() if p.suffix == ".xlsx"]


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
