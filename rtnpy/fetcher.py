"""HTTP fetching utilities for RTN data.

This module handles downloading RTN publications and metadata from the
Tesouro Nacional API.
"""

import datetime as dt
from pathlib import Path

import httpx

from .constants import (
    HTTP_DATE_FORMAT,
    HTTP_REQUEST_TIMEOUT,
    RTN_API_BASE_URL,
    RTN_FILE_BASE_URL,
)


def fetch_publications_metadata() -> str:
    """Fetch RTN publications metadata from API.

    Downloads the JSON list of all available RTN publications with their
    metadata including dates, links, and descriptions.

    Returns:
        JSON string containing publications metadata.

    Raises:
        httpx.HTTPError: If the request fails.
    """
    params = {"pageSize": "9999999"}
    response = httpx.get(RTN_API_BASE_URL, params=params, timeout=HTTP_REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.text


def generate_filename(modified_date: dt.datetime) -> str:
    """Generate standardized filename for RTN file.

    Args:
        modified_date: Last modification datetime of the file.

    Returns:
        Filename in format "rtn_YYYYMMDDHHMI.xlsx".
    """
    return f"rtn_{modified_date:%Y%m%d%H%M}.xlsx"


def download_latest_file(destination_dir: Path) -> Path | None:
    """Download the latest RTN historical series Excel file.

    Downloads the file only if it doesn't already exist locally. Uses the
    Last-Modified header to generate a unique filename.

    Args:
        destination_dir: Directory to save the downloaded file.

    Returns:
        Path to the downloaded file, or None if file already exists.

    Raises:
        httpx.HTTPError: If the download fails.
        ValueError: If Last-Modified header is missing or invalid.
    """
    params = {"conteudo": "cdn"}
    response = httpx.get(
        RTN_FILE_BASE_URL,
        params=params,
        follow_redirects=True,
        timeout=HTTP_REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    last_modified_header = response.headers.get("Last-Modified")
    if not last_modified_header:
        raise ValueError("Response missing Last-Modified header")

    modified_date = dt.datetime.strptime(last_modified_header, HTTP_DATE_FORMAT)
    filename = generate_filename(modified_date)
    destination_path = destination_dir / filename

    if destination_path.exists():
        return None

    destination_path.parent.mkdir(exist_ok=True, parents=True)

    with destination_path.open("wb") as file:
        file.write(response.content)

    return destination_path
