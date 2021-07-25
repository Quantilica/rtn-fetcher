
from itertools import islice
from typing import Any, Callable

Column = list[Any]
Matrix = list[Column]


class Tbl:

    data: Matrix
    ncols: int = 0
    nrows: int = 0

    def __init__(self, data=None) -> None:
        if data:
            self.data = data
            self.ncols = len(self.data)
            self.nrows = len(self.data[0])

    def get_header(self) -> list[Any]:
        return get_header(self.data)

    def iter_rows(self) -> list[Any]:
        yield from iter_rows(self.data)

    def transpose(self) -> "Tbl":
        return Tbl(transpose(self.data))

    def select(self, *columns: str) -> "Tbl":
        return Tbl(select(self.data, *columns))

    def assign(self, **columns: Column) -> "Tbl":
        return Tbl(assign(self.data, **columns))

    def insert(self, data: "Tbl", index: int = 0) -> "Tbl":
        return Tbl(insert(self.data, data.data, index))

    def melt(self, id_cols: list[str], var_name: str = "variable",
             value_name: str= "value") -> "Tbl":
        return Tbl(melt(self.data, id_cols, var_name, value_name))

    def drop_rows(self, rows: list[int]) -> "Tbl":
        return Tbl(drop_rows(self.data, rows))

    def drop_cols(self, cols: list[int]) -> "Tbl":
        return Tbl(drop_cols(self.data, cols))

    def rename(self, **names_to: str) -> "Tbl":
        return Tbl(rename(self.data, **names_to))

    def __getitem__(self, name: str) -> Column:
        header = get_header(self.data)
        if name in header:
            return self.data[header.index(name)]
        raise KeyError("Key %s not in data" % name)

    def __setitem__(self, name: str, value: Column) -> None:
        header = get_header(self.data)
        if name in header:
            self.data[header.index(name)] = value
        self.data = assign(self.data, **{name: value})
        self.ncols += 1

    def __repr__(self) -> str:
        s = ""
        for i, row in enumerate(iter_rows(self.data)):
            s += "\t".join((str(c) for c in row)) + "\n"
            if i > 9:
                break
        s += f"{self.__class__.__name__}: {self.nrows} X {self.ncols}"
        return s


def get_header(data: Matrix) -> list:
    return [col[0] for col in data]


def iter_rows(data: Matrix) -> list:
    for row in zip(*data):
        yield list(row)


def transpose(data: Matrix) -> Matrix:
    return [[*row] for row in zip(*data)]


def melt(data: Matrix,
         id_cols: list[str],
         var_name: str= "variable",
         value_name: str= "value") -> Matrix:
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


def apply(column: Column, func: Callable) -> Column:
    new_data = [func(v) for v in column]
    return new_data


def insert(data1: Matrix, data2: Matrix, index: int = 0) -> Matrix:
    new_data = data1[:index] + data2 + data1[index:]
    return new_data


def select(data: Matrix, *columns: str) -> Matrix:
    header = get_header(data)
    indices = [header.index(column) for column in columns]
    new_data = [data[i] for i in indices]
    return new_data


def where(func: Callable, data: Matrix) -> Matrix:
    new_data = []
    for row in iter_rows(transpose(data)):
        if func(row):
            new_data.append(row)
    new_data = transpose(new_data)
    return new_data


def assign(data: Matrix, **columns: Column) -> Matrix:
    header = get_header(data)
    new_data = data.copy()
    for column_name, column in columns.items():
        new_column = [column_name] + column
        if column_name in header:
            index = header.index(column_name)
            new_data[index] = new_column
        else:
            new_data.append(new_column)
    return new_data


def drop_rows(data: Matrix, rows: list[int]) -> Matrix:
    new_data = []
    for i, row in enumerate(iter_rows(data)):
        if i in rows:
            continue
        new_data.append(row)
    new_data = transpose(new_data)
    return new_data


def drop_cols(data: Matrix, cols: list[int]) -> Matrix:
    new_data = []
    for i, col in enumerate(data):
        if i in cols:
            continue
        new_data.append(col)
    return new_data


def rename(data: Matrix, **names_to: str) -> Matrix:
    new_data = data.copy()
    for i in range(len(new_data)):
        original = new_data[i][0]
        if original in names_to:
            new_data[i][0] = names_to[original]
    return new_data
