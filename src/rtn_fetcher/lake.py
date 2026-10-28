"""Convert raw RTN Excel workbooks into the Hive-partitioned lake.

Each statistical sheet from the RTN Série Histórica lands in
``<lake>/rtn/<tabela-id>/<file_key>.parquet`` (unpartitioned historical time series).
Columns are normalized into long format with account hierarchies, dates, and values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

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
from rtn_fetcher.excel import open_workbook
from rtn_fetcher.reader import read_workbook_sheet
from rtn_fetcher.schema import build_contract

SOURCE_ID = "rtn"


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
                s
                for s in SHEET_CONFIGS
                if s in wb.sheetnames
                and (allowed_sheets is None or s in allowed_sheets)
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


converter = LakeConverter()
