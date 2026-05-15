#!/usr/bin/env python3
"""Generate README charts from RTN data using seaborn and matplotlib."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd

from rtnpy import read_sheet

RTN_FILE = Path("data/rtn_202604301524.xlsx")
ASSETS_DIR = Path("assets")
ASSETS_DIR.mkdir(exist_ok=True)

PALETTE = {
    "blue": "#2563EB",
    "red": "#DC2626",
    "green": "#16A34A",
    "orange": "#EA580C",
    "purple": "#7C3AED",
    "teal": "#0D9488",
    "gray": "#6B7280",
}

sns.set_theme(
    style="whitegrid",
    rc={
        "font.family": "DejaVu Sans",
        "axes.facecolor": "#F9FAFB",
        "figure.facecolor": "white",
        "grid.color": "#E5E7EB",
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
    },
)


def load_annual_pct_gdp() -> pd.DataFrame:
    data, accounts = read_sheet(RTN_FILE, "2.1-A")
    header = data.get_header()
    df = pd.DataFrame({col[0]: col[1:] for col in data.data})

    acc_df = pd.DataFrame({col[0]: col[1:] for col in accounts.data})
    df = df.merge(
        acc_df[["account_code", "account_name"]],
        left_on="account",
        right_on="account_code",
        how="left",
    )
    df["pct"] = df["value"] * 100
    return df.dropna(subset=["year", "value"])


def plot_primary_result(df: pd.DataFrame, output: Path) -> None:
    result = (
        df[df["account"] == "8"]
        .sort_values("year")
        .dropna(subset=["pct"])
    )

    fig, ax = plt.subplots(figsize=(13, 5))

    colors = [PALETTE["green"] if v >= 0 else PALETTE["red"] for v in result["pct"]]
    bars = ax.bar(
        result["year"], result["pct"],
        color=colors, width=0.72, alpha=0.88, edgecolor="white", linewidth=0.6,
    )
    ax.axhline(0, color="#374151", linewidth=1.0, alpha=0.6)

    for bar, val in zip(bars, result["pct"]):
        if bar.get_x() + bar.get_width() / 2 >= 2012:
            offset = 0.08 if val >= 0 else -0.08
            va = "bottom" if val >= 0 else "top"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val + offset,
                f"{val:.1f}%",
                ha="center", va=va, fontsize=7.5, fontweight="bold",
                color=PALETTE["green"] if val >= 0 else PALETTE["red"],
            )

    ax.set_title(
        "Resultado Primário do Governo Central (% do PIB)",
        fontsize=14, fontweight="bold", pad=14, color="#111827",
    )
    ax.set_xlabel("Ano", fontsize=11, color="#374151")
    ax.set_ylabel("% do PIB", fontsize=11, color="#374151")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    ax.tick_params(axis="x", rotation=45)

    surplus = mpatches.Patch(color=PALETTE["green"], alpha=0.88, label="Superávit")
    deficit = mpatches.Patch(color=PALETTE["red"], alpha=0.88, label="Déficit")
    ax.legend(handles=[surplus, deficit], loc="upper right", fontsize=10)

    plt.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  {output}")


def plot_revenue_expenditure(df: pd.DataFrame, output: Path) -> None:
    rev = (
        df[df["account"] == "3"][["year", "pct"]]
        .rename(columns={"pct": "Receita Líquida"})
    )
    exp = (
        df[df["account"] == "4"][["year", "pct"]]
        .rename(columns={"pct": "Despesa Total"})
    )
    merged = (
        rev.merge(exp, on="year")
        .sort_values("year")
        .dropna()
    )

    fig, ax = plt.subplots(figsize=(13, 5))

    ax.fill_between(
        merged["year"], merged["Receita Líquida"], merged["Despesa Total"],
        where=merged["Receita Líquida"] < merged["Despesa Total"],
        alpha=0.12, color=PALETTE["red"],
    )
    ax.fill_between(
        merged["year"], merged["Receita Líquida"], merged["Despesa Total"],
        where=merged["Receita Líquida"] >= merged["Despesa Total"],
        alpha=0.12, color=PALETTE["green"],
    )
    ax.plot(
        merged["year"], merged["Receita Líquida"],
        color=PALETTE["blue"], linewidth=2.5, marker="o", markersize=4.5,
        label="Receita Líquida",
    )
    ax.plot(
        merged["year"], merged["Despesa Total"],
        color=PALETTE["red"], linewidth=2.5, marker="s", markersize=4.5,
        label="Despesa Total",
    )

    ax.set_title(
        "Receita Líquida e Despesa Total do Governo Central (% do PIB)",
        fontsize=14, fontweight="bold", pad=14, color="#111827",
    )
    ax.set_xlabel("Ano", fontsize=11, color="#374151")
    ax.set_ylabel("% do PIB", fontsize=11, color="#374151")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=11)

    plt.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  {output}")


def plot_expenditure_breakdown(df: pd.DataFrame, output: Path) -> None:
    components = {
        "4.1": "Benef. Previdenciários",
        "4.2": "Pessoal e Encargos",
        "4.3": "Outras Obrigatórias",
        "4.4": "Prog. Financeira",
    }
    filtered = df[df["account"].isin(components.keys())].copy()
    filtered["label"] = filtered["account"].map(components)
    pivot = (
        filtered.pivot_table(index="year", columns="label", values="pct", aggfunc="sum")
        .dropna(how="all")
        .fillna(0)
    )
    pivot = pivot[pivot.index >= 2010]

    fig, ax = plt.subplots(figsize=(13, 5))

    colors = [PALETTE["blue"], PALETTE["orange"], PALETTE["purple"], PALETTE["teal"]]
    cols_ordered = [c for c in components.values() if c in pivot.columns]
    pivot[cols_ordered].plot(
        kind="bar", stacked=True, ax=ax,
        color=colors[: len(cols_ordered)], width=0.72,
        edgecolor="white", linewidth=0.5,
    )

    ax.set_title(
        "Composição das Despesas do Governo Central (% do PIB)",
        fontsize=14, fontweight="bold", pad=14, color="#111827",
    )
    ax.set_xlabel("Ano", fontsize=11, color="#374151")
    ax.set_ylabel("% do PIB", fontsize=11, color="#374151")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=9, loc="upper left", framealpha=0.9)

    plt.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  {output}")


def plot_workflow_overview(output: Path) -> None:
    """Diagram showing the rtnpy data pipeline."""
    fig, ax = plt.subplots(figsize=(12, 3.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis("off")

    steps = [
        (1.0, 2.0, "Tesouro\nNacional\n(API)", PALETTE["blue"], "white"),
        (3.5, 2.0, "Download\n& Cache\n(fetcher)", PALETTE["teal"], "white"),
        (6.0, 2.0, "Leitura\nExcel\n(reader)", PALETTE["purple"], "white"),
        (8.5, 2.0, "Tbl\n(estrutura\ncolunar)", PALETTE["orange"], "white"),
        (11.0, 2.0, "pandas /\npolars /\nCSV / DB", PALETTE["green"], "white"),
    ]

    box_w, box_h = 1.6, 1.2
    for x, y, label, color, fc in steps:
        rect = mpatches.FancyBboxPatch(
            (x - box_w / 2, y - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.08", linewidth=1.5,
            edgecolor=color, facecolor=color, alpha=0.85,
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha="center", va="center",
                fontsize=9, fontweight="bold", color=fc, linespacing=1.4)

    arrow_props = dict(arrowstyle="->", color="#374151", lw=1.8)
    for i in range(len(steps) - 1):
        x0 = steps[i][0] + box_w / 2
        x1 = steps[i + 1][0] - box_w / 2
        y = steps[i][1]
        ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=arrow_props)

    ax.set_title(
        "Pipeline de Dados do rtnpy",
        fontsize=13, fontweight="bold", pad=10, color="#111827",
        y=0.97,
    )
    plt.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  {output}")


if __name__ == "__main__":
    print("Carregando dados RTN...")
    df = load_annual_pct_gdp()
    years = sorted(df["year"].unique())
    print(f"  {len(df)} linhas, anos {years[0]}–{years[-1]}")

    print("\nGerando gráficos:")
    plot_primary_result(df, ASSETS_DIR / "primary_result.png")
    plot_revenue_expenditure(df, ASSETS_DIR / "revenue_expenditure.png")
    plot_expenditure_breakdown(df, ASSETS_DIR / "expenditure_breakdown.png")
    plot_workflow_overview(ASSETS_DIR / "pipeline.png")

    print("\nPronto! Gráficos salvos em assets/")
