
import csv
import datetime
import pathlib
import re
from typing import Union, Any

import openpyxl

Table = list[list[Any]]

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


def get_rows(sh, min_row=0, max_row=1_048_576) -> Table:
    rows = []
    for row in sh.iter_rows(min_row=min_row, max_row=max_row):
        if row[0].value:
            row = [cell for cell in row if cell.value is not None]
            if len(row) < 3:
                continue
            rows.append(row)
    return rows


def get_accounts_column(rows):
    return [row[0] for row in rows[1:]]


def get_indent(cell):
    return cell.alignment.indent


def transpose(data) -> Table:
    return list(zip(*data))


def clean_name(name):
    name = re.sub(r" +", " ", name)
    name = re.sub(r" \d+/$", "", name)
    name = name.strip(" -")
    return name


def melt(data: list[list[Any]],
         id_cols: list[str],
         var_name="variable",
         value_name="value",
         get_value=True) -> Table:
    columns = data[0]
    index_id_cols = [columns.index(id_col) for id_col in id_cols]
    header = [*id_cols, var_name, value_name]
    new_data = [header]
    for row in data[1:]:
        id_values = [row[i] for i in index_id_cols]
        for i, cell in enumerate(row):
            if i in index_id_cols:  # cell is in id_cols
                continue
            if get_value:
                output_row = id_values + [columns[i].value, cell.value]
            else:
                output_row = id_values + [columns[i], cell]
            new_data.append(output_row)
    return new_data


def parse_column_name(name):

    # Initialize variables
    account_code = account_name = ""

    match = re.match(r"^\d+((\.\d+)+|\.)", name)
    if match:
        account_code = match.group().strip()
    account_name = clean_name(name.replace(account_code, ""))
    account_code = account_code.replace(".", "=>")

    return account_code, account_name


def account_code_to_list_ints(account_code):
    return [int(code) for code in account_code.split("=>") if code]


def list_ints_to_account_code(account_code):
    return "=>".join([str(code) for code in account_code])


def process_accounts(accounts):
    accounts_data = []
    last_indent = 0
    last_account_code = account_code_root = []
    counter = 1
    for account in accounts:
        indent = get_indent(account)
        indent_change = indent - last_indent
        account_code, account_name = parse_column_name(account.value)
        if indent_change == 0 and account_name.startswith("d/q"):
            indent_change += 1
        account_code = account_code_to_list_ints(account_code)
        if not account_code:
            if indent_change > 0:
                account_code_root = last_account_code
                counter = 1
            elif indent_change < 0:
                account_code_root = account_code_root[:-1]
            account_code = account_code_root + [counter]
            counter += 1
        last_account_code = account_code
        last_indent = indent
        accounts_data.append(
            [
                list_ints_to_account_code(account_code),
                account_name,
            ],
        )
    return accounts_data


def expand_account_hierarchy(accounts_data) -> Table:
    maxlevel = max(map(lambda t: len(t[0].split("=>")), accounts_data))
    path = [f"P_{i}" for i in range(1, maxlevel+1)]
    account_hierarchy = [["account_code", "account_name"] + path]
    last_row = (maxlevel+1) * [None]
    for account_code, name in accounts_data:
        list_int_account_code = account_code.split("=>")
        level = len(list_int_account_code)
        full_account_name = ".".join(list_int_account_code) + " " + name
        row = [account_code, full_account_name] + last_row[:level-1] + [name] + ((maxlevel-level) * [None])
        account_hierarchy.append(row)
        last_row = row[2:]
    return account_hierarchy


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


def insert_account_codes(data, account_hierarchy) -> Table:
    new_data = [["account_code"] + data[0][1:]]
    for row, accounts in zip(data[1:], account_hierarchy[1:]):
        account_code = [accounts[0]]
        original_row = row[1:]
        new_data.append(account_code + original_row)
    return new_data


def value_column_to_int(data, value_column_name, by_value: Union[int, float] = 1_000_000) -> Table:
    new_data = [data[0]]
    index = data[0].index(value_column_name)
    for row in data[1:]:
        row[index] = int(row[index] * by_value)
        new_data.append(row)
    return new_data


def split_datetime_column(data, datetime_column_name) -> Table:
    header: list = data[0]
    index = header.index(datetime_column_name)
    header[index] = "year"
    header.insert(index + 1, "month")
    new_data = [header]
    for row in data[1:]:
        year = row[index].year
        month = row[index].month
        row[index] = year
        row.insert(index + 1, month)
        new_data.append(row)
    return new_data


def openwb(filepath):
    wb = openpyxl.load_workbook(filepath)
    return wb


def read_1_1(wb) -> tuple[Table]:
    sh = wb["1.1"]
    data = list(get_rows(sh, 5, 73))
    accounts = get_accounts_column(data)
    accounts_data = process_accounts(accounts)
    account_hierarchy = expand_account_hierarchy(accounts_data)
    data = insert_account_codes(data, account_hierarchy)
    data = melt(
        data,
        id_cols=["account_code"],
        var_name="date",
    )
    data = value_column_to_int(data, value_column_name="value")
    data = split_datetime_column(data, datetime_column_name="date")
    return data, account_hierarchy


def read_1_2(wb) -> tuple[Table]:
    sh = wb["1.2"]
    data = list(get_rows(sh, 5, 162))
    accounts = get_accounts_column(data)
    accounts_data = process_accounts(accounts)
    account_hierarchy = expand_account_hierarchy(accounts_data)
    data = insert_account_codes(data, account_hierarchy)
    data = melt(
        data,
        id_cols=["account_code"],
        var_name="date",
    )
    data = value_column_to_int(data, value_column_name="value")
    data = split_datetime_column(data, datetime_column_name="date")
    return data, account_hierarchy


def write_csv(data, filepath):
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f, delimiter=",", dialect=csv.QUOTE_ALL)
        writer.writerows(data)
