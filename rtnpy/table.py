from typing import Any, Callable

Column = list[Any]
Table = list[Column]


class Tbl:

    data: list[list[Any]]
    ncols: int
    nrows: int

    def __init__(self, data=None) -> None:
        if data:
            self.data = data
            self.ncols = len(data)
            self.nrows = len(data[0])

    def get_header(self):
        return get_header(self.data)


def get_header(data: Table):
    return list(next(zip(*data)))


def iter_rows(data: Table):
    for row in zip(*data):
        yield list(row)


def transpose(data: Table) -> Table:
    return list(zip(*data))


def melt(data: Table,
         id_cols: list[str],
         var_name="variable",
         value_name="value") -> Table:
    data = transpose(data.copy())
    columns = data[0]
    index_id_cols = [columns.index(id_col) for id_col in id_cols]
    header = [*id_cols, var_name, value_name]
    new_data = [header]
    for row in data[1:]:
        id_values = [row[i] for i in index_id_cols]
        for i, value in enumerate(row):
            if i in index_id_cols:  # cell is in id_cols
                continue
            output_row = id_values + [columns[i], value]
            new_data.append(output_row)
    new_data = transpose(new_data)
    return new_data


def apply(data: Table, column_name: str, func: Callable) -> Table:
    header = get_header(data)
    index = header.index(column_name)
    new_data = data.copy()
    new_data[index] = [column_name] + [func(v) for v in new_data[index][1:]]
    return new_data


def insert(data1: Table, data2: Table, index: int = 0) -> Table:
    new_data = data1[:index] + data2 + data1[index:]
    return new_data


def select(data: Table, *columns: str) -> Table:
    header = get_header(data)
    indices = [header.index(column) for column in columns]
    new_data = [data[i] for i in indices]
    return new_data


def where(func: Callable, data: Table) -> Table:
    new_data = []
    for row in iter_rows(transpose(data)):
        if func(row):
            new_data.append(row)
    new_data = transpose(new_data)
    return new_data


def assign(data: Table, column: Column) -> Table:
    header = get_header(data)
    new_data = data.copy()
    column_name = column[0]
    if column_name in header:
        index = header.index(column_name)
        new_data[index] = column
    else:
        new_data.insert(len(data), column)
    return new_data
