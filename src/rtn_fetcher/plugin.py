"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlsplit

from quantilica.cli.sdk import CheckPlanItem, FetcherApp
from quantilica.core.http import HttpClient
from quantilica.core.logging import get_logger
from quantilica.core.registry import FetcherInfo
from quantilica.core.sync import FreshnessPolicy

from .catalog import (
    GROUP_ALIASES,
    GROUPS,
    list_datasets,
    resolve_groups_with_default,
)
from .fetcher import VIEWER_HOST, resolve_pdf_url
from .storage import DataRepository

logger = get_logger(__name__)


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


class RtnFetcherApp(FetcherApp):
    """``FetcherApp`` que baixa o PDF real no lugar da página visualizadora.

    O endereço de cada anexo PDF do Tesouro devolve uma página HTML
    ("Visualização de PDF") com o arquivo num iframe. Antes de baixar ou
    checar um PDF, a entrada passa a apontar para a URL real (validada) e a
    exigir assinatura ``%PDF``; o nome do arquivo no bruto não muda.
    """

    def _resolve_pdf_entry(self, entry: dict[str, Any]) -> dict[str, Any]:
        """Devolve a entrada com a URL do PDF real; outras entradas passam."""
        ext = str(entry.get("ext") or "").lstrip(".").lower()
        if ext != "pdf":
            return entry
        if urlsplit(str(entry["url"])).hostname != VIEWER_HOST:
            return entry  # já é a URL do arquivo (plano do check)
        real_url = resolve_pdf_url(cast(HttpClient, self.client), str(entry["url"]))
        return {**entry, "url": real_url, "expected_format": "pdf"}

    def download_entry(
        self,
        entry: dict[str, Any],
        output_dir: Path,
        *,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> Path:
        """Baixa a entrada; para PDF, resolve o visualizador antes."""
        if not dry_run:
            entry = self._resolve_pdf_entry(entry)
        return super().download_entry(entry, output_dir, dry_run=dry_run, **kwargs)

    def check_entry(self, entry: dict[str, Any], output_dir: Path) -> CheckPlanItem:
        """Confere a entrada; para PDF, confere o arquivo real.

        Se o visualizador não puder ser resolvido, cai na checagem padrão da
        página (o download recusará o corpo inválido).
        """
        try:
            entry = self._resolve_pdf_entry(entry)
        except Exception as exc:  # noqa: BLE001 - checagem é best effort
            logger.warning(
                "PDF %s: visualizador não resolvido: %s", entry.get("id"), exc
            )
        return super().check_entry(entry, output_dir)


fetcher = RtnFetcherApp(
    name="rtn-fetcher",
    help=(
        "Resultado do Tesouro Nacional (RTN). Sem grupo, sync/check usam só "
        "'rtn' (planilhas da série histórica); peça 'rtn-anexos', "
        "'rtn-publicacoes', 'planilhas' ou 'todos' para incluir o resto."
    ),
    info=FetcherInfo(
        id="rtn",
        nome="Resultado do Tesouro Nacional (RTN)",
        aliases=("stn-rtn",),
        orgao="Secretaria do Tesouro Nacional (STN/MF)",
        licenca="Open Data Commons Open Database License (ODbL)",
        homepage="https://www.tesourotransparente.gov.br/ckan/",
        cadencia="monthly",
        dominio="fiscal",
    ),
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
    default_output=Path("/data/rtn"),
    freshness_policy=FreshnessPolicy.HEAD_FALLBACK_GET,
)
# Sem grupo explícito, sync/check usam só a série histórica (o SDK expandiria
# para todos os grupos: ~2.000 arquivos, incluindo PDFs e GIFs desde 1995).
fetcher.resolve_groups = resolve_groups_with_default(fetcher.resolve_groups)


def convert(
    input_dir: Path,
    lake_dir: Path,
    *,
    dataset: list[str] | None = None,
    force: bool = False,
) -> Any:
    """Converte arquivos brutos do RTN para o lake Hive (Parquet)."""
    try:
        from rtn_fetcher import lake
    except ImportError as exc:
        raise ImportError(
            "Conversão para o lake requer o extra 'analysis'. "
            "Instale com: quantilica install rtn --extra analysis"
        ) from exc

    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


fetcher.command_convert(convert)
fetcher.command_pipeline(convert)

app = fetcher.app
