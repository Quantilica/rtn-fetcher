
import csv
import datetime
import pathlib
import re
from typing import Union

import openpyxl

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


def get_rows(sh, skip=0, nrows=1_048_576):
    rows = []
    for row in sh.iter_rows(min_row=1 + skip, max_row=nrows):
        if row[0].value:
            row = [cell for cell in row if cell.value is not None]
            if len(row) < 3:
                continue
            if isinstance(row[0].value, str) and row[0].value.startswith("Memorando:"):
                break
            rows.append(row)
    return rows


def get_accounts_column(rows):
    return [row[0] for row in rows[1:]]


def get_indent(cell):
    return cell.alignment.indent


def transpose(data):
    return list(zip(*data))


def clean_name(name):
    name = re.sub(r" +", " ", name)
    name = re.sub(r" \d+/$", "", name)
    name = name.strip(" -")
    return name


def melt(data, id_cols: list[str], var_name="variable", value_name="value", get_value=True):
    columns: list = data[0]
    index_id_cols = [columns.index(id_col) for id_col in id_cols]
    header = [*id_cols, var_name, value_name]
    yield header
    for row in data[1:]:
        id_values = [row[i] for i in index_id_cols]
        for i, cell in enumerate(row):
            if i in index_id_cols:  # cell is in id_cols
                continue
            if get_value:
                output_row = id_values + [columns[i].value, cell.value]
            else:
                output_row = id_values + [columns[i], cell]
            yield output_row


def parse_column_name(name):

    # Initialize variables
    account_code = account_name = ""

    match = re.match(r"^\d+((\.\d+)+|\.)", name)
    if match:
        account_code = match.group().strip()
    account_name = clean_name(name.replace(account_code, ""))

    return account_code, account_name


def account_code_to_list_ints(account_code):
    return [int(code) for code in account_code.split(".") if code]


def list_ints_to_account_code(account_code):
    return ".".join([str(code) for code in account_code])


def process_accounts(accounts):
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
        yield (list_ints_to_account_code(account_code), account_name)


def insert_account_data(data):
    new_data = [["account_name", "account_code", *data[0][2:]]]
    accounts = get_accounts_column(data)
    accounts_data = process_accounts(accounts)
    for row, (account_code, account_name) in zip(data[1:], accounts_data):
        new_data.append([account_name, account_code, *row[2:]])
    return new_data


def multiply_column(data, column_name, by_value: Union[int, float] = 1_000_000):
    new_data = [data[0]]
    index = data[0].index(column_name)
    for row in data[1:]:
        row[index] = int(row[index] * by_value)
        new_data.append(row)
    return new_data


def split_datetime_column(data, datetime_column_name):
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


def write_tsv(data, filepath):
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        writer = csv.writer(f, delimiter="\t", dialect=csv.QUOTE_ALL)
        writer.writerows(data)
