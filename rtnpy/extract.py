import re

from bs4 import BeautifulSoup

from .account import parse_column_name
from .excel import Cell, Sheet, get_indent
from .table import Matrix, Tbl


def extract_metadata_yearsmonths(soup: BeautifulSoup) -> list[tuple[str]]:
    yearsmonths = [
        (op_year.text, op_month.text)
        for op_year in soup.select("select#filtro-ano option")
        for op_month in soup.select("select#filtro-mes option")
        if op_year.text in op_month["data-nr-ano"].split(":")
    ]
    return yearsmonths


def extract_metadata(soup: BeautifulSoup) -> list[dict]:
    cards_info = []
    cards_rtn = soup.select("div.card-rtn")
    for card in cards_rtn:
        id_publicacao = card["data-id-publicacao"]
        ano_publicacao = card["data-nr-ano"]
        mes_publicacao = card["data-id-periodicidade-periodo"]
        h3_text = card.select_one("h3").find(string=True, recursive=False).strip(" \n")
        p_text = re.sub("[ \n]+", " ", card.select_one("p").text.strip()).replace(
            " ", " "
        )
        links = {
            re.sub("[ \n]+", " ", a.text.strip(" \n")): a["href"]
            for a in card.select("a")
        }
        card_info = {
            "id_publicacao": id_publicacao,
            "ano_publicacao": ano_publicacao,
            "mes_publicacao": mes_publicacao,
            "titulo": h3_text,
            "resumo": p_text,
            "links": links,
        }
        cards_info.append(card_info)
    return cards_info


def get_rows(sh: Sheet, min_row: int = 0, max_row: int = 1_048_576) -> Matrix:
    rows = []
    for row in sh.iter_rows(min_row=min_row, max_row=max_row):
        if row[0].value:
            row = [cell for cell in row if cell.value is not None]
            if len(row) < 3:
                continue
            rows.append(row)
    return rows


def get_accounts_data(accounts: list[Cell]) -> Tbl:
    accounts_data = [["account_code"], ["account_name"], ["account_level"]]
    last_account = (0,)
    indent_stack = (0,)
    for cell in accounts:
        indent = get_indent(cell)
        if indent > indent_stack[-1]:
            indent_stack = indent_stack + (indent,)
            last_account = last_account + (0,)
        elif "d/q" in cell.value:
            indent_stack = indent_stack + (indent,)
            last_account = last_account + (0,)
        elif indent < indent_stack[-1]:
            while indent < indent_stack[-1]:
                indent_stack = indent_stack[:-1]
                last_account = last_account[:-1]
        last_account = last_account[:-1] + (last_account[-1] + 1,)
        account_code, account_name = parse_column_name(cell.value)
        if account_code == "":
            account_code = "=>".join(str(n) for n in last_account)
        account_level = len(last_account)
        accounts_data[0].append(account_code)
        accounts_data[1].append(account_name)
        accounts_data[2].append(account_level)
    accounts_data = Tbl(accounts_data)
    return accounts_data
