"""File location management for rtn-fetcher."""

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.core.storage import BaseDataRepository


class DataRepository(BaseDataRepository):
    """Manages local storage for rtn-fetcher files."""

    def __init__(self, root: Path | str):
        super().__init__(root)

    def path_for_entry(
        self,
        entry: dict[str, Any],
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Compute the local path for a dataset entry.

        Args:
            entry: Dataset entry dictionary containing metadata.
            last_modified: Optional last modified date.

        Returns:
            Computed local file path.
        """
        ano = entry.get("ano_publicacao")
        mes = entry.get("mes_publicacao")
        filename = entry.get("filename", "unknown.xlsx")

        if ano is not None and mes is not None:
            partition_dir = f"{ano}-{int(mes):0>2}"
            return self.storage.path_for(f"{partition_dir}/{filename}")

        return self.storage.path_for(filename)
