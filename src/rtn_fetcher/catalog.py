"""RTN unified dataset catalog.

A página de publicações do RTN lista ~2.000 arquivos desde 1995: a planilha
mensal da série histórica, planilhas de anexos/tabelas antigas (``.xls`` de
1996–2014, "Anexos RTN" ``.xlsx``) e boletins em PDF, GIFs, DOCs etc. O
catálogo separa esses arquivos em grupos para que ``sync``/``check`` sem
argumentos baixem só a série histórica (grupo ``rtn``); os demais exigem
pedido explícito (``rtn-anexos``, ``rtn-publicacoes`` ou os aliases
``planilhas``/``todos``).
"""

import time
import unicodedata
from collections.abc import Callable, Iterable
from typing import Any

from bs4 import BeautifulSoup
from quantilica.core.logging import get_logger

from .constants import (
    KNOWN_SERIE_HISTORICA_ANEXOS,
    RTN_THOT_ARQUIVOS_BASE_URL,
)
from .extract import extract_publication_metadata
from .fetcher import fetch_publications_metadata

logger = get_logger(__name__)

GROUP_SERIE_HISTORICA = "rtn"
GROUP_ANEXOS = "rtn-anexos"
GROUP_PUBLICACOES = "rtn-publicacoes"

GROUPS = {
    GROUP_SERIE_HISTORICA: {
        "name": "Resultado do Tesouro Nacional — série histórica",
        "description": (
            "Planilhas mensais da Série Histórica do RTN "
            "(serie_historica_*.xlsx/.csv). Padrão de sync/check sem grupo."
        ),
    },
    GROUP_ANEXOS: {
        "name": "Resultado do Tesouro Nacional — anexos e tabelas",
        "description": (
            "Demais planilhas publicadas (Anexos RTN, tabelas .xls de 1996 a 2014)."
        ),
    },
    GROUP_PUBLICACOES: {
        "name": "Resultado do Tesouro Nacional — publicações",
        "description": "Boletins e demais arquivos (PDF, GIF, DOC, PPT, links).",
    },
}

GROUP_ALIASES: dict[str, list[str]] = {
    "planilhas": [GROUP_SERIE_HISTORICA, GROUP_ANEXOS],
    "todos": [GROUP_SERIE_HISTORICA, GROUP_ANEXOS, GROUP_PUBLICACOES],
}

# Grupos usados por sync/check quando nenhum grupo é informado.
DEFAULT_GROUPS = [GROUP_SERIE_HISTORICA]

DATA_EXTENSIONS = frozenset({"xlsx", "xls", "csv", "ods"})

# A página de publicações tem ~700 KB e é lida várias vezes por comando
# (``list`` percorre cada grupo e depois soma o total); o cache evita repetir o
# download dentro do mesmo processo sem prender um processo longo a uma lista
# velha.
_CACHE_TTL_SECONDS = 300.0
_cache: tuple[float, list[dict[str, Any]]] | None = None


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def file_extension(filename: str) -> str:
    """Extensão do arquivo em minúsculas, ou ``""`` para links sem extensão."""
    base = filename.rsplit("/", 1)[-1]
    if "." not in base:
        return ""
    return base.rsplit(".", 1)[-1].strip().lower()


def classify_entry(filename: str) -> str:
    """Grupo do catálogo de um arquivo de publicação, pelo nome.

    Args:
        filename: Nome do arquivo (texto do link na página de publicações).

    Returns:
        ``"rtn"`` para as planilhas da série histórica, ``"rtn-anexos"`` para
        as demais planilhas e ``"rtn-publicacoes"`` para todo o resto (PDF,
        GIF, DOC, PPT, links sem extensão).
    """
    ext = file_extension(filename)
    if ext not in DATA_EXTENSIONS:
        return GROUP_PUBLICACOES
    nome = _normalize(filename).replace(" ", "_")
    if nome.startswith("serie_historica"):
        return GROUP_SERIE_HISTORICA
    return GROUP_ANEXOS


def resolve_groups_with_default(
    resolve: Callable[[Iterable[str] | None], list[str]],
) -> Callable[[Iterable[str] | None], list[str]]:
    """Envolve um resolvedor de grupos do SDK para usar ``DEFAULT_GROUPS``.

    O SDK expande "nenhum grupo" para todos os grupos; no RTN isso baixaria
    ~2.000 arquivos. Sem grupo explícito, usa só a série histórica.
    """

    def resolve_default(keys: Iterable[str] | None = None) -> list[str]:
        keys = list(keys) if keys is not None else []
        return resolve(keys or DEFAULT_GROUPS)

    return resolve_default


def _fallback_entries() -> list[dict[str, Any]]:
    """Gera entradas sintéticas para a série histórica a partir dos anexos conhecidos.

    Utilizado quando a API APEX do Tesouro Nacional está fora do ar (ex.: erro 503),
    assegurando que comandos como ``sync`` e ``check`` não abortem com crash e consigam
    baixar as versões mais recentes.
    """
    entries = []
    for (ano, mes), meta in sorted(KNOWN_SERIE_HISTORICA_ANEXOS.items(), reverse=True):
        filename = meta["filename"]
        anexo_id = meta["anexo_id"]
        url = f"{RTN_THOT_ARQUIVOS_BASE_URL}/publicacao-anexo/{anexo_id}"
        entries.append(
            {
                "group": classify_entry(filename),
                "id": filename,
                "url": url,
                "ano_publicacao": ano,
                "mes_publicacao": mes,
                "filename": filename,
                "ext": file_extension(filename) or "xlsx",
            }
        )
    return entries


def _all_entries() -> list[dict[str, Any]]:
    global _cache
    now = time.monotonic()
    if _cache is not None and now - _cache[0] < _CACHE_TTL_SECONDS:
        return _cache[1]

    try:
        html = fetch_publications_metadata()
        soup = BeautifulSoup(html, "html.parser")
        pubs = extract_publication_metadata(soup)
    except Exception as exc:
        logger.warning(
            "API de metadados APEX indisponível (%s). Usando catálogo resiliente.", exc
        )
        entries = _fallback_entries()
        _cache = (now, entries)
        return entries

    entries = []
    for pub in pubs:
        ano = pub.get("ano_publicacao")
        mes = pub.get("mes_publicacao")
        for filename, url in pub.get("links", {}).items():
            entries.append(
                {
                    "group": classify_entry(filename),
                    "id": filename,
                    "url": url,
                    "ano_publicacao": ano,
                    "mes_publicacao": mes,
                    "filename": filename,
                    "ext": file_extension(filename) or "html",
                }
            )
    _cache = (now, entries)
    return entries


def clear_cache() -> None:
    """Descarta o cache da página de publicações (força novo download)."""
    global _cache
    _cache = None


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """Return dataset entries, optionally filtered by group.

    Args:
        group: Grupo do catálogo (``"rtn"``, ``"rtn-anexos"`` ou
            ``"rtn-publicacoes"``). ``None`` devolve todos os arquivos.

    Returns:
        List of dataset entry dictionaries.

    Raises:
        ValueError: If an unknown group is provided.
    """
    if group is not None and group not in GROUPS:
        raise ValueError(f"Unknown group: {group!r}")

    entries = _all_entries()
    if group is None:
        return list(entries)
    return [e for e in entries if e["group"] == group]
