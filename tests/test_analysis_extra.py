"""Tests for rtn_fetcher analysis-extra import guard."""

import importlib
import subprocess
import sys
import textwrap

import pytest

from rtn_fetcher.dataframe import to_polars
from rtn_fetcher.table import Tbl

MODULES = [
    "rtn_fetcher.schema",
    "rtn_fetcher.writer",
]

ANALYTICS = (
    "quantilica.analytics",
    "quantilica.analytics.schema",
    "quantilica.analytics.writer",
)

# Cenários de ausência do extra 'analysis'. Sem polars, quantilica.analytics
# também não importa (depende dele); o bloqueio explícito evita que os
# submódulos já carregados em sys.modules mascarem a falha.
EXTRA_DEPS = [
    ("polars", *ANALYTICS),
    ANALYTICS,
]


@pytest.mark.parametrize("bloqueados", EXTRA_DEPS, ids=["polars", "analytics"])
def test_analysis_extra_mensagem_acionavel(bloqueados):
    salvos = {name: sys.modules.get(name) for name in (*bloqueados, *MODULES)}
    try:
        for module_name in MODULES:
            for dep in bloqueados:
                sys.modules[dep] = None
            sys.modules.pop(module_name, None)
            try:
                with pytest.raises(
                    ImportError,
                    match=f"{module_name} requer o extra 'analysis'",
                ):
                    importlib.import_module(module_name)
            finally:
                sys.modules.pop(module_name, None)
    finally:
        for name, mod in salvos.items():
            if mod is not None:
                sys.modules[name] = mod
            else:
                sys.modules.pop(name, None)
        for module_name in MODULES:
            importlib.import_module(module_name)


def test_to_polars_sem_polars_mensagem_acionavel():
    tbl = Tbl([["a", 1, 2]])
    salvo_polars = sys.modules.get("polars")
    try:
        sys.modules["polars"] = None
        with pytest.raises(ImportError, match="requer o extra 'analysis'"):
            tbl.to_polars()
        with pytest.raises(ImportError, match="requer o extra 'analysis'"):
            to_polars(tbl)
    finally:
        if salvo_polars is not None:
            sys.modules["polars"] = salvo_polars
        else:
            sys.modules.pop("polars", None)


def test_api_basica_importa_sem_extra_analysis():
    """reader/fetcher/constants (usados pelo quantilica-workers) não exigem o extra.

    Roda em subprocesso para importar o pacote do zero com polars e
    quantilica.analytics bloqueados, sem afetar os módulos já carregados.
    """
    codigo = textwrap.dedent(
        """
        import sys

        for dep in ("polars", "quantilica.analytics"):
            sys.modules[dep] = None

        import rtn_fetcher
        from rtn_fetcher.constants import SHEET_CONFIGS
        from rtn_fetcher.fetcher import download_latest_file
        from rtn_fetcher.reader import read_all_sheets

        assert SHEET_CONFIGS
        assert callable(download_latest_file)
        assert callable(read_all_sheets)
        assert rtn_fetcher._HAS_ANALYSIS is False
        assert rtn_fetcher.write_table_to_parquet is None
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", codigo], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
