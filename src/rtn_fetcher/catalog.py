"""RTN unified dataset catalog."""

from typing import Any

from bs4 import BeautifulSoup

from .extract import extract_publication_metadata
from .fetcher import fetch_publications_metadata

GROUPS = {
    "rtn": {
        "name": "Resultado do Tesouro Nacional",
        "description": "Série Histórica do Resultado do Tesouro Nacional",
    }
}

GROUP_ALIASES: dict[str, list[str]] = {}


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """Return all dataset entries, optionally filtered by group."""
    if group is not None and group != "rtn":
        raise ValueError(f"Unknown group: {group!r}")

    html = fetch_publications_metadata()
    soup = BeautifulSoup(html, "html.parser")
    pubs = extract_publication_metadata(soup)

    entries = []
    for pub in pubs:
        ano = pub.get("ano_publicacao")
        mes = pub.get("mes_publicacao")
        for filename, url in pub.get("links", {}).items():
            ext = filename.split(".")[-1] if "." in filename else "xlsx"
            entries.append(
                {
                    "group": "rtn",
                    "id": filename,
                    "url": url,
                    "ano_publicacao": ano,
                    "mes_publicacao": mes,
                    "filename": filename,
                    "ext": ext,
                }
            )
    return entries
