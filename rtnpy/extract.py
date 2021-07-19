from .account import (account_code_to_list_ints, list_ints_to_account_code,
                      parse_column_name)
from .excel import Cell, Sheet, get_indent
from .table import Table


def get_rows(sh: Sheet, min_row: int = 0, max_row: int = 1_048_576) -> Table:
    rows = []
    for row in sh.iter_rows(min_row=min_row, max_row=max_row):
        if row[0].value:
            row = [cell for cell in row if cell.value is not None]
            if len(row) < 3:
                continue
            rows.append(row)
    return rows


def get_accounts_data(accounts: list[Cell]) -> list[list[str]]:
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
