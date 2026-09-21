"""
ÉTAPE 5 — Dashboard analytique Streamlit + Pandas + Matplotlib.

Lecture seule PostgreSQL. Aucune modification des données sources.
Les agrégations et graphiques sont recalculés sur un DataFrame filtré,
sans altérer le DataFrame chargé.
"""

from __future__ import annotations

import os
from io import BytesIO
from urllib.parse import quote_plus

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

HOST = "127.0.0.1"
PORT = 5432
USER = "data_project"
DATABASE = "marketing_analysis"
EXPECTED_N = 200_005
SQL = """
SELECT *
FROM public.marketing_campaigns
ORDER BY campaign_id
"""
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
CORR_LABELS = [
    "ROI",
    "Acquisition Cost",
    "Conversion Rate",
    "Clicks",
    "Impressions",
    "Engagement Score",
    "Duration",
    "CTR",
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
MONTH_FR = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre",
}
QUARTER_MONTHS = {
    "Q1": [1, 2, 3],
    "Q2": [4, 5, 6],
    "Q3": [7, 8, 9],
    "Q4": [10, 11, 12],
}
CTR_CLASS_LABELS = ["Faible", "Moyen", "Élevé"]
DURATION_ORDER = [15, 30, 45, 60]
FILTER_TOUS = "Tous"

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#4a4a4a",
        "axes.labelcolor": "#222222",
        "xtick.color": "#222222",
        "ytick.color": "#222222",
        "font.size": 9,
        "axes.titlesize": 11,
    }
)


def _sanitize_error(message: str, password: str) -> str:
    cleaned = message
    if password:
        cleaned = cleaned.replace(password, "***")
        cleaned = cleaned.replace(quote_plus(password), "***")
    return cleaned


@st.cache_data(show_spinner="Chargement des campagnes depuis PostgreSQL (lecture seule)…")
def load_and_prepare(password: str) -> pd.DataFrame:
    """Extraction lecture seule puis préparation Pandas. Ne modifie pas PostgreSQL."""
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


@st.cache_data
def filter_choices(_df: pd.DataFrame) -> dict[str, list]:
    """Listes de valeurs pour les filtres (calculées une fois)."""
    return {
        "company": [FILTER_TOUS] + sorted(_df["company"].dropna().astype(str).unique().tolist()),
        "campaign_type": [FILTER_TOUS]
        + sorted(_df["campaign_type"].dropna().astype(str).unique().tolist()),
        "channel_used": [FILTER_TOUS]
        + sorted(_df["channel_used"].dropna().astype(str).unique().tolist()),
        "target_audience": [FILTER_TOUS]
        + sorted(_df["target_audience"].dropna().astype(str).unique().tolist()),
        "customer_segment": [FILTER_TOUS]
        + sorted(_df["customer_segment"].dropna().astype(str).unique().tolist()),
        "location": [FILTER_TOUS] + sorted(_df["location"].dropna().astype(str).unique().tolist()),
        "quarter": [FILTER_TOUS] + ["Q1", "Q2", "Q3", "Q4"],
        "month": [FILTER_TOUS] + [MONTH_FR[m] for m in range(1, 13)],
    }


def apply_filters(
    df: pd.DataFrame,
    company: str,
    campaign_type: str,
    channel: str,
    audience: str,
    segment: str,
    location: str,
    quarter: str,
    month_label: str,
) -> pd.DataFrame:
    """Retourne un sous-ensemble. Le DataFrame source n'est pas modifié."""
    mask = pd.Series(True, index=df.index)
    if company != FILTER_TOUS:
        mask &= df["company"] == company
    if campaign_type != FILTER_TOUS:
        mask &= df["campaign_type"] == campaign_type
    if channel != FILTER_TOUS:
        mask &= df["channel_used"] == channel
    if audience != FILTER_TOUS:
        mask &= df["target_audience"] == audience
    if segment != FILTER_TOUS:
        mask &= df["customer_segment"] == segment
    if location != FILTER_TOUS:
        mask &= df["location"] == location
    if quarter != FILTER_TOUS:
        mask &= df["quarter"] == quarter
    if month_label != FILTER_TOUS:
        month_num = next(m for m, name in MONTH_FR.items() if name == month_label)
        mask &= df["month"] == month_num
    return df.loc[mask]


def fmt_int(n: int | float) -> str:
    return f"{int(n):,}".replace(",", " ")


def fmt_num(x: float, nd: int = 4) -> str:
    if x is None or not np.isfinite(x):
        return "n.d."
    return f"{x:.{nd}f}".replace(".", ",")


def fmt_fr(x: float, nd: int = 2) -> str:
    """Nombre français : milliers en espaces, virgule décimale."""
    if x is None or not np.isfinite(x):
        return "n.d."
    raw = f"{x:,.{nd}f}"
    whole, _, frac = raw.partition(".")
    whole = whole.replace(",", " ")
    return f"{whole},{frac}" if nd else whole


def fmt_pct(x: float, nd: int = 2) -> str:
    if x is None or not np.isfinite(x):
        return "n.d."
    return f"{x:.{nd}f} %".replace(".", ",")


def finite_series(s: pd.Series) -> pd.Series:
    values = pd.to_numeric(s, errors="coerce")
    return values[np.isfinite(values)]


def months_to_display(quarter: str, month_label: str) -> list[int]:
    if month_label != FILTER_TOUS:
        return [next(m for m, name in MONTH_FR.items() if name == month_label)]
    if quarter != FILTER_TOUS:
        return QUARTER_MONTHS[quarter]
    return list(range(1, 13))


def show_fig(fig: plt.Figure) -> None:
    st.pyplot(fig, clear_figure=True)
    plt.close(fig)


def add_bar_labels(ax, values, percents=None) -> None:
    for i, val in enumerate(values):
        if not np.isfinite(val):
            continue
        if percents is None:
            txt = fmt_int(val)
        else:
            pct = percents[i]
            txt = f"{fmt_int(val)}\n({pct:.1f} %)".replace(".", ",")
        ax.text(i, val, txt, ha="center", va="bottom", fontsize=8)


def fig_volume_bars(df: pd.DataFrame, col: str, title: str, xlabel: str) -> plt.Figure | None:
    if df.empty:
        return None
    counts = df[col].value_counts().sort_index()
    denom = max(len(df), 1)
    percents = counts / denom * 100
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.bar(range(len(counts)), counts.values, color="#3d5a80")
    ax.set_xticks(range(len(counts)), counts.index.astype(str), rotation=20, ha="right")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Nombre de campagnes")
    ymax = float(counts.max()) if len(counts) else 1.0
    ax.set_ylim(0, ymax * 1.18 if ymax > 0 else 1)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    add_bar_labels(ax, counts.values, percents.values)
    fig.tight_layout()
    return fig


def fig_volume_mensuel(df: pd.DataFrame, months: list[int], unfiltered: bool) -> plt.Figure | None:
    if df.empty:
        return None
    g = (
        df.groupby("month")
        .agg(
            n=("campaign_id", "count"),
            n_jours=("campaign_date", lambda s: int(s.dt.days_in_month.iloc[0])),
        )
        .reindex(months)
    )
    g["per_day"] = g["n"] / g["n_jours"]
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(9.5, 6.4))
    ax1.plot(g.index, g["n"], marker="o", color="#3d5a80")
    ax1.set_title("Nombre de campagnes par mois")
    ax1.set_ylabel("Nombre de campagnes")
    ax1.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax1.set_axisbelow(True)

    ax2.plot(g.index, g["per_day"], marker="o", color="#3d5a80")
    per_day = finite_series(g["per_day"])
    if not per_day.empty:
        ax2.axhline(
            float(per_day.mean()),
            linestyle="--",
            linewidth=1,
            color="#9a031e",
            label="moyenne journalière",
        )
    ax2.set_title("Campagnes par jour civil (n / nombre de jours du mois)")
    ax2.set_xlabel("Mois")
    ax2.set_ylabel("Campagnes / jour")
    ax2.set_xticks(months, [MONTH_LABELS[m - 1] for m in months])
    if unfiltered and months == list(range(1, 13)):
        ax2.set_ylim(540, 556)
    elif not per_day.empty:
        center = float(per_day.mean())
        spread = float(per_day.max() - per_day.min())
        pad = max(8.0, spread * 3.0)
        ax2.set_ylim(center - pad, center + pad)
    ax2.legend(frameon=False)
    ax2.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax2.set_axisbelow(True)
    fig.suptitle(
        "Le volume mensuel suit principalement le nombre de jours du mois",
        y=1.02,
        fontsize=10,
    )
    fig.tight_layout()
    return fig


def fig_roi_mensuel(df: pd.DataFrame, months: list[int], unfiltered: bool) -> plt.Figure | None:
    if df.empty:
        return None
    monthly = df.groupby("month")["roi"].mean().reindex(months)
    global_mean = float(finite_series(df["roi"]).mean()) if len(df) else np.nan
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.plot(
        monthly.index,
        monthly.values,
        marker="o",
        color="#3d5a80",
        label="ROI moyen mensuel",
    )
    if np.isfinite(global_mean):
        ax.axhline(
            global_mean,
            linestyle="--",
            linewidth=1,
            color="#9a031e",
            label=f"ROI moyen du sous-ensemble ({global_mean:.2f})".replace(".", ","),
        )
    ax.set_xticks(months, [MONTH_LABELS[m - 1] for m in months])
    ax.set_title("ROI moyen par mois — écarts faibles : ne pas lire comme une tendance")
    ax.set_xlabel("Mois")
    ax.set_ylabel("ROI moyen")
    if unfiltered and months == list(range(1, 13)):
        ax.set_ylim(4.90, 5.10)
    else:
        vals = finite_series(monthly)
        if not vals.empty:
            center = float(vals.mean())
            spread = float(vals.max() - vals.min())
            pad = max(0.10, spread * 3.0)
            ax.set_ylim(center - pad, center + pad)
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def fig_hist(
    series: pd.Series,
    title: str,
    xlabel: str,
    bins: int,
    mean_fmt: str,
    median_fmt: str,
    hist_range: tuple[float, float] | None = None,
    x_formatter=None,
) -> plt.Figure | None:
    values = finite_series(series)
    if values.empty:
        return None
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.hist(values, bins=bins, range=hist_range, color="#3d5a80")
    mean_v = float(values.mean())
    median_v = float(values.median())
    ax.axvline(mean_v, linestyle="--", linewidth=1.2, color="#9a031e", label=mean_fmt.format(mean_v))
    ax.axvline(median_v, linestyle=":", linewidth=1.2, color="#0f4c5c", label=median_fmt.format(median_v))
    if hist_range is not None:
        ax.set_xlim(*hist_range)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Nombre de campagnes")
    if x_formatter is not None:
        ax.xaxis.set_major_formatter(x_formatter)
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def fig_conversion_discrete(df: pd.DataFrame) -> plt.Figure | None:
    if df.empty:
        return None
    pct = (df["conversion_rate"] * 100).round(0)
    vc = pct.value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.bar(vc.index.astype(int), vc.values, width=0.7, color="#3d5a80")
    ax.set_title("Distribution discrète du taux de conversion")
    ax.set_xlabel("Taux de conversion (%)")
    ax.set_ylabel("Nombre de campagnes")
    ax.set_xticks(vc.index.astype(int))
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def fig_heatmap_means(pivot: pd.DataFrame, title: str, xlabel: str, ylabel: str) -> plt.Figure | None:
    if pivot.empty or pivot.size == 0:
        return None
    values = pivot.to_numpy(dtype=float)
    if not np.isfinite(values).any():
        return None
    vmin = float(np.nanmin(values))
    vmax = float(np.nanmax(values))
    if vmin == vmax:
        vmin -= 0.05
        vmax += 0.05
    fig, ax = plt.subplots(figsize=(9.5, 5.2))
    im = ax.imshow(values, cmap="coolwarm", vmin=vmin, vmax=vmax, aspect="auto")
    ax.set_xticks(range(pivot.shape[1]), pivot.columns.astype(str), rotation=25, ha="right")
    ax.set_yticks(range(pivot.shape[0]), pivot.index.astype(str))
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = values[i, j]
            if np.isfinite(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="ROI moyen")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    return fig


def ctr_class_labels(df: pd.DataFrame) -> pd.Series:
    return pd.cut(
        df["ctr_percent"],
        bins=[-np.inf, 5, 15, np.inf],
        labels=CTR_CLASS_LABELS,
        right=False,
    )


def fig_roi_classes_ctr(df: pd.DataFrame) -> plt.Figure | None:
    if df.empty:
        return None
    classes = ctr_class_labels(df)
    plot_data = []
    labels = []
    for lab in CTR_CLASS_LABELS:
        arr = finite_series(df.loc[classes == lab, "roi"]).to_numpy()
        if len(arr) == 0:
            continue
        plot_data.append(arr)
        labels.append(f"{lab}\n(n={fmt_int(len(arr))})")
    if not plot_data:
        return None
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.boxplot(plot_data, tick_labels=labels, showfliers=False)
    ax.set_title("ROI selon la classe de CTR\nLes distributions de ROI restent très proches")
    ax.set_xlabel("Classe de CTR (Faible < 5 % ; Moyen 5–15 % ; Élevé ≥ 15 %)")
    ax.set_ylabel("ROI")
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def fig_correlations(df: pd.DataFrame) -> plt.Figure | None:
    if df.empty:
        return None
    subset = df[CORR_COLS].apply(pd.to_numeric, errors="coerce")
    corr = subset.corr(method="pearson")
    if corr.isna().all().all():
        return None
    fig, ax = plt.subplots(figsize=(8.8, 7.0))
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1, aspect="equal")
    ax.set_xticks(range(len(CORR_LABELS)), CORR_LABELS, rotation=35, ha="right")
    ax.set_yticks(range(len(CORR_LABELS)), CORR_LABELS)
    for i in range(len(CORR_COLS)):
        for j in range(len(CORR_COLS)):
            val = corr.values[i, j]
            if np.isfinite(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="r de Pearson")
    ax.set_title("Corrélations de Pearson entre variables numériques")
    fig.tight_layout()
    return fig


def fig_roi_duration(df: pd.DataFrame) -> plt.Figure | None:
    if df.empty:
        return None
    data = []
    labels = []
    for duration in DURATION_ORDER:
        arr = finite_series(df.loc[df["duration_days"] == duration, "roi"]).to_numpy()
        if len(arr) == 0:
            continue
        data.append(arr)
        labels.append(f"{duration} jours\n(moy. {arr.mean():.2f})".replace(".", ","))
    if not data:
        return None
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.set_title("ROI selon la durée de campagne\nDifférences de moyennes très faibles")
    ax.set_xlabel("Durée (jours)")
    ax.set_ylabel("ROI")
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def fig_roi_engagement(df: pd.DataFrame) -> plt.Figure | None:
    if df.empty:
        return None
    means = df.groupby("engagement_score")["roi"].mean().reindex(range(1, 11))
    global_mean = float(finite_series(df["roi"]).mean()) if len(df) else np.nan
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    ax.plot(means.index, means.values, marker="o", color="#3d5a80")
    if np.isfinite(global_mean):
        ax.axhline(
            global_mean,
            linestyle="--",
            linewidth=1,
            color="#9a031e",
            label="ROI moyen du sous-ensemble",
        )
    ax.set_xticks(range(1, 11))
    ax.set_title("ROI moyen selon le score d'engagement (1 à 10)\nPas de gradient clair")
    ax.set_xlabel("Score d'engagement")
    ax.set_ylabel("ROI moyen")
    vals = finite_series(means)
    if not vals.empty:
        center = float(vals.mean())
        spread = float(vals.max() - vals.min())
        pad = max(0.10, spread * 3.0)
        ax.set_ylim(center - pad, center + pad)
    ax.legend(frameon=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4)
    ax.set_axisbelow(True)
    fig.tight_layout()
    return fig


def ctr_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    classes = ctr_class_labels(df)
    rows = []
    for lab in CTR_CLASS_LABELS:
        subset = finite_series(df.loc[classes == lab, "roi"])
        n = int(len(subset))
        mean_roi = float(subset.mean()) if n else np.nan
        rows.append(
            {
                "Classe de CTR": lab,
                "Définition": {
                    "Faible": "CTR < 5 %",
                    "Moyen": "5 % ≤ CTR < 15 %",
                    "Élevé": "CTR ≥ 15 %",
                }[lab],
                "Effectif": fmt_int(n) if n else "0",
                "ROI moyen": fmt_num(mean_roi, 4),
            }
        )
    return pd.DataFrame(rows)


def inject_style() -> None:
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1280px; }
        h1 { font-size: 1.72rem !important; font-weight: 650 !important; letter-spacing: -0.02em; }
        h2 { font-size: 1.22rem !important; margin-top: 1.4rem !important; border-bottom: 1px solid #dde1e6; padding-bottom: 0.35rem; }
        h3 { font-size: 1.02rem !important; color: #243447 !important; }
        div[data-testid="stMetric"] {
            background: #f5f7f9;
            border: 1px solid #d9dee5;
            padding: 0.7rem 0.85rem;
            border-radius: 6px;
        }
        div[data-testid="stMetric"] label { color: #4a5560 !important; }
        .stCaption, .stMarkdown p { line-height: 1.45; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.title("Analyse des performances des campagnes marketing")
    st.markdown("**Dashboard analytique — 200 005 campagnes — Année 2021**")
    st.caption(
        "Analyse exploratoire des performances selon les entreprises, "
        "types de campagnes, canaux, audiences, segments et période."
    )


def render_kpis(filtered: pd.DataFrame) -> None:
    n = int(len(filtered))
    roi = float(finite_series(filtered["roi"]).mean()) if n else np.nan
    cost = float(finite_series(filtered["acquisition_cost"]).mean()) if n else np.nan
    conv = float(finite_series(filtered["conversion_rate"]).mean()) if n else np.nan
    ctr = float(finite_series(filtered["ctr_percent"]).mean()) if n else np.nan
    eng = float(finite_series(filtered["engagement_score"]).mean()) if n else np.nan

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Nombre de campagnes", fmt_int(n) if n else "0")
    c2.metric("ROI moyen", fmt_num(roi, 4))
    c3.metric("Coût d'acquisition moyen", fmt_fr(cost, 2))
    c4.metric("Taux de conversion moyen", fmt_pct(conv * 100, 2) if np.isfinite(conv) else "n.d.")
    c5.metric("CTR moyen", fmt_pct(ctr, 2))
    c6.metric("Engagement moyen", fmt_num(eng, 2))
    st.caption(
        "Indicateurs calculés sur le sous-ensemble actuellement filtré. "
        "Le CTR est affiché en pourcentage (moyenne des CTR individuels). "
        "Le taux de conversion est affiché en pourcentage."
    )


def render_overview(filtered: pd.DataFrame) -> None:
    st.header("1. Vue d'ensemble")
    st.caption("Volumes par entreprise, type de campagne et canal — pas un classement de performance.")
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("A. Volume par entreprise")
        fig = fig_volume_bars(
            filtered,
            "company",
            "Répartition des campagnes par entreprise",
            "Entreprise",
        )
        if fig is not None:
            show_fig(fig)
        else:
            st.info("Aucune donnée pour ce graphique.")
    with col_b:
        st.subheader("B. Volume par type")
        fig = fig_volume_bars(
            filtered,
            "campaign_type",
            "Répartition des campagnes par type",
            "Type de campagne",
        )
        if fig is not None:
            show_fig(fig)
        else:
            st.info("Aucune donnée pour ce graphique.")
    st.subheader("C. Volume par canal")
    fig = fig_volume_bars(
        filtered,
        "channel_used",
        "Répartition des campagnes par canal",
        "Canal",
    )
    if fig is not None:
        show_fig(fig)
    else:
        st.info("Aucune donnée pour ce graphique.")


def render_performance(filtered: pd.DataFrame) -> None:
    st.header("2. Performance")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.subheader("A. Distribution du ROI")
        fig = fig_hist(
            filtered["roi"],
            "Distribution du ROI",
            "ROI",
            bins=40,
            mean_fmt="Moyenne ({:.2f})",
            median_fmt="Médiane ({:.2f})",
        )
        if fig is not None:
            show_fig(fig)
        else:
            st.info("Aucune donnée pour ce graphique.")
    with r1c2:
        st.subheader("B. Distribution du coût d'acquisition")
        fig = fig_hist(
            filtered["acquisition_cost"],
            "Distribution du coût d'acquisition",
            "Coût d'acquisition (unités de la source)",
            bins=40,
            mean_fmt="Moyenne ({:,.0f})",
            median_fmt="Médiane ({:,.0f})",
            x_formatter=plt.FuncFormatter(lambda x, _p: f"{x:,.0f}"),
        )
        if fig is not None:
            show_fig(fig)
        else:
            st.info("Aucune donnée pour ce graphique.")
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.subheader("C. Distribution du taux de conversion")
        fig = fig_conversion_discrete(filtered)
        if fig is not None:
            show_fig(fig)
        else:
            st.info("Aucune donnée pour ce graphique.")
    with r2c2:
        st.subheader("D. Distribution du CTR")
        fig = fig_hist(
            filtered["ctr_percent"],
            "Distribution du CTR (%) — asymétrie à droite",
            "CTR (%)",
            bins=60,
            mean_fmt="Moyenne ({:.2f} %)",
            median_fmt="Médiane ({:.2f} %)",
            hist_range=(0, 100),
        )
        if fig is not None:
            show_fig(fig)
        else:
            st.info("Aucune donnée pour ce graphique.")


def render_audience(filtered: pd.DataFrame) -> None:
    st.header("3. Audience, segments et canaux")
    st.subheader("A. ROI moyen : audience × segment")
    pivot_as = filtered.pivot_table(
        index="target_audience",
        columns="customer_segment",
        values="roi",
        aggfunc="mean",
    )
    fig = fig_heatmap_means(
        pivot_as,
        "ROI moyen : audience × segment",
        "Segment client",
        "Audience cible",
    )
    if fig is not None:
        show_fig(fig)
    else:
        st.info("Aucune donnée pour ce graphique.")
    st.caption(
        "Les écarts observés sont faibles ; ils ne permettent pas d'établir "
        "une différence forte entre les combinaisons."
    )

    st.subheader("B. ROI moyen : entreprise × canal")
    pivot_cc = filtered.pivot_table(
        index="company",
        columns="channel_used",
        values="roi",
        aggfunc="mean",
    )
    fig = fig_heatmap_means(
        pivot_cc,
        "ROI moyen : entreprise × canal — écarts faibles, pas un classement",
        "Canal",
        "Entreprise",
    )
    if fig is not None:
        show_fig(fig)
    else:
        st.info("Aucune donnée pour ce graphique.")
    st.caption(
        "Les couleurs reflètent de petits écarts de moyennes. "
        "Ce graphique ne constitue pas un classement de canaux ou d'entreprises."
    )

    st.subheader("C. ROI moyen par classe de CTR")
    summary = ctr_summary_table(filtered)
    st.dataframe(summary, hide_index=True, width="stretch")
    fig = fig_roi_classes_ctr(filtered)
    if fig is not None:
        show_fig(fig)
    else:
        st.info("Aucune donnée pour ce graphique.")
    st.caption("Les ROI moyens sont très proches entre les trois classes.")


def render_time(filtered: pd.DataFrame, quarter: str, month_label: str, unfiltered: bool) -> None:
    st.header("4. Analyse temporelle")
    months = months_to_display(quarter, month_label)
    st.subheader("A. Volume mensuel")
    fig = fig_volume_mensuel(filtered, months, unfiltered)
    if fig is not None:
        show_fig(fig)
    else:
        st.info("Aucune donnée pour ce graphique.")
    st.caption(
        "Le rythme quotidien est proche de 548 campagnes/jour sur l'ensemble de 2021. "
        "Les mois plus courts (février) ont un volume total plus bas sans baisse d'activité journalière. "
        "L'échelle du rythme quotidien est volontairement large afin de ne pas exagérer de très faibles écarts."
    )
    st.subheader("B. ROI moyen mensuel")
    fig = fig_roi_mensuel(filtered, months, unfiltered)
    if fig is not None:
        show_fig(fig)
    else:
        st.info("Aucune donnée pour ce graphique.")
    st.caption(
        "Les variations mensuelles du ROI sont faibles. "
        "Elles ne doivent pas être présentées comme une tendance forte."
    )


def render_relations(filtered: pd.DataFrame) -> None:
    st.header("5. Relations entre variables")
    st.subheader("A. Corrélations")
    fig = fig_correlations(filtered)
    if fig is not None:
        show_fig(fig)
    else:
        st.info("Aucune donnée pour ce graphique.")
    st.caption(
        "CTR = Clicks / Impressions. Les corrélations CTR–Clicks et CTR–Impressions "
        "sont donc liées à la définition du ratio et ne doivent pas être interprétées "
        "comme des relations causales."
    )

    with st.expander("Analyses complémentaires — ROI selon la durée et l'engagement", expanded=False):
        st.caption(
            "Analyses secondaires. Les écarts restent faibles dans ce dataset ; "
            "ils ne justifient pas une lecture causale."
        )
        c1, c2 = st.columns(2)
        with c1:
            fig = fig_roi_duration(filtered)
            if fig is not None:
                show_fig(fig)
            else:
                st.info("Aucune donnée pour ce graphique.")
        with c2:
            fig = fig_roi_engagement(filtered)
            if fig is not None:
                show_fig(fig)
            else:
                st.info("Aucune donnée pour ce graphique.")


def render_conclusions() -> None:
    st.header("6. Conclusions et limites")
    st.subheader("Principaux constats")
    st.caption(
        "Constats établis par l'EDA sur l'ensemble des 200 005 campagnes de 2021, "
        "indépendamment des filtres appliqués ci-dessus."
    )
    st.markdown(
        """
1. Les volumes sont très équilibrés entre les entreprises, types de campagnes, audiences, localisations et segments.
2. Le volume mensuel suit principalement le nombre de jours du mois ; le rythme quotidien est proche de 548 campagnes/jour.
3. Le CTR présente une distribution asymétrique : moyenne 14,04 % contre médiane 9,98 %.
4. Le ROI moyen est proche de 5 dans les différentes dimensions analysées.
5. Les corrélations les plus visibles concernent CTR avec Clicks et Impressions, ce qui découle de la définition du CTR.
6. Les variations de ROI selon CTR, durée et engagement restent faibles dans ce dataset.
        """
    )

    st.subheader("Limites de l'analyse")
    st.markdown(
        """
- Les données sont observationnelles.
- L'analyse décrit des associations et des distributions.
- Elle ne permet pas d'établir une causalité.
- Les écarts entre catégories sont souvent très faibles.
- Les corrélations CTR / Clicks / Impressions sont en partie mécaniques.
- Le dataset doit être interprété dans son contexte.
- Les résultats ne doivent pas être généralisés au-delà des données étudiées.
        """
    )
    st.caption(
        "Source : PostgreSQL marketing_analysis.public.marketing_campaigns — extraction en lecture seule. "
        "Aucune écriture en base. Aucune modification des données sources."
    )


def render_export(filtered: pd.DataFrame) -> None:
    buffer = BytesIO()
    filtered.to_csv(buffer, index=False)
    st.download_button(
        label="Télécharger les données filtrées (CSV)",
        data=buffer.getvalue(),
        file_name="marketing_campaigns_filtered.csv",
        mime="text/csv",
        help="Export du sous-ensemble actuellement affiché. Le dataset original n'est pas modifié.",
    )


def main() -> None:
    st.set_page_config(
        page_title="Analyse des performances des campagnes marketing",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_style()
    render_header()

    st.sidebar.header("Connexion")
    env_password = os.environ.get("PGPASSWORD", "")
    password = st.sidebar.text_input(
        "Mot de passe du rôle data_project",
        value="",
        type="password",
        help="Saisie masquée, ou variable d'environnement PGPASSWORD. Jamais écrit dans le code.",
    )
    if not password:
        password = env_password
    st.sidebar.caption("Base : marketing_analysis — table : public.marketing_campaigns")

    if not password:
        st.info(
            "Saisir le mot de passe du rôle data_project dans la barre latérale "
            "pour charger les données (lecture seule)."
        )
        st.stop()

    try:
        df = load_and_prepare(password)
    except Exception as exc:
        st.error(
            "Impossible de charger les données. Vérifier le mot de passe et que "
            "PostgreSQL est accessible en lecture seule. "
            f"Détail : {_sanitize_error(str(exc), password)}"
        )
        st.stop()

    choices = filter_choices(df)

    st.sidebar.header("Filtres")
    st.sidebar.caption("Les filtres se combinent. « Tous » n'applique aucune restriction sur le champ.")
    company = st.sidebar.selectbox("Company", choices["company"])
    campaign_type = st.sidebar.selectbox("Campaign Type", choices["campaign_type"])
    channel = st.sidebar.selectbox("Channel", choices["channel_used"])
    audience = st.sidebar.selectbox("Target Audience", choices["target_audience"])
    segment = st.sidebar.selectbox("Customer Segment", choices["customer_segment"])
    location = st.sidebar.selectbox("Location", choices["location"])
    quarter = st.sidebar.selectbox("Quarter", choices["quarter"])
    month_label = st.sidebar.selectbox("Month", choices["month"])

    filtered = apply_filters(
        df,
        company=company,
        campaign_type=campaign_type,
        channel=channel,
        audience=audience,
        segment=segment,
        location=location,
        quarter=quarter,
        month_label=month_label,
    )
    unfiltered = (
        company == FILTER_TOUS
        and campaign_type == FILTER_TOUS
        and channel == FILTER_TOUS
        and audience == FILTER_TOUS
        and segment == FILTER_TOUS
        and location == FILTER_TOUS
        and quarter == FILTER_TOUS
        and month_label == FILTER_TOUS
    )

    st.sidebar.markdown("---")
    st.sidebar.metric("Campagnes affichées", f"{fmt_int(len(filtered))} / {fmt_int(len(df))}")
    if st.sidebar.checkbox("Préparer l'export CSV du sous-ensemble", value=False):
        render_export(filtered)
    else:
        st.sidebar.caption(
            "Cocher pour générer marketing_campaigns_filtered.csv à partir du DataFrame filtré."
        )

    if filtered.empty:
        st.warning("Aucune campagne ne correspond à la combinaison de filtres sélectionnée.")
        st.stop()

    render_kpis(filtered)
    render_overview(filtered)
    render_performance(filtered)
    render_audience(filtered)
    render_time(filtered, quarter, month_label, unfiltered)
    render_relations(filtered)
    render_conclusions()


if __name__ == "__main__":
    main()
