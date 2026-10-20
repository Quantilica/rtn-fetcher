"""Regressão: códigos de conta com mais de um dígito sem ponto.

Nas abas 1.x/2.x o código vem embutido no rótulo ("10. RESULTADO NOMINAL DO
GOVERNO CENTRAL (8 + 9)"); "10" é uma conta de nível 1, irmã de "9 JUROS
NOMINAIS". Antes do fix o parser a tratava como código compacto ("1.0", nível
2, filha de "JUROS NOMINAIS"). Os códigos compactos de verdade ficam na coluna
de código separada das abas 4.1/4.2 ("111" -> "1.1.1", "2M" -> "2.M").
"""

from types import SimpleNamespace

import pytest

from rtn_fetcher.account import normalize_account_code, parse_account_name
from rtn_fetcher.extract import build_account_data, build_account_data_from_columns


def _cell(value, indent=0.0):
    return SimpleNamespace(value=value, alignment=SimpleNamespace(indent=indent))


@pytest.mark.parametrize(
    ("label", "code", "name"),
    [
        ("10. RESULTADO NOMINAL DO GOVERNO CENTRAL (8 + 9) 8/", "10", None),
        ("9. JUROS NOMINAIS", "9", "JUROS NOMINAIS"),
        ("1.0 Conta legítima com ponto", "1.0", "Conta legítima com ponto"),
        ("1.1 Receita Administrada", "1.1", "Receita Administrada"),
        ("1.1.02    IPI", "1.1.02", "IPI"),
        ("11. Conta hipotética de nível 1", "11", "Conta hipotética de nível 1"),
    ],
)
def test_parse_account_name_codigo_no_rotulo(label, code, name):
    parsed_code, parsed_name = parse_account_name(label)
    assert parsed_code == code
    if name is not None:
        assert parsed_name == name


def test_resultado_nominal_e_conta_de_nivel_1():
    code, name = parse_account_name(
        "10. RESULTADO NOMINAL DO GOVERNO CENTRAL (8 + 9) 8/"
    )
    assert code == "10"
    assert name.startswith("RESULTADO NOMINAL")


def test_codigos_compactos_da_coluna_de_codigo_continuam_expandidos():
    assert normalize_account_code(111) == "1.1.1"
    assert normalize_account_code(11.0) == "1.1"
    assert normalize_account_code("14x") == "1.4.x"
    assert normalize_account_code("2M") == "2.M"
    assert normalize_account_code("31.1") == "31.1"
    assert normalize_account_code("10", compact=False) == "10"


def test_build_account_data_resultado_nominal_irma_de_juros():
    """Árvore de ponta a ponta (abas 1.x): "10" no nível 1, como "9"."""
    cells = [
        _cell("8. RESULTADO PRIMÁRIO"),
        _cell("9. JUROS NOMINAIS"),
        _cell("10. RESULTADO NOMINAL DO GOVERNO CENTRAL (8 + 9) 8/"),
    ]
    tbl = build_account_data(cells)
    codes = tbl["account_code"][1:]
    levels = tbl["account_level"][1:]
    assert codes == ["8", "9", "10"]
    assert levels == [1, 1, 1]


def test_build_account_data_from_columns_mantem_codigo_compacto():
    """Abas 4.x: coluna de código numérica continua sendo compacta."""
    codes = [_cell(1), _cell(11), _cell(111), _cell("14x")]
    names = [_cell("Receita"), _cell("Impostos"), _cell("Renda"), _cell("Demais")]
    tbl = build_account_data_from_columns(codes, names)
    assert tbl["account_code"][1:] == ["1", "1.1", "1.1.1", "1.4.x"]
    assert tbl["account_level"][1:] == [1, 2, 3, 3]
