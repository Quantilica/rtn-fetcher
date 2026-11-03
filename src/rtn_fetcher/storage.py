"""File location management for rtn-fetcher."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.core.storage import BaseDataRepository, build_stamped_filename


class DataRepository(BaseDataRepository):
    """Manages local storage for rtn-fetcher files."""

    def __init__(self, root: Path | str):
        super().__init__(root)

    def path_for_entry(
        self,
        entry: dict[str, Any],
        *,
        last_modified: dt.date | dt.datetime | None = None,
    ) -> Path:
        """Compute the local path for a dataset entry.

        The stamp is the remote Last-Modified date (F2: HEAD_FALLBACK_GET), so the
        name stays stable between runs. Only when the server exposes no
        Last-Modified at all does it fall back to the download date.
        """
        ano = entry.get("ano_publicacao")
        mes = entry.get("mes_publicacao")
        group = entry.get("group") or "rtn"
        orig_filename = entry.get("filename", "unknown.xlsx")
        ext = entry.get("ext")
        if not ext:
            ext = orig_filename.rsplit(".", 1)[-1] if "." in orig_filename else "xlsx"
        ext = ext.lstrip(".")

        if group == "rtn":
            dataset_id = "serie-historica"
            slug = "rtn"
        else:
            dataset_id = str(group)
            slug = Path(orig_filename).stem

        partition = None
        if ano is not None and mes is not None:
            partition = f"{int(ano)}-{int(mes):02d}"
        elif ano is not None:
            partition = f"{int(ano)}"

        # Fallback to today's date when server doesn't provide reliable metadata
        timestamp = last_modified or dt.date.today()

        filename = build_stamped_filename(
            slug,
            partition,
            ext=ext,
            timestamp=timestamp,
            precision="date",
        )
        return self.dataset_path(dataset_id, filename)
