"""Data contracts for RTN sheets.

Builds a quantilica-io DataContract from a SHEET_CONFIGS entry so
that Parquet outputs can be cast and validated against a known schema.
"""

from __future__ import annotations

import polars as pl
from quantilica.analytics.schema import DataContract, Field

from .constants import (
    ACCOUNT_COLUMN,
    MONTH_COLUMN,
    QUARTER_COLUMN,
    VALUE_COLUMN,
    YEAR_COLUMN,
)


def build_contract(
    sheet_name: str,
    sheet_config: dict,
) -> DataContract:
    """Return the DataContract for a given RTN sheet.

    The contract reflects the long-format schema produced by
    ``read_sheet_data``: a period column set (year, plus month or quarter
    when applicable), the account identifier, and the value.
    """
    period = sheet_config["period"]

    fields: list[Field] = [Field(name=YEAR_COLUMN, dtype=pl.Int64)]
    if period == "monthly":
        fields.append(Field(name=MONTH_COLUMN, dtype=pl.Int64))
    elif period == "quarterly":
        fields.append(Field(name=QUARTER_COLUMN, dtype=pl.Int64))

    fields.append(Field(name=ACCOUNT_COLUMN, dtype=pl.Utf8))
    fields.append(Field(name=VALUE_COLUMN, dtype=pl.Float64, required=False))

    return DataContract(
        dataset_id=f"rtn:{sheet_name}",
        fields=fields,
        metadata={"period": period},
    )
