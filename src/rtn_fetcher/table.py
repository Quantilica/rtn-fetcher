"""Table data structure and manipulation functions.

This module provides a column-oriented table structure (Tbl) and associated
transformation functions for working with tabular data.
"""

from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING, Any

from .constants import MAX_DISPLAY_ROWS

if TYPE_CHECKING:
    import polars as pl

Column = list[Any]
Matrix = list[Column]


class Tbl:
    """Column-oriented table data structure.

    Data is stored as a list of columns, where each column is a list of values.
    The first element of each column is the column name (header).

    Attributes:
        data: List of columns, each column starts with the column name.
        ncols: Number of columns in the table.
        nrows: Number of rows (including header).
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

    def assign(self, **columns: Column) -> "Tbl":
        """Add or update columns.

        Args:
            **columns: Column names and their data (without header).

        Returns:
            New table with assigned columns.
        """
        return Tbl(assign(self.data, **columns))

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

    def to_polars(self) -> "pl.DataFrame":
        """Convert to polars DataFrame.

        polars is available via the quantilica-io dependency — no extra required.

        Returns:
            polars DataFrame with same data and column names.
        """
        import polars as pl

        header = self.get_header()
        columns = {
            col_name: col_data[1:]
            for col_name, col_data in zip(header, self.data, strict=False)
        }
        return pl.DataFrame(columns)


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
    for row in zip(*data, strict=False):
        yield list(row)


def transpose(data: Matrix) -> Matrix:
    """Transpose matrix (swap rows and columns).

    Args:
        data: Matrix to transpose.

    Returns:
        Transposed matrix.
    """
    return [[*row] for row in zip(*data, strict=False)]


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
