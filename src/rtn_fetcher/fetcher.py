"""HTTP fetching utilities for RTN data.

This module handles downloading RTN publications and metadata from the
Tesouro Nacional API.
"""

import datetime as dt
from pathlib import Path

import quantilica_core.metadata as core_meta
from bs4 import BeautifulSoup
from quantilica_core.exceptions import ParseError
from quantilica_core.files import write_bytes_atomic, write_text_atomic
from quantilica_core.http import AsyncHttpClient, HttpClient
from quantilica_core.logging import log_step
from quantilica_core.storage import stamp_filename

from . import logger
from .constants import (
    HTTP_DATE_FORMAT,
    RTN_API_BASE_URL,
    RTN_FILE_BASE_URL,
)

client = HttpClient(timeout=60.0)

SOURCE_ID = "tesouro-nacional"
DATASET_ID = "rtn"


def fetch_publications_metadata() -> str:
    """Fetch RTN publications metadata from API."""
    params = {"pageSize": "9999999"}
    with log_step(logger, "fetch-rtn-metadata"):
        return client.get_text(RTN_API_BASE_URL, params=params)


def generate_filename(modified_date: dt.datetime) -> str:
    """Generate a stamped filename for the RTN file.

    Returns ``rtn@YYYYMMDDTHHMMSS.xlsx`` using the upstream Last-Modified
    timestamp so each new version produces a distinct local file.
    """
    return stamp_filename("rtn", "xlsx", modified_date, precision="datetime")


def download_latest_file(destination_dir: Path) -> Path:
    """Download the latest RTN historical series Excel file.

    The filename embeds the remote ``Last-Modified`` timestamp, so each new
    upstream version produces a distinct local file. Returns the local path;
    if the file already exists locally, the download is skipped.
    """
    params = {"conteudo": "cdn"}

    with log_step(logger, "download-rtn-file"):
        head = client.head_or_get(RTN_FILE_BASE_URL, params=params)
        last_modified_header = head.headers.get("Last-Modified")
        if not last_modified_header:
            raise ParseError("Response missing Last-Modified header")

        try:
            modified_date = dt.datetime.strptime(
                last_modified_header, HTTP_DATE_FORMAT
            )
        except ValueError as exc:
            raise ParseError(
                f"Invalid Last-Modified date format: {last_modified_header}"
            ) from exc

        filename = generate_filename(modified_date)
        destination_path = Path(destination_dir) / filename

        if destination_path.exists():
            logger.info(f"File {filename} already exists, skipping download.")
            return destination_path

        return client.download_with_manifest(
            RTN_FILE_BASE_URL,
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


def generate_catalog(rtn_files: list[Path]) -> core_meta.MetadataCatalog:
    """Build a validated MetadataCatalog for the given RTN files."""
    source = core_meta.Source(
        id=SOURCE_ID,
        name="Tesouro Nacional",
        homepage_url="https://www.tesouro.fazenda.gov.br",
    )
    dataset = core_meta.Dataset(
        id=DATASET_ID,
        source_id=SOURCE_ID,
        name="Resultado do Tesouro Nacional (RTN)",
        description="Série Histórica do Resultado do Tesouro Nacional",
    )
    resources = [
        core_meta.Resource(
            id=file_path.name.replace(".", "_"),
            dataset_id=DATASET_ID,
            name=file_path.name,
            url=RTN_FILE_BASE_URL,
            format="xlsx",
            path=str(file_path.absolute()),
        )
        for file_path in rtn_files
    ]
    return core_meta.build_simple_catalog(source, dataset, resources)
