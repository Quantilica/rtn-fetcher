
import csv
import re
from typing import Union

from .account import (account_code_to_list_ints, expand_account_hierarchy,
                      get_accounts_column, list_ints_to_account_code,
                      parse_column_name)
from .excel import Cell, get_indent, openwb
from .extract import get_accounts_data, get_rows
from .table import Table, apply, melt, split_datetime_column, transpose

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


def insert_accounts_data(data, accounts_data) -> Table:
    new_data = [["account_name", "account_code", *data[0][2:]]]
    for row, (account_code, account_name) in zip(data[1:], accounts_data):
        new_data.append([account_name, account_code, *row[2:]])
    return new_data


def insert_account_hierarchy(data, account_hierarchy) -> Table:
    new_data = [account_hierarchy[0] + data[0][1:]]
    for row, accounts in zip(data[1:], account_hierarchy[1:]):
        new_data.append(accounts + row[1:])
    return new_data


def insert_account_codes(data: Table, account_hierarchy: Table) -> Table:
    new_data = [["account_code"] + data[0][1:]]
    for row, accounts in zip(data[1:], account_hierarchy[1:]):
        account_code = [accounts[0]]
        original_row = row[1:]
        new_data.append(account_code + original_row)
    return new_data


def value_column_to_int(data: Table, value_column_name: str,
                        by_value: Union[int, float] = 1_000_000) -> Table:
    new_data = apply(
        data=data,
        column_name=value_column_name,
        func=lambda x: x.value * by_value,
    )
    return new_data


def read_1_1(wb) -> tuple[Table]:
    sh = wb["1.1"]
    data = list(get_rows(sh, 5, 73))
    accounts = get_accounts_column(data)
    accounts_data = get_accounts_data(accounts)
    account_hierarchy = expand_account_hierarchy(accounts_data)
    data = insert_account_codes(data, account_hierarchy)
    data = melt(
        data,
        id_cols=["account_code"],
        var_name="date",
    )
    data = value_column_to_int(data, value_column_name="value")
    data = apply(data, "date", lambda x: x.value)
    data = split_datetime_column(data, datetime_column_name="date")
    return data, account_hierarchy


def read_1_2(wb) -> tuple[Table]:
    sh = wb["1.2"]
    data = list(get_rows(sh, 5, 162))
    accounts = get_accounts_column(data)
    accounts_data = get_accounts_data(accounts)
    account_hierarchy = expand_account_hierarchy(accounts_data)
    data = insert_account_codes(data, account_hierarchy)
    data = melt(
        data,
        id_cols=["account_code"],
        var_name="date",
    )
    data = value_column_to_int(data, value_column_name="value")
    data = apply(data, "date", lambda x: x.value)
    data = split_datetime_column(data, datetime_column_name="date")
    return data, account_hierarchy


def write_csv(data, filepath):
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f, delimiter=",", dialect=csv.QUOTE_ALL)
        writer.writerows(data)
