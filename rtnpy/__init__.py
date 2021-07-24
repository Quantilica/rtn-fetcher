
import csv
import os
import pathlib
from typing import Union

from .account import (account_code_to_list_ints, expand_account_hierarchy,
                      get_accounts_column, list_ints_to_account_code,
                      parse_column_name)
from .excel import Cell, get_indent, openwb, to_value
from .extract import get_accounts_data, get_rows
from .table import (Column, Matrix, Tbl, apply, assign, drop_rows, get_header,
                    insert, iter_rows, melt, select, transpose, where)

Filepath = Union[pathlib.Path, str, os.PathLike]

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


def insert_account_codes(data: Tbl, account_hierarchy: Tbl) -> Tbl:
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


def value_column_to_int(column: list[float],
                        by_value: Union[int, float] = 1_000_000) -> Column:
    return apply(
        column=column,
        func=lambda x: int(x * by_value),
    )


def read_1_1(wb) -> tuple[Tbl]:
    sh = wb["1.1"]
    data = Tbl(get_rows(sh, 5, 73))
    data = data.drop_cols([1])
    data.data[0][0] = "date"
    accounts_data = get_accounts_data(get_accounts_column(data))
    account_hierarchy = expand_account_hierarchy(accounts_data)
    data = tbl_values(data)
    data = insert_account_codes(data, account_hierarchy)
    data = data.melt(
        id_cols=["date"],
        var_name="account_code",
    )
    data = data.assign(
        value=apply(data["value"][1:], lambda x: int(1_000_000 * x)),
    )
    data = split_datetime_column(data, "date")
    return data, account_hierarchy


def read_1_2(wb) -> tuple[Tbl]:
    sh = wb["1.2"]
    data = Tbl(get_rows(sh, 5, 162))
    data = data.drop_cols([1])
    data.data[0][0] = "date"
    accounts_data = get_accounts_data(get_accounts_column(data))
    account_hierarchy = expand_account_hierarchy(accounts_data)
    data = tbl_values(data)
    data = insert_account_codes(data, account_hierarchy)
    data = data.melt(
        id_cols=["date"],
        var_name="account_code",
    )
    data = data.assign(
        value=apply(data["value"][1:], lambda x: int(1_000_000 * x)),
    )
    data = split_datetime_column(data, "date")
    return data, account_hierarchy


def read_1_3(wb) -> tuple[Tbl]:
    sh = wb["1.3"]
    data = Tbl(get_rows(sh, 5, 65))
    data = data.drop_cols([1])
    data.data[0][0] = "date"
    accounts_data = get_accounts_data(get_accounts_column(data))
    account_hierarchy = expand_account_hierarchy(accounts_data)
    data = tbl_values(data)
    data = insert_account_codes(data, account_hierarchy)
    data = data.melt(
        id_cols=["date"],
        var_name="account_code",
    )
    data = data.assign(
        value=apply(data["value"][1:], lambda x: int(1_000_000 * x)),
    )
    data = split_datetime_column(data, "date")
    return data, account_hierarchy


def read_1_6(wb) -> tuple[Tbl]:
    pass


def write_csv(data: Tbl, filepath):
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f, delimiter=",", dialect=csv.QUOTE_ALL)
        writer.writerows(data.transpose().data)
