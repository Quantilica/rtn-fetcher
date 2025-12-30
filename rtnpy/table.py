"""Table data structure and manipulation functions.

This module provides a column-oriented table structure (Tbl) and associated
transformation functions for working with tabular data.
"""

from typing import Any, Callable, Iterator

from .constants import MAX_DISPLAY_ROWS

Column = list[Any]
Matrix = list[Column]


class Tbl:
    """Column-oriented table data structure.

    Data is stored as a list of columns, where each column is a list of values.
    The first element of each column is the column name (header).

    Attributes:
        data: List of columns, each column is a list starting with the column name.
        ncols: Number of columns in the table.
        nrows: Number of rows in the table (including header).
    """

    def __init__(self, data: Matrix | None = None) -> None:
        """Initialize a table from column data.

        Args:
            data: List of columns. If None, creates an empty table.
        """
        if data:
            self.data = data
            self.ncols = len(self.data)
            self.nrows = len(self.data[0]) if self.data else 0
        else:
            self.data = []
            self.ncols = 0
            self.nrows = 0

    def get_header(self) -> list[Any]:
        """Get column names.

        Returns:
            List of column names (first element of each column).
        """
        return get_header(self.data)

    def iter_rows(self) -> Iterator[list[Any]]:
        """Iterate over rows.

        Yields:
            Each row as a list of values.
        """
        yield from iter_rows(self.data)

    def transpose(self) -> "Tbl":
        """Transpose table (swap rows and columns).

        Returns:
            New table with transposed data.
        """
        return Tbl(transpose(self.data))

    def select(self, *columns: str) -> "Tbl":
        """Select specific columns.

        Args:
            columns: Names of columns to select.

        Returns:
            New table with only the selected columns.
        """
        return Tbl(select(self.data, *columns))

    def assign(self, **columns: Column) -> "Tbl":
        """Add or update columns.

        Args:
            **columns: Column names and their data (without header).

        Returns:
            New table with assigned columns.
        """
        return Tbl(assign(self.data, **columns))

    def insert(self, data: "Tbl", index: int = 0) -> "Tbl":
        """Insert columns from another table at a specific position.

        Args:
            data: Table whose columns to insert.
            index: Position to insert columns at.

        Returns:
            New table with inserted columns.
        """
        return Tbl(insert(self.data, data.data, index))

    def melt(
        self,
        id_cols: list[str],
        var_name: str = "variable",
        value_name: str = "value",
    ) -> "Tbl":
        """Transform from wide to long format (unpivot).

        Args:
            id_cols: Columns to use as identifier variables.
            var_name: Name for the variable column.
            value_name: Name for the value column.

        Returns:
            New table in long format.
        """
        return Tbl(melt(self.data, id_cols, var_name, value_name))

    def drop_rows(self, rows: list[int]) -> "Tbl":
        """Remove specific rows by index.

        Args:
            rows: List of row indices to remove.

        Returns:
            New table without the specified rows.
        """
        return Tbl(drop_rows(self.data, rows))

    def drop_cols(self, cols: list[int]) -> "Tbl":
        """Remove specific columns by index.

        Args:
            cols: List of column indices to remove.

        Returns:
            New table without the specified columns.
        """
        return Tbl(drop_cols(self.data, cols))

    def rename(self, **names_to: str) -> "Tbl":
        """Rename columns.

        Args:
            **names_to: Mapping from old column names to new names.

        Returns:
            New table with renamed columns.
        """
        return Tbl(rename(self.data, **names_to))

    def __getitem__(self, name: str) -> Column:
        """Get column by name.

        Args:
            name: Column name.

        Returns:
            Column data including header.

        Raises:
            KeyError: If column name not found.
        """
        header = get_header(self.data)
        if name in header:
            return self.data[header.index(name)]
        raise KeyError(f"Column '{name}' not found in table")

    def __setitem__(self, name: str, value: Column) -> None:
        """Set or update a column.

        Args:
            name: Column name.
            value: Column data (without header).
        """
        header = get_header(self.data)
        if name in header:
            self.data[header.index(name)] = value
        else:
            self.data = assign(self.data, **{name: value})
            self.ncols += 1

    def __repr__(self) -> str:
        """String representation of the table.

        Returns:
            Table preview with dimensions.
        """
        lines = []
        for i, row in enumerate(iter_rows(self.data)):
            if i > MAX_DISPLAY_ROWS:
                break
            lines.append("\t".join(str(cell) for cell in row))
        lines.append(
            f"{self.__class__.__name__}: {self.nrows} rows × {self.ncols} cols"
        )
        return "\n".join(lines)


def get_header(data: Matrix) -> list[Any]:
    """Extract column names from matrix.

    Args:
        data: Column-oriented matrix.

    Returns:
        List of column names.
    """
    return [col[0] for col in data]


def iter_rows(data: Matrix) -> Iterator[list[Any]]:
    """Iterate over rows of a column-oriented matrix.

    Args:
        data: Column-oriented matrix.

    Yields:
        Each row as a list.
    """
    for row in zip(*data):
        yield list(row)


def transpose(data: Matrix) -> Matrix:
    """Transpose matrix (swap rows and columns).

    Args:
        data: Matrix to transpose.

    Returns:
        Transposed matrix.
    """
    return [[*row] for row in zip(*data)]


def melt(
    data: Matrix,
    id_cols: list[str],
    var_name: str = "variable",
    value_name: str = "value",
) -> Matrix:
    """Transform data from wide to long format.

    Args:
        data: Column-oriented matrix.
        id_cols: Columns to keep as identifiers.
        var_name: Name for the new variable column.
        value_name: Name for the new value column.

    Returns:
        Matrix in long format.
    """
    transposed = transpose(data.copy())
    columns = transposed[0]
    id_col_indices = [columns.index(id_col) for id_col in id_cols]
    header = [*id_cols, var_name, value_name]
    melted_rows = [header]

    for row in transposed[1:]:
        id_values = [row[i] for i in id_col_indices]
        for i, value in enumerate(row):
            if i in id_col_indices:
                continue
            melted_row = [*id_values, columns[i], value]
            melted_rows.append(melted_row)

    return transpose(melted_rows)


def apply(column: Column, func: Callable[[Any], Any]) -> Column:
    """Apply function to each element in a column.

    Args:
        column: Column data.
        func: Function to apply to each element.

    Returns:
        New column with transformed values.
    """
    return [func(value) for value in column]


def insert(data1: Matrix, data2: Matrix, index: int = 0) -> Matrix:
    """Insert columns from data2 into data1 at specified index.

    Args:
        data1: Primary matrix.
        data2: Matrix to insert.
        index: Position to insert at.

    Returns:
        Combined matrix.
    """
    return data1[:index] + data2 + data1[index:]


def select(data: Matrix, *columns: str) -> Matrix:
    """Select specific columns from matrix.

    Args:
        data: Source matrix.
        *columns: Column names to select.

    Returns:
        Matrix with only selected columns.

    Raises:
        ValueError: If a column name is not found.
    """
    header = get_header(data)
    indices = [header.index(column) for column in columns]
    return [data[i] for i in indices]


def where(func: Callable[[list[Any]], bool], data: Matrix) -> Matrix:
    """Filter rows based on a predicate function.

    Args:
        func: Predicate function that takes a row and returns bool.
        data: Matrix to filter.

    Returns:
        Filtered matrix.
    """
    filtered_rows = [row for row in iter_rows(transpose(data)) if func(row)]
    return transpose(filtered_rows)


def assign(data: Matrix, **columns: Column) -> Matrix:
    """Add or update columns in matrix.

    Args:
        data: Source matrix.
        **columns: Column names and their data (without header).

    Returns:
        Matrix with assigned columns.
    """
    header = get_header(data)
    new_data = data.copy()

    for column_name, column_values in columns.items():
        new_column = [column_name, *column_values]
        if column_name in header:
            index = header.index(column_name)
            new_data[index] = new_column
        else:
            new_data.append(new_column)

    return new_data


def drop_rows(data: Matrix, rows: list[int]) -> Matrix:
    """Remove rows by index.

    Args:
        data: Source matrix.
        rows: List of row indices to remove.

    Returns:
        Matrix without specified rows.
    """
    rows_set = set(rows)
    filtered_rows = [row for i, row in enumerate(iter_rows(data)) if i not in rows_set]
    return transpose(filtered_rows)


def drop_cols(data: Matrix, cols: list[int]) -> Matrix:
    """Remove columns by index.

    Args:
        data: Source matrix.
        cols: List of column indices to remove.

    Returns:
        Matrix without specified columns.
    """
    cols_set = set(cols)
    return [col for i, col in enumerate(data) if i not in cols_set]


def rename(data: Matrix, **names_to: str) -> Matrix:
    """Rename columns.

    Args:
        data: Source matrix.
        **names_to: Mapping from old names to new names.

    Returns:
        Matrix with renamed columns.
    """
    new_data = data.copy()
    for i, column in enumerate(new_data):
        original_name = column[0]
        if original_name in names_to:
            new_data[i][0] = names_to[original_name]
    return new_data
