import re

from .table import Tbl, transpose


def get_accounts_column(data: Tbl):
    return [col[0] for col in data.data[1:]]


def clean_name(name):
    name = re.sub(r" +", " ", name)
    name = re.sub(r" \d+/$", "", name)
    name = name.strip(" -")
    return name


def parse_column_name(name):

    # Initialize variables
    account_code = account_name = ""

    match = re.match(r"^\d+((\.\d+)+|\.)", name)
    if match:
        account_code = match.group().strip()
    account_name = clean_name(name.replace(account_code, ""))
    account_code = account_code.replace(".", "=>")

    return account_code, account_name


def expand_account_hierarchy(accounts_data: Tbl) -> Tbl:
    account_code_col = accounts_data["account_code"][1:]
    maxlevel = max(map(lambda t: len(t.split("=>")), account_code_col))
    part_levels = [f"P_{i}" for i in range(1, maxlevel+1)]
    account_hierarchy = [["account_code", "account_name", "account_level"] + part_levels]
    last_row = (maxlevel+1) * [None]
    it = accounts_data.iter_rows()
    next(it)
    for account_code, account_name, account_level in it:
        list_account_code = account_code.split("=>")
        level = len(list_account_code)
        full_account_name = ".".join(list_account_code) + " " + account_name
        row = (
            [account_code, full_account_name, account_level]
            + last_row[:level-1]
            + [account_name]
            + ((maxlevel-level) * [None])  # Fill with None
        )
        account_hierarchy.append(row)
        last_row = row[3:]
    account_hierarchy = Tbl(transpose(account_hierarchy))
    return account_hierarchy
