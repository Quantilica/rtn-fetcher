
import csv
from pathlib import Path
from typing import Any, Sequence

from .account import expand_account_hierarchy, get_accounts_column
from .excel import Sheet, openwb, to_value
from .extract import get_accounts_data, get_rows
from .table import Tbl, apply, get_header

sheets = [
    "1.1",
    "1.2",
    "1.3",
    "1.4",
    "1.5",
    "1.6",
    "2.1",
    "2.2",
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "4.1",
]


def tbl_values(data: Tbl) -> Tbl:
    return Tbl([apply(col, to_value) for col in data.data])


def rename_accounts_columns_to_codes(data: Tbl, account_hierarchy: Tbl) -> Tbl:
    new_data = data.data.copy()
    for i, account_code in enumerate(account_hierarchy["account_code"][1:], 1):
        new_data[i][0] = account_code
    new_data = Tbl(new_data)
    return new_data


def split_datetime_column(data: Tbl, datetime_column_name: str) -> Tbl:
    new_data = data.data.copy()
    header = get_header(new_data)
    index = header.index(datetime_column_name)
    dates_col = new_data[index]
    year_col = ["year"] + [dt.year for dt in dates_col[1:]]
    new_data[index] = year_col
    month_col = ["month"] + [dt.month for dt in dates_col[1:]]
    new_data.insert(index + 1, month_col)
    new_data = Tbl(new_data)
    return new_data


def _read(
    sh: Sheet,
    rows: Sequence[int],
    drop_cols: Sequence[int] = (),
    period: str = "monthly",
) -> tuple[Tbl]:
    data = Tbl(get_rows(sh, *rows))
    if drop_cols:
        data = data.drop_cols(drop_cols)
    data.data[0][0] = "date"
    accounts_data = get_accounts_data(get_accounts_column(data))
    account_hierarchy = expand_account_hierarchy(accounts_data)
    data = tbl_values(data)
    data = data.melt(
        id_cols=["date"],
        var_name="account",
    )
    if period == "monthly":
        data = split_datetime_column(data, "date")
    elif period == "yearly":
        data = data.rename(date="year")
    return data, account_hierarchy


def read(filepath: Path) -> dict:

    def to_million(x: Any) -> int:
        if x == "n.a.":
            return None
        return int(x) * 1_000_000

    def read_1_2(wb) -> tuple[Tbl]:
        sh = wb["1.2"]
        data, account_hierarchy = _read(sh, rows=(5, 162), period="monthly")
        data = data.assign(
            value=apply(data["value"][1:], to_million),
        )
        return data, account_hierarchy

    def read_1_3(wb) -> tuple[Tbl]:
        sh = wb["1.3"]
        data, account_hierarchy = _read(sh, rows=(5, 65), drop_cols=[1], period="monthly")
        data = data.assign(
            value=apply(data["value"][1:], to_million),
        )
        return data, account_hierarchy

    def read_1_6(wb) -> tuple[Tbl]:
        sh = wb["1.6"]
        data, account_hierarchy = _read(sh, rows=(5, 24), period="monthly")
        data = data.assign(
            value=apply(data["value"][1:], to_million),
        )
        return data, account_hierarchy

    def read_2_2_a(wb) -> tuple[Tbl]:
        sh = wb["2.2-A"]
        data, account_hierarchy = _read(sh, rows=(5, 162), period="yearly")
        data = data.assign(
            value=apply(data["value"][1:], to_million),
        )
        return data, account_hierarchy

    wb = openwb(filepath)

    data_1_2 = read_1_2(wb)
    # data_1_3 = read_1_3(wb)
    # data_1_6 = read_1_6(wb)
    # data_2_2_a = read_2_2_a(wb)

    # return {
    #     "1.2": data_1_2,
    #     "1.3": data_1_3,
    #     "1.6": data_1_6,
    #     "2.2-A": data_2_2_a,
    # }


def write_csv(data: Tbl, filepath: Path):
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f, delimiter=",", dialect=csv.QUOTE_ALL)
        writer.writerows(data.transpose().data)
