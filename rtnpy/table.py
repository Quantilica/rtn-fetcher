
from typing import Any, Callable

Table = list[list[Any]]


class Tbl:

    data: list[list[Any]]

    def __init__(self, data=None) -> None:
        if data:
            self.data = data

    def transpose(self):
        pass

    def melt(self):
        pass

    def apply(self):
        pass

    def insert(self):
        pass

    def select(self):
        pass

    def where(self):
        pass


def transpose(data: Table) -> Table:
    return list(zip(*data))


def melt(data: Table,
         id_cols: list[str],
         var_name="variable",
         value_name="value") -> Table:
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
    return new_data


def apply(data: Table, column_name: str, func: Callable) -> Table:
    new_data = [data[0]]
    index = data[0].index(column_name)
    for row in data[1:]:
        row[index] = func(row[index])
        new_data.append(row)
    return new_data


def insert(data1: Table, data2: Table, index: int = 0) -> Table:
    new_data = [data1[:index] + data2 + data1[index:]]
    for row1, row2 in zip(data1[1:], data2[1:]):
        new_data.append(row1[:index] + row2 + row1[index:])
    return new_data


def select(data: Table, *columns: str) -> Table:
    header = data[0]
    indices = [header.index(column) for column in columns]
    new_data = [header[i] for i in indices]
    for row in data[1:]:
        new_data.append([row[i] for i in indices])
    return new_data


def where(func: Callable, data: Table) -> Table:
    new_data = [data[0]]
    for row in data[1:]:
        if func(row):
            new_data.append(row)
    return new_data


def assign(data: Table, index: int, values: list[Any]) -> Table:
    new_data = []
    for row, new_value in zip(data, values):
        row[index] = new_value
        new_data.append(row)
    return new_data
