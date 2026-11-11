"""HTTP fetching utilities for RTN data.

This module handles downloading RTN publications and metadata from the
Tesouro Nacional API.
"""

import datetime as dt
from pathlib import Path

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
    KNOWN_SERIE_HISTORICA_ANEXOS,
    RTN_API_BASE_URL,
    RTN_CKAN_PACKAGE_URL,
    RTN_FILE_BASE_URL,
    RTN_THOT_ARQUIVOS_BASE_URL,
)

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


def resolve_latest_serie_historica(
    client: HttpClient,
) -> tuple[str, dt.datetime, dict[str, str] | None]:
    """Resolve the URL, Last-Modified date, and request params for latest RTN file.

    Follows a multi-tier fallback strategy:
    1. Legacy permalink (RTN_FILE_BASE_URL) with short timeout (5s).
    2. THOT-Arquivos microservice / CDN using known attachments.
    3. CKAN Open Data API package resource.

    Returns:
        tuple of (download_url, modified_datetime, params_dict).

    Raises:
        ParseError: If unable to determine a valid Last-Modified timestamp.
        FetchError: If all upstream sources fail.
    """
    # 1. Tentativa via permalink legado do sisweb
    try:
        head = client.head_or_get(
            RTN_FILE_BASE_URL,
            params={"conteudo": "cdn"},
        )
        if head.status_code < 400:
            last_modified_header = head.headers.get("Last-Modified")
            if last_modified_header:
                modified_date = dt.datetime.strptime(
                    last_modified_header, HTTP_DATE_FORMAT
                )
                return RTN_FILE_BASE_URL, modified_date, {"conteudo": "cdn"}
    except Exception as exc:
        logger.warning(
            "Upstream permalink legado (%s) indisponível: %s. "
            "Ativando fallback resiliente.",
            RTN_FILE_BASE_URL,
            exc,
        )

    # 2. Resolução via THOT-Arquivos / CDN
    try:
        sorted_editions = sorted(KNOWN_SERIE_HISTORICA_ANEXOS.items(), reverse=True)
        for (ano, mes), meta in sorted_editions:
            anexo_id = meta["anexo_id"]
            url = f"{RTN_THOT_ARQUIVOS_BASE_URL}/publicacao-anexo/{anexo_id}"
            head = client.head_or_get(url)
            if head.status_code < 400:
                last_modified_header = head.headers.get("Last-Modified")
                if last_modified_header:
                    modified_date = dt.datetime.strptime(
                        last_modified_header, HTTP_DATE_FORMAT
                    )
                    final_url = str(head.url) if head.url else url
                    logger.info(
                        "Resolvido arquivo RTN (%02d/%d) via THOT-Arquivos: %s",
                        mes,
                        ano,
                        final_url,
                    )
                    return final_url, modified_date, None
    except Exception as exc:
        logger.warning(
            "Resolução via THOT-Arquivos falhou (%s). Tentando CKAN.",
            exc,
        )

    # 3. Resolução via CKAN Open Data API
    try:
        data = client.get_json(RTN_CKAN_PACKAGE_URL)
        resources = data.get("result", {}).get("resources", [])
        for r in resources:
            r_name = r.get("name", "").lower()
            r_url = r.get("url", "").lower()
            is_xlsx = r.get("format", "").upper() == "XLSX"
            is_serie = any(
                k in r_name or k in r_url
                for k in ["serie", "série", "historica", "histórica"]
            )
            if is_xlsx and is_serie:
                ckan_url = r.get("url")
                if ckan_url:
                    head = client.head_or_get(ckan_url)
                    last_modified_header = head.headers.get("Last-Modified")
                    if last_modified_header:
                        modified_date = dt.datetime.strptime(
                            last_modified_header, HTTP_DATE_FORMAT
                        )
                        logger.info("Resolvido arquivo RTN via CKAN: %s", ckan_url)
                        return ckan_url, modified_date, None
                    ckan_lm = r.get("last_modified")
                    if ckan_lm:
                        modified_date = dt.datetime.fromisoformat(ckan_lm)
                        logger.info(
                            "Resolvido arquivo RTN via CKAN (meta): %s", ckan_url
                        )
                        return ckan_url, modified_date, None
    except Exception as exc:
        logger.warning("Resolução via CKAN falhou: %s", exc)

    raise FetchError(
        "Não foi possível resolver a Série Histórica do RTN: todos os endpoints "
        "(sisweb, thot-arquivos e CKAN) falharam ou estão indisponíveis."
    )


def download_latest_file(destination_dir: Path) -> Path:
    """Download the latest RTN historical series Excel file.

    The filename embeds the remote ``Last-Modified`` timestamp, so each new
    upstream version produces a distinct local file. Returns the local path;
    if the file already exists locally, the download is skipped.

    Args:
        destination_dir: Directory where the file should be downloaded.

    Returns:
        Path to the downloaded or existing local file.

    Raises:
        ParseError: If the server response lacks a Last-Modified header or it's invalid.
        FetchError: If all upstream sources are unavailable.
    """
    client = _get_client()

    with log_step(logger, "download-rtn-file"):
        url, modified_date, params = resolve_latest_serie_historica(client)
        filename = generate_filename(modified_date)
        destination_path = Path(destination_dir) / filename

        if is_complete_file(destination_path):
            logger.info(f"File {filename} already exists, skipping download.")
            return destination_path

        return client.download_with_manifest(
            url,
            destination_path,
            source_id=SOURCE_ID,
            dataset_id=DATASET_ID,
            producer="rtn-fetcher",
            params=params,
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
        inner = await client.get(str(iframe_src))
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
        inner = client.get(str(iframe_src))
        write_bytes_atomic(dest_file, inner.content)
        return

    write_text_atomic(dest_file, response.text, encoding=text_encoding)
