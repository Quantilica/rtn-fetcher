"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.cli.sdk import FetcherApp

from .catalog import (
    GROUP_ALIASES,
    GROUPS,
    list_datasets,
    resolve_groups_with_default,
)
from .storage import DataRepository


def path_builder(
    output_dir: Path, entry: dict[str, Any], last_modified: dt.date | None
) -> Path:
    """Build the destination path for a publication entry.

    Args:
        output_dir: Base directory for output.
        entry: The publication entry dictionary.
        last_modified: Optional last modified date.

    Returns:
        The destination path.
    """
    return DataRepository(output_dir).path_for_entry(entry, last_modified=last_modified)


fetcher = FetcherApp(
    name="rtn-fetcher",
    help=(
        "Resultado do Tesouro Nacional (RTN). Sem grupo, sync/check usam só "
        "'rtn' (planilhas da série histórica); peça 'rtn-anexos', "
        "'rtn-publicacoes', 'planilhas' ou 'todos' para incluir o resto."
    ),
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
)
# Sem grupo explícito, sync/check usam só a série histórica (o SDK expandiria
# para todos os grupos: ~2.000 arquivos, incluindo PDFs e GIFs desde 1995).
fetcher.resolve_groups = resolve_groups_with_default(fetcher.resolve_groups)

app = fetcher.app
