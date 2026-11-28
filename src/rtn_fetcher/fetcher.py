"""HTTP fetching utilities for RTN data.

This module handles downloading RTN publications and metadata from the
Tesouro Nacional API.
"""

import datetime as dt
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from quantilica.core.exceptions import FetchError
from quantilica.core.files import (
    is_complete_file,
    write_bytes_atomic,
    write_text_atomic,
)
from quantilica.core.http import AsyncHttpClient, HttpClient
from quantilica.core.logging import get_logger, log_step
from quantilica.core.storage import stamp_filename

from .constants import (
    HTTP_DATE_FORMAT,
    RTN_API_BASE_URL,
    RTN_CKAN_PACKAGE_URL,
    RTN_FILE_BASE_URL,
)

_Resolution = tuple[str, dt.datetime, dict[str, str] | None]

logger = get_logger(__name__)
_client: HttpClient | None = None


def _get_client() -> HttpClient:
    """Return the shared HTTP client, creating it lazily on first use.

    Avoids instantiating the client (and its connection pool) at module
    import time; the instance is reused across calls for keep-alive.

    Returns:
        HttpClient: The shared client instance.
    """
    global _client
    if _client is None:
        _client = HttpClient(timeout=60.0)
    return _client


# Domínio (e subdomínios) de onde o visualizador de PDF pode apontar o arquivo.
PDF_HOST_DOMAIN = "tesouro.gov.br"
PDF_SIGNATURE = b"%PDF"
# Teto para a página visualizadora (a real tem ~400 bytes).
MAX_VIEWER_BYTES = 1_000_000
VIEWER_HOST = "thot-arquivos.tesouro.gov.br"

SOURCE_ID = "tesouro-nacional"
DATASET_ID = "rtn"


def fetch_publications_metadata() -> str:
    """Fetch RTN publications metadata from API.

    Returns:
        HTML string containing the publications metadata.
    """
    params = {"pageSize": "9999999"}
    client = _get_client()
    with log_step(logger, "fetch-rtn-metadata"):
        return client.get_text(RTN_API_BASE_URL, params=params)


def generate_filename(modified_date: dt.datetime) -> str:
    """Generate a stamped filename for the RTN file.

    Returns ``rtn@YYYYMMDDTHHMMSS.xlsx`` using the upstream Last-Modified
    timestamp so each new version produces a distinct local file.

    Args:
        modified_date: The last modified datetime from the upstream server.

    Returns:
        Generated filename string.
    """
    return stamp_filename("rtn", "xlsx", modified_date, precision="datetime")


_XLSX_FORMAT = "xlsx"


def _last_modified_of(head: Any, url: str) -> dt.datetime:
    """Lê o ``Last-Modified`` de uma resposta de cabeçalho.

    Raises:
        FetchError: Se a resposta não trouxer o cabeçalho.
    """
    header = head.headers.get("Last-Modified")
    if not header:
        raise FetchError(f"Resposta de {url} sem Last-Modified")
    return dt.datetime.strptime(header, HTTP_DATE_FORMAT)


def _check_not_html(head: Any, url: str) -> None:
    """Recusa resposta que se anuncia como página HTML (soft-200 da fonte).

    Raises:
        FetchError: Se o ``Content-Type`` for HTML ou o status for de erro.
    """
    if head.status_code >= 400:
        raise FetchError(f"{url} respondeu HTTP {head.status_code}")
    content_type = head.headers.get("Content-Type", "")
    if "html" in content_type.lower():
        raise FetchError(
            f"{url} devolveu uma página HTML (Content-Type {content_type!r}) "
            "no lugar da planilha"
        )


def _resolve_via_link(client: HttpClient) -> _Resolution:
    """Resolve pelo link curto da fonte (``RTN_FILE_BASE_URL``)."""
    head = client.head_or_get(RTN_FILE_BASE_URL, params={"conteudo": "cdn"})
    _check_not_html(head, RTN_FILE_BASE_URL)
    return (
        RTN_FILE_BASE_URL,
        _last_modified_of(head, RTN_FILE_BASE_URL),
        {"conteudo": "cdn"},
    )


def _resolve_via_catalog(client: HttpClient) -> _Resolution:
    """Resolve pelo catálogo, o mesmo que o ``sync`` usa para o grupo ``rtn``.

    Escolhe a planilha mais recente da série histórica listada pelo catálogo
    real. A lista fixa de anexos (usada quando a API de metadados está fora do
    ar) é recusada: pode estar atrasada. Se o mesmo (ano, mês) tiver mais de uma
    planilha, vence a de ``Last-Modified`` mais recente.
    """
    from .catalog import latest_serie_historica_entries

    best: tuple[_Resolution, dict[str, Any]] | None = None
    errors: list[str] = []
    for entry in latest_serie_historica_entries():
        url = str(entry["url"])
        try:
            head = client.head_or_get(url)
            _check_not_html(head, url)
            resolution: _Resolution = (url, _last_modified_of(head, url), None)
        except Exception as exc:  # noqa: BLE001 - pula só esta planilha
            logger.warning(
                "Catálogo: planilha %s ignorada: %s", entry["filename"], _describe(exc)
            )
            errors.append(f"{entry['filename']}: {_describe(exc)}")
            continue
        if best is None or resolution[1] > best[0][1]:
            best = (resolution, entry)
    if best is None:
        raise FetchError(
            "nenhuma planilha da edição mais recente do catálogo respondeu ("
            + "; ".join(errors)
            + ")"
        )
    resolution, entry = best
    logger.info(
        "Série histórica do RTN escolhida pelo catálogo: %s (%02d/%d)",
        entry["filename"],
        int(entry["mes_publicacao"]),
        int(entry["ano_publicacao"]),
    )
    return resolution


def _to_utc_naive(value: dt.datetime) -> dt.datetime:
    """UTC sem fuso: data com offset é convertida, data sem fuso vale como UTC."""
    if value.tzinfo is not None:
        value = value.astimezone(dt.UTC).replace(tzinfo=None)
    return value


def _parse_ckan_date(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        return _to_utc_naive(dt.datetime.fromisoformat(str(value)))
    except ValueError:
        return None


def _ckan_resource_date(resource: dict[str, Any]) -> dt.datetime | None:
    """Data para ORDENAR os recursos do CKAN (UTC sem fuso), quando informada.

    Serve só para ordenar: ``metadata_modified`` e ``created`` não são a data do
    arquivo e nunca viram o carimbo dele.
    """
    for key in ("last_modified", "metadata_modified", "created"):
        parsed = _parse_ckan_date(resource.get(key))
        if parsed is not None:
            return parsed
    return None


def _resolve_via_ckan(client: HttpClient) -> _Resolution:
    """Resolve pelos recursos da série histórica no CKAN (último recurso).

    Considera todos os recursos XLSX da série, do mais recente (data de
    modificação do recurso, normalizada para UTC) ao mais antigo, e fica com o
    primeiro que responder. Sem data nos recursos, a escolha segue a ordem da
    fonte (registrado no log). O carimbo do arquivo é o ``Last-Modified`` HTTP do
    recurso ou, sem ele, o ``last_modified`` do recurso; sem nenhum dos dois o
    recurso não serve.
    """
    data = client.get_json(RTN_CKAN_PACKAGE_URL)
    resources = data.get("result", {}).get("resources", [])
    matching: list[dict[str, Any]] = []
    for r in resources:
        r_name = r.get("name", "").lower()
        r_url = r.get("url", "").lower()
        is_xlsx = r.get("format", "").upper() == "XLSX"
        is_serie = any(
            k in r_name or k in r_url
            for k in ["serie", "série", "historica", "histórica"]
        )
        if is_xlsx and is_serie and r.get("url"):
            matching.append(r)
    if not matching:
        raise FetchError("o pacote do CKAN não lista a série histórica em XLSX")

    dated = [r for r in matching if _ckan_resource_date(r) is not None]
    if dated:
        dated.sort(
            key=lambda r: _ckan_resource_date(r) or dt.datetime.min, reverse=True
        )
        undated = [r for r in matching if _ckan_resource_date(r) is None]
        ordered = dated + undated
    else:
        logger.info(
            "CKAN: recursos sem data de modificação; escolha pela ordem da fonte"
        )
        ordered = matching

    errors: list[str] = []
    for r in ordered:
        ckan_url = str(r["url"])
        try:
            head = client.head_or_get(ckan_url)
            _check_not_html(head, ckan_url)
            # carimbo do arquivo: o Last-Modified HTTP do próprio recurso; sem
            # ele, o last_modified do recurso. metadata_modified/created não
            # servem (podem ser posteriores ao arquivo).
            if head.headers.get("Last-Modified"):
                return ckan_url, _last_modified_of(head, ckan_url), None
            ckan_date = _parse_ckan_date(r.get("last_modified"))
            if ckan_date is not None:
                return ckan_url, ckan_date, None
            raise FetchError(
                f"{ckan_url} sem Last-Modified nem last_modified no CKAN "
                "(sem data confiável do arquivo)"
            )
        except Exception as exc:  # noqa: BLE001 - tenta o próximo recurso
            logger.warning("CKAN: recurso %s falhou: %s", ckan_url, _describe(exc))
            errors.append(f"{ckan_url}: {_describe(exc)}")
    raise FetchError("nenhum recurso do CKAN respondeu (" + "; ".join(errors) + ")")


# Caminhos para achar a planilha: link curto e catálogo são comparados; o CKAN
# é o último recurso.
_PATHS: tuple[tuple[str, Callable[[HttpClient], _Resolution]], ...] = (
    ("link curto da fonte", _resolve_via_link),
    ("catálogo", _resolve_via_catalog),
    ("CKAN", _resolve_via_ckan),
)


def _describe(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {exc}"


def _fail_all(causes: list[tuple[str, BaseException]]) -> FetchError:
    detail = "; ".join(f"{label}: {_describe(exc)}" for label, exc in causes)
    return FetchError(
        f"Não foi possível obter a Série Histórica do RTN por nenhum caminho "
        f"({detail})."
    )


def _candidates(
    client: HttpClient, causes: list[tuple[str, BaseException]]
) -> Iterator[tuple[str, _Resolution]]:
    """Gera, do melhor ao pior, os caminhos que resolveram (lazy no CKAN).

    O link curto e o catálogo são resolvidos antes de qualquer download para que
    o link, mesmo funcionando, não vença uma edição mais nova do catálogo: vence
    o de ``Last-Modified`` mais recente (empate: o link). Se um deles falha, o
    outro vale. O CKAN só é consultado se os dois não bastarem. Causas de falha
    de resolução vão para ``causes``.
    """
    resolved: list[tuple[str, _Resolution]] = []
    for label, resolve in _PATHS[:2]:
        try:
            resolved.append((label, resolve(client)))
        except Exception as exc:  # noqa: BLE001 - cai para o próximo caminho
            logger.warning("Caminho '%s' indisponível: %s", label, _describe(exc))
            causes.append((label, exc))
    # ordenação estável: em empate, fica o link (primeiro da lista)
    resolved.sort(key=lambda item: item[1][1], reverse=True)
    if len(resolved) == 2 and resolved[0][0] != _PATHS[0][0]:
        logger.warning(
            "Link curto abandonado: o catálogo tem edição mais nova "
            "(Last-Modified %s contra %s do link)",
            resolved[0][1][1],
            resolved[1][1][1],
        )
    yield from resolved
    label, resolve = _PATHS[2]
    try:
        resolution = resolve(client)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Caminho '%s' indisponível: %s", label, _describe(exc))
        causes.append((label, exc))
        return
    yield label, resolution


def resolve_latest_serie_historica(
    client: HttpClient,
) -> tuple[str, dt.datetime, dict[str, str] | None]:
    """Resolve a URL, o ``Last-Modified`` e os params da série histórica mais recente.

    Consulta o link curto da fonte e o catálogo (o mesmo do ``sync``) e fica com
    o de modificação mais recente (empate: o link); se um falhar, vale o outro.
    O CKAN é o último recurso. Link que responde erro, página HTML ou sem
    ``Last-Modified`` é abandonado.

    Returns:
        tuple of (download_url, modified_datetime, params_dict).

    Raises:
        FetchError: Se nenhum caminho resolver (a mensagem traz cada causa).
    """
    causes: list[tuple[str, BaseException]] = []
    for label, resolution in _candidates(client, causes):
        logger.info("Série histórica do RTN resolvida pelo caminho '%s'", label)
        return resolution
    raise _fail_all(causes) from (causes[-1][1] if causes else None)


def download_latest_file(destination_dir: Path) -> Path:
    """Download the latest RTN historical series Excel file.

    Resolve o link curto da fonte e o catálogo (o mesmo do ``sync``, que só
    vale com o catálogo real, nunca a lista fixa) e baixa a edição de
    modificação mais recente; o link vence o empate e vale sozinho se o
    catálogo estiver fora. Se o download do escolhido falhar (erro HTTP, tempo
    esgotado, página HTML ou arquivo que não é um ZIP válido, contêiner do
    XLSX), tenta o outro; o CKAN é o último recurso.

    The filename embeds the remote ``Last-Modified`` timestamp, so each new
    upstream version produces a distinct local file. Returns the local path;
    if the file already exists locally, the download is skipped.

    Args:
        destination_dir: Directory where the file should be downloaded.

    Returns:
        Path to the downloaded or existing local file.

    Raises:
        FetchError: If every path fails; the message lists each cause.
    """
    client = _get_client()
    causes: list[tuple[str, BaseException]] = []

    with log_step(logger, "download-rtn-file"):
        for label, (url, modified_date, params) in _candidates(client, causes):
            filename = generate_filename(modified_date)
            destination_path = Path(destination_dir) / filename
            try:
                if is_complete_file(destination_path):
                    logger.info(f"File {filename} already exists, skipping download.")
                    return destination_path

                path = client.download_with_manifest(
                    url,
                    destination_path,
                    source_id=SOURCE_ID,
                    dataset_id=DATASET_ID,
                    producer="rtn-fetcher",
                    params=params,
                    expected_format=_XLSX_FORMAT,
                )
            except Exception as exc:  # noqa: BLE001 - cai para o próximo caminho
                logger.warning(
                    "Caminho '%s' falhou no download, tentando o próximo: %s",
                    label,
                    _describe(exc),
                )
                causes.append((label, exc))
                continue
            if causes:
                logger.info(
                    "Série histórica do RTN baixada pelo caminho '%s' "
                    "(abandonados antes: %s)",
                    label,
                    "; ".join(f"{lb}: {_describe(e)}" for lb, e in causes),
                )
            else:
                logger.info("Série histórica do RTN baixada pelo caminho '%s'", label)
            return path

    raise _fail_all(causes) from (causes[-1][1] if causes else None)


def is_pdf_body(content: bytes) -> bool:
    """Diz se o corpo começa com a assinatura de PDF (``%PDF``)."""
    return content.lstrip(b"\xef\xbb\xbf")[:4] == PDF_SIGNATURE


def validate_pdf_url(url: str) -> str:
    """Valida a URL do PDF real apontada pelo visualizador.

    Só aceita ``https`` em ``tesouro.gov.br`` ou subdomínio, sem credenciais
    embutidas nem porta diferente da padrão.

    Args:
        url: URL lida do ``src`` do iframe.

    Returns:
        A própria URL, sem espaços nas pontas.

    Raises:
        FetchError: Se a URL for relativa ou apontar para outro host.
    """
    url = url.strip()
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    host_ok = host == PDF_HOST_DOMAIN or host.endswith("." + PDF_HOST_DOMAIN)
    try:
        port = parts.port
    except ValueError:
        port = -1
    if (
        parts.scheme != "https"
        or not host_ok
        or parts.username is not None
        or parts.password is not None
        or port not in (None, 443)
    ):
        raise FetchError(f"URL de PDF fora do domínio esperado: {url!r}")
    return url


def extract_pdf_viewer_url(html: str) -> str:
    """Extrai a URL do PDF real da página "Visualização de PDF" do Tesouro.

    Args:
        html: Corpo HTML do visualizador (``<iframe src='...pdf'>``).

    Returns:
        URL validada do PDF.

    Raises:
        FetchError: Se não houver iframe com ``src`` ou se a URL for recusada.
    """
    soup = BeautifulSoup(html, "html.parser")
    iframe = soup.find("iframe")
    src = iframe.get("src") if iframe else None
    if not src:
        raise FetchError("Página recebida no lugar do PDF não tem iframe com src")
    return validate_pdf_url(str(src))


def resolve_pdf_url(client: HttpClient, url: str) -> str:
    """Resolve a URL de um anexo PDF para a URL do arquivo real.

    O endereço de publicação/anexo do Tesouro devolve uma página HTML que
    embute o PDF em um iframe. Se a resposta já for o PDF, devolve ``url``.

    Args:
        client: Cliente HTTP.
        url: URL de publicação ou de anexo.

    Returns:
        URL de onde baixar o PDF.

    Raises:
        FetchError: Se a resposta não for PDF nem um visualizador válido.
    """
    chunks: list[bytes] = []
    size = 0
    with client.stream("GET", url) as response:
        content_type = response.headers.get("Content-Type", "")
        for chunk in response.iter_bytes():
            if not chunks and is_pdf_body(chunk):
                return url  # já é o PDF: não lê o resto do corpo
            chunks.append(chunk)
            size += len(chunk)
            if size > MAX_VIEWER_BYTES:
                raise FetchError(
                    f"Resposta de {url} grande demais para ser um visualizador"
                )
        encoding = response.encoding or "utf-8"
    body = b"".join(chunks)
    if "html" not in content_type.lower() and not body.lstrip().startswith(b"<"):
        raise FetchError(
            f"Resposta de {url} não é PDF nem HTML (Content-Type {content_type!r})"
        )
    return extract_pdf_viewer_url(body.decode(encoding, errors="replace"))


def _check_pdf_before_write(dest_file: Path, content: bytes) -> None:
    """Recusa corpo que não seja PDF quando o destino é ``.pdf``."""
    if Path(dest_file).suffix.lower() == ".pdf" and not is_pdf_body(content):
        raise FetchError(
            f"Corpo recebido para {Path(dest_file).name} não começa com %PDF"
        )


async def download_publication_link(
    client: AsyncHttpClient,
    url: str,
    dest_file: Path,
    *,
    text_encoding: str = "utf-8",
) -> None:
    """Download an RTN publication link, following iframe wrappers.

    Some RTN publication URLs return an HTML page that embeds the actual
    asset (PDF, XLSX, etc.) inside an ``<iframe>``. This helper follows that
    one extra hop transparently and writes the final bytes (or HTML) to
    ``dest_file`` atomically.

    Args:
        client: Async HTTP client instance.
        url: URL of the publication link.
        dest_file: Destination path to save the file.
        text_encoding: Encoding to use if the response is text.
    """
    response = await client.get(url)
    content_type = response.headers.get("Content-Type", "")

    if not content_type.startswith("text/html"):
        write_bytes_atomic(dest_file, response.content)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    iframe = soup.find("iframe")
    iframe_src = iframe.get("src") if iframe else None
    if iframe_src:
        logger.debug(f"Following iframe src: {iframe_src}")
        inner = await client.get(validate_pdf_url(str(iframe_src)))
        _check_pdf_before_write(dest_file, inner.content)
        write_bytes_atomic(dest_file, inner.content)
        return

    write_text_atomic(dest_file, response.text, encoding=text_encoding)


def download_publication_link_sync(
    client: HttpClient,
    url: str,
    dest_file: Path,
    *,
    text_encoding: str = "utf-8",
) -> None:
    """Download an RTN publication link, following iframe wrappers (synchronous).

    Args:
        client: HTTP client instance.
        url: URL of the publication link.
        dest_file: Destination path to save the file.
        text_encoding: Encoding to use if the response is text.
    """
    response = client.get(url)
    content_type = response.headers.get("Content-Type", "")

    if not content_type.startswith("text/html"):
        write_bytes_atomic(dest_file, response.content)
        return

    soup = BeautifulSoup(response.text, "html.parser")
    iframe = soup.find("iframe")
    iframe_src = iframe.get("src") if iframe else None
    if iframe_src:
        logger.debug(f"Following iframe src: {iframe_src}")
        inner = client.get(validate_pdf_url(str(iframe_src)))
        _check_pdf_before_write(dest_file, inner.content)
        write_bytes_atomic(dest_file, inner.content)
        return

    write_text_atomic(dest_file, response.text, encoding=text_encoding)
