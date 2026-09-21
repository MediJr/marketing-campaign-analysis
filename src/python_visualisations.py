"""
ETAPE 4 — Visualisations Matplotlib (sans Seaborn, sans Plotly).

Chargement identique au workflow Python (SELECT lecture seule + preparation).
16 figures independantes, enregistrees en PNG. Aucune ecriture PostgreSQL.
"""

from __future__ import annotations

import getpass
import sys
from pathlib import Path
from urllib.parse import quote_plus

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

HOST = "127.0.0.1"
PORT = 5432
USER = "data_project"
DATABASE = "marketing_analysis"
EXPECTED_N = 200005
DPI = 150
ORIGINAL_COLS = [
    "campaign_id",
    "company",
    "campaign_type",
    "target_audience",
    "duration_days",
    "channel_used",
    "conversion_rate",
    "acquisition_cost",
    "roi",
    "location",
    "campaign_date",
    "clicks",
    "impressions",
    "engagement_score",
    "customer_segment",
]
CORR_COLS = [
    "roi",
    "acquisition_cost",
    "conversion_rate",
    "clicks",
    "impressions",
    "engagement_score",
    "duration_days",
    "ctr",
]
MONTH_LABELS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
SQL = """
SELECT *
FROM public.marketing_campaigns
ORDER BY campaign_id
"""
# Dossier des PNG : racine du dépôt / visualisations (indépendant de src/)
OUT_DIR = Path(__file__).resolve().parent.parent / "visualisations"
FILES = [
    "01_volume_company.png",
    "02_volume_campaign_type.png",
    "03_volume_channel.png",
    "04_volume_mensuel.png",
    "05_roi_mensuel.png",
    "06_distribution_roi.png",
    "07_distribution_ctr.png",
    "08_distribution_acquisition_cost.png",
    "09_distribution_conversion_rate.png",
    "10_heatmap_correlations.png",
    "11_roi_classes.png",
    "12_roi_classes_ctr.png",
    "13_heatmap_audience_segment.png",
    "14_heatmap_company_channel.png",
    "15_roi_duration.png",
    "16_roi_engagement.png",
]


def load_and_prepare() -> pd.DataFrame:
    """Extraction PostgreSQL lecture seule, puis preparation Pandas."""
    password = getpass.getpass("Mot de passe data_project: ")
    url = (
        f"postgresql+psycopg2://{USER}:{quote_plus(password)}"
        f"@{HOST}:{PORT}/{DATABASE}"
    )
    engine = create_engine(url)
    try:
        df = pd.read_sql(text(SQL), engine)
    finally:
        engine.dispose()

    df["campaign_date"] = pd.to_datetime(df["campaign_date"], errors="coerce")
    df["year"] = df["campaign_date"].dt.year.astype("int64")
    df["month"] = df["campaign_date"].dt.month.astype("int64")
    df["month_name"] = df["campaign_date"].dt.month_name()
    df["quarter"] = "Q" + df["campaign_date"].dt.quarter.astype("int64").astype(str)
    impressions = pd.to_numeric(df["impressions"], errors="coerce")
    clicks = pd.to_numeric(df["clicks"], errors="coerce")
    df["ctr"] = np.where(impressions == 0, np.nan, clicks / impressions)
    df["ctr_percent"] = df["ctr"] * 100
    return df


def verify_frame(df: pd.DataFrame) -> list[str]:
    """Controles pre-graphiques. Ne modifie pas df."""
    errors: list[str] = []
    if len(df) != EXPECTED_N:
        errors.append(f"n_lignes={len(df)}")
    if int(df.isna().sum().sum()) != 0:
        errors.append("valeurs manquantes")
    if not bool(df["campaign_id"].is_unique):
        errors.append("campaign_id non unique")
    if df["campaign_date"].min() < pd.Timestamp("2021-01-01"):
        errors.append("date min invalide")
    if df["campaign_date"].max() > pd.Timestamp("2021-12-31"):
        errors.append("date max invalide")
    ctr_ok = np.allclose(
        df["ctr"],
        np.where(df["impressions"] == 0, np.nan, df["clicks"] / df["impressions"]),
        equal_nan=True,
    )
    if not ctr_ok:
        errors.append("ctr incoherent")
    return errors


def save_fig(fig: plt.Figure, name: str) -> Path:
    path = OUT_DIR / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return path


def add_bar_labels(ax, values, percents=None, fmt_n="{:,.0f}") -> None:
    for i, val in enumerate(values):
        if percents is None:
            txt = fmt_n.format(val)
        else:
            txt = f"{fmt_n.format(val)}\n({percents[i]:.1f} %)"
        ax.text(i, val, txt, ha="center", va="bottom", fontsize=8)


def plot_volume_bars(df: pd.DataFrame, col: str, title: str, xlabel: str, outfile: str) -> None:
    """Barres de volume par categorie, avec effectifs et pourcentages."""
    counts = df[col].value_counts().sort_index()
    percents = counts / EXPECTED_N * 100
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(range(len(counts)), counts.values)
    ax.set_xticks(range(len(counts)), counts.index.astype(str), rotation=20, ha="right")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Nombre de campagnes")
    ax.set_ylim(0, counts.max() * 1.18)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    add_bar_labels(ax, counts.values, percents.values)
    fig.tight_layout()
    save_fig(fig, outfile)


def plot_01(df: pd.DataFrame) -> None:
    plot_volume_bars(
        df,
        "company",
        "Repartition des campagnes par entreprise\n(volumes, pas un classement de performance)",
        "Entreprise",
        FILES[0],
    )


def plot_02(df: pd.DataFrame) -> None:
    plot_volume_bars(
        df,
        "campaign_type",
        "Repartition des campagnes par type",
        "Type de campagne",
        FILES[1],
    )


def plot_03(df: pd.DataFrame) -> None:
    plot_volume_bars(
        df,
        "channel_used",
        "Repartition des campagnes par canal",
        "Canal",
        FILES[2],
    )


def plot_04(df: pd.DataFrame) -> None:
    """Volume mensuel + campagnes par jour (fevrier n'est pas une baisse d'activite)."""
    g = (
        df.groupby("month")
        .agg(
            n=("campaign_id", "count"),
            n_jours=("campaign_date", lambda s: int(s.dt.days_in_month.iloc[0])),
        )
        .reindex(range(1, 13))
    )
    g["per_day"] = g["n"] / g["n_jours"]
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 7))
    ax1.plot(g.index, g["n"], marker="o")
    ax1.set_title("Nombre de campagnes par mois (2021)")
    ax1.set_ylabel("Nombre de campagnes")
    ax1.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax1.set_axisbelow(True)

    ax2.plot(g.index, g["per_day"], marker="o")
    ax2.axhline(g["per_day"].mean(), linestyle="--", linewidth=1, label="moyenne journaliere")
    ax2.set_title("Campagnes par jour civil (n / nombre de jours du mois)")
    ax2.set_xlabel("Mois")
    ax2.set_ylabel("Campagnes / jour")
    ax2.set_xticks(range(1, 13), MONTH_LABELS)
    ax2.set_ylim(540, 556)
    ax2.legend(frameon=False)
    ax2.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax2.set_axisbelow(True)
    fig.suptitle(
        "Le volume de fevrier suit la longueur du mois (28 jours), "
        "pas une baisse d'activite",
        y=1.02,
        fontsize=10,
    )
    fig.tight_layout()
    save_fig(fig, FILES[3])


def plot_05(df: pd.DataFrame) -> None:
    monthly = df.groupby("month")["roi"].mean().reindex(range(1, 13))
    global_mean = float(df["roi"].mean())
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly.index, monthly.values, marker="o", label="ROI moyen mensuel")
    ax.axhline(global_mean, linestyle="--", linewidth=1, label=f"ROI moyen global ({global_mean:.2f})")
    ax.set_xticks(range(1, 13), MONTH_LABELS)
    ax.set_title("ROI moyen par mois (2021)\nEcarts faibles : ne pas lire comme une tendance")
    ax.set_xlabel("Mois")
    ax.set_ylabel("ROI moyen")
    ax.set_ylim(4.90, 5.10)
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_fig(fig, FILES[4])


def plot_06(df: pd.DataFrame) -> None:
    roi = df["roi"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(roi, bins=40)
    ax.axvline(roi.mean(), linestyle="--", linewidth=1.2, label=f"Moyenne ({roi.mean():.2f})")
    ax.axvline(roi.median(), linestyle=":", linewidth=1.2, label=f"Mediane ({roi.median():.2f})")
    ax.set_title("Distribution du ROI (200 005 campagnes)")
    ax.set_xlabel("ROI")
    ax.set_ylabel("Nombre de campagnes")
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_fig(fig, FILES[5])


def plot_07(df: pd.DataFrame) -> None:
    """Histogramme du CTR en % : moyenne > mediane (asymetrie a droite)."""
    ctr = df["ctr_percent"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(ctr, bins=60, range=(0, 100))
    ax.axvline(ctr.mean(), linestyle="--", linewidth=1.2, label=f"Moyenne ({ctr.mean():.2f} %)")
    ax.axvline(ctr.median(), linestyle=":", linewidth=1.2, label=f"Mediane ({ctr.median():.2f} %)")
    ax.set_xlim(0, 100)
    ax.set_title("Distribution du CTR (%) — asymetrie a droite")
    ax.set_xlabel("CTR (%)")
    ax.set_ylabel("Nombre de campagnes")
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_fig(fig, FILES[6])


def plot_08(df: pd.DataFrame) -> None:
    cost = df["acquisition_cost"]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.hist(cost, bins=40)
    ax.axvline(cost.mean(), linestyle="--", linewidth=1.2, label=f"Moyenne ({cost.mean():,.0f})")
    ax.axvline(cost.median(), linestyle=":", linewidth=1.2, label=f"Mediane ({cost.median():,.0f})")
    ax.set_title("Distribution du cout d'acquisition (montant par campagne)")
    ax.set_xlabel("Cout d'acquisition (montant, unites de la source)")
    ax.set_ylabel("Nombre de campagnes")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _p: f"{x:,.0f}"))
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_fig(fig, FILES[7])


def plot_09(df: pd.DataFrame) -> None:
    """15 valeurs discretes : barres, pas un histograme continu."""
    pct = (df["conversion_rate"] * 100).round(0)
    vc = pct.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(vc.index.astype(int), vc.values, width=0.7)
    ax.set_title("Distribution discrete du taux de conversion (15 valeurs)")
    ax.set_xlabel("Taux de conversion (%)")
    ax.set_ylabel("Nombre de campagnes")
    ax.set_xticks(vc.index.astype(int))
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_fig(fig, FILES[8])


def plot_10(df: pd.DataFrame) -> None:
    corr = df[CORR_COLS].corr(method="pearson")
    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1, aspect="equal")
    ax.set_xticks(range(len(CORR_COLS)), CORR_COLS, rotation=35, ha="right")
    ax.set_yticks(range(len(CORR_COLS)), CORR_COLS)
    for i in range(len(CORR_COLS)):
        for j in range(len(CORR_COLS)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="r de Pearson")
    ax.set_title(
        "Correlations de Pearson entre variables numeriques\n"
        "CTR = clicks / impressions : les liens CTR–clics et CTR–impressions "
        "sont definitionnels, pas causaux"
    )
    fig.tight_layout()
    save_fig(fig, FILES[9])


def roi_class_labels(df: pd.DataFrame) -> pd.Series:
    return pd.cut(
        df["roi"],
        bins=[-np.inf, 4, 6, np.inf],
        labels=["Faible", "Moyen", "Eleve"],
        right=False,
    )


def ctr_class_labels(df: pd.DataFrame) -> pd.Series:
    return pd.cut(
        df["ctr_percent"],
        bins=[-np.inf, 5, 15, np.inf],
        labels=["Faible", "Moyen", "Eleve"],
        right=False,
    )


def plot_boxplot_by_class(series_y: pd.Series, classes: pd.Series, title: str, xlabel: str, outfile: str) -> None:
    order = ["Faible", "Moyen", "Eleve"]
    data = [series_y[classes == lab].to_numpy() for lab in order]
    ns = [len(d) for d in data]
    labels = [f"{lab}\n(n={n:,})".replace(",", " ") for lab, n in zip(order, ns)]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("ROI")
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_fig(fig, outfile)


def plot_11(df: pd.DataFrame) -> None:
    plot_boxplot_by_class(
        df["roi"],
        roi_class_labels(df),
        "Distribution du ROI par classe de ROI\n(points extremes non dessines, 200 005 lignes)",
        "Classe de ROI (Faible < 4 ; Moyen 4-6 ; Eleve >= 6)",
        FILES[10],
    )


def plot_12(df: pd.DataFrame) -> None:
    plot_boxplot_by_class(
        df["roi"],
        ctr_class_labels(df),
        "ROI selon la classe de CTR\nLes distributions de ROI restent tres proches",
        "Classe de CTR (Faible < 5 % ; Moyen 5-15 % ; Eleve >= 15 %)",
        FILES[11],
    )


def heatmap_means(pivot: pd.DataFrame, title: str, xlabel: str, ylabel: str, outfile: str) -> None:
    """Heatmap Matplotlib d'une table de moyennes, valeurs dans les cellules."""
    fig, ax = plt.subplots(figsize=(10, 6))
    vmin = float(pivot.min().min())
    vmax = float(pivot.max().max())
    # Echelle zoomée autour des moyennes observees, avec note anti-surinterpretation.
    im = ax.imshow(pivot.values, cmap="coolwarm", vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(pivot.shape[1]), pivot.columns.astype(str), rotation=25, ha="right")
    ax.set_yticks(range(pivot.shape[0]), pivot.index.astype(str))
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.values[i, j]:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="ROI moyen (echelle zoomée)")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    save_fig(fig, outfile)


def plot_13(df: pd.DataFrame) -> None:
    pivot = df.pivot_table(
        index="target_audience",
        columns="customer_segment",
        values="roi",
        aggfunc="mean",
    )
    heatmap_means(
        pivot,
        "ROI moyen : audience x segment (25 combinaisons)\n"
        "Ecarts faibles : ne pas surinterpreter les couleurs",
        "Segment client",
        "Audience cible",
        FILES[12],
    )


def plot_14(df: pd.DataFrame) -> None:
    pivot = df.pivot_table(
        index="company",
        columns="channel_used",
        values="roi",
        aggfunc="mean",
    )
    heatmap_means(
        pivot,
        "ROI moyen : entreprise x canal (30 combinaisons)\n"
        "Ecarts faibles : ne pas surinterpreter les couleurs",
        "Canal",
        "Entreprise",
        FILES[13],
    )


def plot_15(df: pd.DataFrame) -> None:
    order = [15, 30, 45, 60]
    data = [df.loc[df["duration_days"] == d, "roi"].to_numpy() for d in order]
    means = [arr.mean() for arr in data]
    labels = [f"{d} jours\n(moy. {m:.2f})" for d, m in zip(order, means)]
    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.set_title("ROI selon la duree de campagne\nDifferences de moyennes tres faibles")
    ax.set_xlabel("Duree (jours)")
    ax.set_ylabel("ROI")
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_fig(fig, FILES[14])


def plot_16(df: pd.DataFrame) -> None:
    means = df.groupby("engagement_score")["roi"].mean().reindex(range(1, 11))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(means.index, means.values, marker="o")
    ax.axhline(df["roi"].mean(), linestyle="--", linewidth=1, label="ROI moyen global")
    ax.set_xticks(range(1, 11))
    ax.set_title("ROI moyen selon le score d'engagement (1 a 10)\nPas de gradient clair")
    ax.set_xlabel("Score d'engagement")
    ax.set_ylabel("ROI moyen")
    ax.set_ylim(4.90, 5.10)
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    save_fig(fig, FILES[15])


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_and_prepare()
    original_snapshot = df[ORIGINAL_COLS].copy()

    errors = verify_frame(df)
    print("Controles pre-graphiques :", "OK" if not errors else ", ".join(errors))
    if errors:
        return 1

    known_months = set(range(1, 13))
    if set(df["month"].unique()) != known_months:
        print("ERREUR : mois inattendus", sorted(df["month"].unique()))
        return 1

    plotters = [
        plot_01,
        plot_02,
        plot_03,
        plot_04,
        plot_05,
        plot_06,
        plot_07,
        plot_08,
        plot_09,
        plot_10,
        plot_11,
        plot_12,
        plot_13,
        plot_14,
        plot_15,
        plot_16,
    ]
    only: set[int] | None = None
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        only = {int(x) for x in sys.argv[idx + 1].split(",")}

    statuses: list[tuple[int, str, str, str]] = []
    for i, (fn, name) in enumerate(zip(plotters, FILES), start=1):
        if only is not None and i not in only:
            path = OUT_DIR / name
            ok = path.exists() and path.stat().st_size > 1000
            statuses.append((i, name, name, "OK" if ok else "ABSENT"))
            print(f"{i:02d} {name} : conserve ({path.stat().st_size if path.exists() else 0} octets)")
            continue
        fn(df)
        path = OUT_DIR / name
        ok = path.exists() and path.stat().st_size > 1000
        statuses.append((i, name, name, "OK" if ok else "ECHEC"))
        print(f"{i:02d} {name} : {'OK' if ok else 'ECHEC'} ({path.stat().st_size if path.exists() else 0} octets)")

    originals_ok = original_snapshot.equals(df[ORIGINAL_COLS])
    files_ok = all(s[3] == "OK" for s in statuses)
    n_ok = sum(1 for s in statuses if s[3] == "OK")

    print()
    print("| # | Visualisation | Fichier | Statut |")
    print("|---|---|---|---|")
    labels = [
        "Volume par entreprise",
        "Volume par type",
        "Volume par canal",
        "Volume mensuel",
        "ROI moyen mensuel",
        "Distribution ROI",
        "Distribution CTR",
        "Distribution cout d'acquisition",
        "Distribution conversion",
        "Heatmap correlations",
        "ROI par classe de ROI",
        "ROI par classe de CTR",
        "Heatmap audience x segment",
        "Heatmap entreprise x canal",
        "ROI par duree",
        "ROI par engagement",
    ]
    for (i, _n, fname, st), lab in zip(statuses, labels):
        print(f"| {i} | {lab} | {fname} | {st} |")

    print()
    print("VISUALISATIONS TERMINÉES")
    print(f"- nombre de graphiques crees : {n_ok}/16")
    print(f"- dossier de sortie : {OUT_DIR}")
    print(f"- controles : pre-graphiques={'OK' if not errors else 'ECHEC'} ; fichiers={'OK' if files_ok else 'ECHEC'} ; sources={'OK' if originals_ok else 'ECHEC'}")
    print(f"- erreurs : {0 if files_ok and originals_ok and not errors else 1}")
    print()
    print("VISUALISATIONS TERMINÉES")
    print(f"- graphiques crees : {n_ok}/16")
    print(f"- erreurs : {0 if files_ok and originals_ok else 1}")
    print("- donnees modifiees : non" if originals_ok else "- donnees modifiees : oui")
    print("- PostgreSQL modifie : non")
    print(f"- dossier de sortie : {OUT_DIR.name}/")
    return 0 if files_ok and originals_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
