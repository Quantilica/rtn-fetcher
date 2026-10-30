"""Convert raw RTN Excel workbooks into the Hive-partitioned lake.

Each statistical sheet from the RTN Série Histórica lands in
``<lake>/rtn/<tabela-id>/<file_key>.parquet`` (unpartitioned historical time series).
Columns are normalized into long format with account hierarchies, dates, and values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

try:
    import polars as pl
    from quantilica.analytics.lake import LakeError, LakeWriter
    from quantilica.core.lake import DatasetDescriptor
except ImportError as exc:
    raise ImportError(
        "rtn_fetcher.lake requer o extra 'analysis': "
        "uv add 'rtn-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from rtn_fetcher import __version__
from rtn_fetcher.constants import SHEET_CONFIGS
from rtn_fetcher.dataframe import to_polars
from rtn_fetcher.excel import Workbook, open_workbook
from rtn_fetcher.reader import read_workbook_sheet
from rtn_fetcher.schema import build_contract

if TYPE_CHECKING:  # só tipagem: o core publicado antes do contrato não tem Planned
    from quantilica.core.lake import Planned

SOURCE_ID = "rtn"

# Formatos que o conversor não lê: documentos, imagens e páginas salvas de
# links. O resto é planilha ou outro dado.
_NON_TABULAR_SUFFIXES = frozenset(
    {
        ".pdf",
        ".doc",
        ".docx",
        ".odt",
        ".rtf",
        ".ppt",
        ".pptx",
        ".odp",
        ".gif",
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".svg",
        ".html",
        ".htm",
    }
)

_MANIFEST_SUFFIX = ".manifest.json"
_TEMP_SUFFIX = ".tmp"


def _is_sidecar(path: Path) -> bool:
    """Se o arquivo é sidecar de manifest ou resto ``.tmp``, não dado bruto."""
    return path.name.endswith(_MANIFEST_SUFFIX) or path.name.endswith(_TEMP_SUFFIX)


def _is_non_tabular(path: Path) -> bool:
    """Se o conversor não lê o arquivo: documento, imagem, página ou trava do Excel."""
    return (
        path.name.startswith("~$")
        or not path.suffix
        or path.suffix.lower() in _NON_TABULAR_SUFFIXES
    )


def _base_name(path: Path) -> str:
    """Nome sem a extensão final, para achar o mesmo conteúdo em outro formato."""
    return path.stem.casefold()


def _is_twin(path: Path, chosen: Path) -> bool:
    """Se ``path`` é o mesmo conteúdo de ``chosen`` em outro formato."""
    return path.parent == chosen.parent and _base_name(path) == _base_name(chosen)


def sheet_to_dataset_id(sheet_name: str) -> str:
    """Normalize sheet name into dataset id (e.g. '1.1' -> 'tabela-1-1')."""
    return f"tabela-{sheet_name.replace('.', '-').lower()}"


def dataset_id_to_sheet(dataset_id: str) -> str | None:
    """Map dataset id back to sheet name if matched."""
    for s in SHEET_CONFIGS:
        if sheet_to_dataset_id(s) == dataset_id or s == dataset_id:
            return s
    return None


@dataclass
class ConvertResult:
    """Counts of a conversion run; ``errors`` holds one message per failure."""

    converted: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def latest_workbook(input_dir: Path) -> list[Path]:
    """A série histórica mais recente (uma lista vazia ou de um item).

    Cada série histórica mensal traz o histórico inteiro, e cada aba vira um Parquet
    de chave fixa: converter todas as pastas só refazia o trabalho, e os layouts
    antigos (anexos de 1995 a 2022) falhavam. Vale a mais recente pela pasta do
    mês; os arquivos ``serie_historica*`` têm preferência sobre os anexos.
    """
    workbooks = sorted(
        p for p in Path(input_dir).rglob("*.xlsx") if not p.name.startswith("~$")
    )
    series = [p for p in workbooks if p.name.lower().startswith("serie_historica")]
    chosen = series or workbooks
    return chosen[-1:]


def workbook_sheets(workbook: Workbook) -> list[str]:
    """Abas que ``convert`` lê, na ordem de ``SHEET_CONFIGS``.

    Compartilhada por :meth:`LakeConverter.convert` e
    :meth:`LakeConverter.inventory`, para o inventário refletir exatamente as
    abas que o conversor percorre.
    """
    return [sheet for sheet in SHEET_CONFIGS if sheet in workbook.sheetnames]


class LakeConverter:
    """Converter registered under the ``quantilica.lake`` entry point."""

    source_id = SOURCE_ID

    def datasets(self) -> list[str]:
        """Dataset ids this converter writes to the lake."""
        return [sheet_to_dataset_id(s) for s in SHEET_CONFIGS]

    def convert(
        self,
        input_dir: Path,
        lake_dir: Path,
        *,
        datasets: list[str] | None = None,
        force: bool = False,
    ) -> ConvertResult:
        """Convert raw RTN workbooks into ``lake_dir``.

        Args:
            input_dir: Root directory containing raw files.
            lake_dir: Root of the lake.
            datasets: Optional list of dataset ids or sheet names to convert.
            force: Reconvert even if sha256 already matches in the lake.

        Returns:
            ConvertResult: Files converted, skipped, and error messages.
        """
        input_dir = Path(input_dir)
        lake_dir = Path(lake_dir)
        result = ConvertResult()
        if not input_dir.is_dir():
            result.errors.append(f"diretório '{input_dir}' não existe")
            return result

        allowed_sheets: set[str] | None = None
        if datasets:
            allowed_sheets = set()
            for d in datasets:
                sheet = dataset_id_to_sheet(d)
                if sheet:
                    allowed_sheets.add(sheet)
                else:
                    result.errors.append(f"dataset desconhecido: {d}")
            if result.errors:
                return result

        workbooks = latest_workbook(input_dir)
        if not workbooks:
            return result

        for path in workbooks:
            try:
                wb = open_workbook(path)
            except Exception as exc:
                result.errors.append(f"{path.name}: erro ao abrir workbook: {exc}")
                continue

            sheets_to_process = [
                sheet
                for sheet in workbook_sheets(wb)
                if allowed_sheets is None or sheet in allowed_sheets
            ]

            for sheet_name in sheets_to_process:
                dataset_id = sheet_to_dataset_id(sheet_name)
                writer = LakeWriter(
                    lake_dir / SOURCE_ID / dataset_id,
                    DatasetDescriptor(
                        source_id=SOURCE_ID,
                        dataset_id=dataset_id,
                        alias=sheet_name,
                        partition_keys=[],
                        partition_types={},
                    ),
                    force=force,
                )

                try:
                    data, _ = read_workbook_sheet(wb, sheet_name)
                    df = to_polars(data)
                    contract = build_contract(sheet_name, SHEET_CONFIGS[sheet_name])
                    df = contract.cast(df)

                    written = writer.write_polars(
                        df,
                        path,
                        file_key_name=sheet_name.replace(".", "-"),
                        converter=f"rtn-fetcher {__version__}",
                    )
                    if written.status == "skipped":
                        result.skipped += 1
                    else:
                        result.converted += 1
                except (
                    LakeError,
                    OSError,
                    pl.exceptions.PolarsError,
                    Exception,
                ) as exc:
                    message = str(exc).strip()
                    first_line = message.splitlines()[0] if message else repr(exc)
                    result.errors.append(f"{path.name}:{sheet_name}: {first_line}")
                    continue

        return result

    def inventory(self, input_dir: Path) -> list[Planned]:
        """Um ``Planned`` por dataset (ou motivo de ignorar) de cada arquivo.

        Espelha a descoberta de :meth:`convert` (mesma :func:`latest_workbook`
        e mesmas abas de :func:`workbook_sheets`): só a série histórica mais
        recente é aberta, e cada aba dela vira um dataset. Os demais arquivos
        vêm com o motivo de serem ignorados: gêmeo de outro formato da mesma
        base (``"gemeo"``), documento, imagem ou página (``"nao_tabular"``) e
        publicação anterior, como as séries de meses passados e os anexos
        antigos (``"superado"``). Sidecars ``*.manifest.json`` e restos
        ``*.tmp`` não entram no inventário.

        Uma planilha pode alimentar mais de um dataset (uma aba por tabela),
        então ela aparece uma vez por dataset que ``convert`` escreveria.

        Args:
            input_dir: Raiz dos arquivos brutos do RTN (a mesma de ``convert``).

        Returns:
            list[Planned]: Um item por dataset de cada arquivo, ou um item com
            o motivo de ignorá-lo.
        """
        # Import local: o core publicado antes do contrato não tem ``Planned``.
        from quantilica.core.lake import Planned

        input_dir = Path(input_dir)
        if not input_dir.is_dir():
            return []

        planned: list[Planned] = []
        workbooks = latest_workbook(input_dir)
        chosen = workbooks[-1] if workbooks else None

        if chosen is not None:
            try:
                workbook = open_workbook(chosen)
            except Exception:  # o inventário não pode falhar por planilha ilegível
                workbook = None
            if workbook is None:
                # O conversor também não grava nada: fica sem destino para a
                # auditoria apontar a lacuna em vez de supor um Parquet.
                planned.append(Planned(chosen))
            else:
                try:
                    for sheet in workbook_sheets(workbook):
                        planned.append(
                            Planned(chosen, dataset=sheet_to_dataset_id(sheet))
                        )
                finally:
                    workbook.close()

        for path in sorted(input_dir.rglob("*")):
            if not path.is_file() or path == chosen or _is_sidecar(path):
                continue
            if _is_non_tabular(path):
                planned.append(Planned(path, skip_reason="nao_tabular"))
            elif chosen is not None and _is_twin(path, chosen):
                planned.append(Planned(path, skip_reason="gemeo"))
            elif chosen is not None:
                planned.append(Planned(path, skip_reason="superado"))
            else:
                planned.append(Planned(path))
        return planned


converter = LakeConverter()
