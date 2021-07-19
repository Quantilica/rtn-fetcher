import re

from .table import Table


def get_accounts_column(data: Table):
    return [row[0] for row in data[1:]]


def account_code_to_list_ints(account_code: str) -> list[int]:
    return [int(code) for code in account_code.split("=>") if code]


def list_ints_to_account_code(account_code: list[int]) -> str:
    return "=>".join([str(code) for code in account_code])


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
