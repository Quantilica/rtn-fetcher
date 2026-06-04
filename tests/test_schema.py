"""Schema-regression tests for RTN sheet contracts."""

import polars as pl
import pytest
from rtn_fetcher import Tbl, build_contract, write_table_to_parquet
from rtn_fetcher.constants import SHEET_CONFIGS


def _monthly_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "year": [2020, 2020, 2021],
            "month": [1, 2, 1],
            "account": ["a", "a", "b"],
            "value": [100.0, 200.0, 300.0],
        }
    )


def _yearly_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "year": [2019, 2020, 2021],
            "account": ["a", "a", "a"],
            "value": [100.0, 200.0, 300.0],
        }
    )


def _quarterly_df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "year": [2020, 2020],
            "quarter": [1, 2],
            "account": ["a", "a"],
            "value": [100.0, 200.0],
        }
    )


class TestBuildContractMonthly:
    contract = build_contract("1.1", SHEET_CONFIGS["1.1"])

    def test_accepts_valid_frame(self):
        self.contract.validate(_monthly_df())

    def test_rejects_missing_month(self):
        df = _monthly_df().drop("month")
        with pytest.raises(ValueError, match="month"):
            self.contract.validate(df)

    def test_rejects_wrong_dtype_on_year(self):
        df = _monthly_df().with_columns(pl.col("year").cast(pl.Utf8))
        with pytest.raises(TypeError, match="year"):
            self.contract.validate(df)

    def test_value_is_optional(self):
        df = _monthly_df().drop("value")
        self.contract.validate(df)


class TestBuildContractYearly:
    contract = build_contract("2.1", SHEET_CONFIGS["2.1"])

    def test_accepts_valid_frame(self):
        self.contract.validate(_yearly_df())

    def test_has_no_month_field(self):
        names = {f.name for f in self.contract.fields}
        assert "month" not in names
        assert "quarter" not in names


class TestBuildContractQuarterly:
    contract = build_contract("4.1", SHEET_CONFIGS["4.1"])

    def test_accepts_valid_frame(self):
        self.contract.validate(_quarterly_df())

    def test_rejects_missing_quarter(self):
        df = _quarterly_df().drop("quarter")
        with pytest.raises(ValueError, match="quarter"):
            self.contract.validate(df)


class TestWriteTableToParquetSchema:
    def test_writes_valid_parquet(self, tmp_path):
        data = Tbl(
            [
                ["year", 2020, 2021],
                ["account", "a", "b"],
                ["value", 100.0, 200.0],
            ]
        )
        out = tmp_path / "rtn.parquet"
        write_table_to_parquet(data, out, "2.1")
        assert out.exists()

        df = pl.read_parquet(out)
        contract = build_contract("2.1", SHEET_CONFIGS["2.1"])
        contract.validate(df)

    def test_rejects_unknown_sheet(self, tmp_path):
        data = Tbl([["year", 2020], ["account", "a"], ["value", 1.0]])
        with pytest.raises(ValueError, match="Unknown sheet"):
            write_table_to_parquet(data, tmp_path / "x.parquet", "9.9")
