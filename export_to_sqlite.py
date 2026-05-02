"""Script to download the latest RTN data and export it to a SQLite database."""

import sqlite3
from datetime import date
from pathlib import Path

from rtnpy import Tbl, download_latest_file, read_all_sheets


def get_column_names(table: Tbl) -> list[str]:
    return [col[0] for col in table.data]


def make_period_date(year, month, quarter) -> str | None:
    if year is None:
        return None
    if quarter is not None:
        return date(int(year), (int(quarter) - 1) * 3 + 1, 1).isoformat()
    if month is not None:
        return date(int(year), int(month), 1).isoformat()
    return date(int(year), 1, 1).isoformat()


def save_to_sqlite(
    results: dict[str, tuple[Tbl, Tbl, str | None]],
    db_path: Path,
) -> None:
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE rtn_data (
            key   TEXT,
            date  TEXT,
            value REAL
        )
    """)

    hierarchy_cols = [f"P_{i}" for i in range(1, 11)]
    cols_sql = ", ".join(f"{col} TEXT" for col in hierarchy_cols)
    cursor.execute(f"""
        CREATE TABLE rtn_accounts (
            key           TEXT,
            sheet         TEXT,
            sheet_title   TEXT,
            account_code  TEXT,
            account_name  TEXT,
            account_level INTEGER,
            {cols_sql}
        )
    """)

    for sheet_name, (data_tbl, accounts_tbl, sheet_title) in results.items():
        print(f"Processing sheet {sheet_name}...")

        data_header = get_column_names(data_tbl)
        for row in data_tbl.iter_rows():
            if row == data_header:
                continue
            row_dict = dict(zip(data_header, row))
            account = row_dict.get("account")
            period_date = make_period_date(
                row_dict.get("year"),
                row_dict.get("month"),
                row_dict.get("quarter"),
            )
            cursor.execute(
                "INSERT INTO rtn_data (key, date, value) VALUES (?, ?, ?)",
                (f"{sheet_name}|{account}", period_date, row_dict.get("value")),
            )

        acc_header = get_column_names(accounts_tbl)
        for row in accounts_tbl.iter_rows():
            if row == acc_header:
                continue
            row_dict = dict(zip(acc_header, row))
            account_code = row_dict.get("account_code")
            p_values = [row_dict.get(f"P_{i}") for i in range(1, 11)]
            cursor.execute(
                f"INSERT INTO rtn_accounts (key, sheet, sheet_title, account_code, account_name, account_level, {', '.join(hierarchy_cols)}) VALUES (?, ?, ?, ?, ?, ?, {', '.join(['?'] * 10)})",
                [
                    f"{sheet_name}|{account_code}",
                    sheet_name,
                    sheet_title,
                    account_code,
                    row_dict.get("account_name"),
                    row_dict.get("account_level"),
                    *p_values,
                ],
            )

    conn.commit()
    conn.close()
    print(f"Database saved to {db_path}")


def main() -> None:
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    print("Checking for latest RTN file...")
    filepath = download_latest_file(data_dir)

    if not filepath:
        xlsx_files = sorted(data_dir.glob("rtn_*.xlsx"), reverse=True)
        if not xlsx_files:
            print("No RTN files found and could not download latest.")
            return
        filepath = xlsx_files[0]
        print(f"Using existing file: {filepath}")
    else:
        print(f"Downloaded: {filepath}")

    print(f"Reading all sheets from {filepath}...")
    results = read_all_sheets(filepath)

    db_path = Path("rtn_data.db")
    save_to_sqlite(results, db_path)


if __name__ == "__main__":
    main()
