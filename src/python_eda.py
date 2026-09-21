"""
ETAPE 3 — EDA Python/Pandas.

Workflow :
  PostgreSQL (SELECT lecture seule)
    -> DataFrame 15 colonnes
    -> preparation (year, month, month_name, quarter, ctr, ctr_percent)
    -> analyses A a S exclusivement dans Pandas

Aucune ecriture PostgreSQL, aucun graphique, aucune suppression de ligne/colonne source.
"""

from __future__ import annotations

import getpass
import sys
from itertools import product
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

HOST = "127.0.0.1"
PORT = 5432
USER = "data_project"
DATABASE = "marketing_analysis"
EXPECTED_N = 200005
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
PREP_COLS = ["year", "month", "month_name", "quarter", "ctr", "ctr_percent"]
CATEGORICAL_COLS = [
    "company",
    "campaign_type",
    "target_audience",
    "channel_used",
    "location",
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
SQL = """
SELECT *
FROM public.marketing_campaigns
ORDER BY campaign_id
"""


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def fmt_table(frame: pd.DataFrame) -> str:
    """Affichage numerique lisible, sans notation scientifique."""
    return frame.to_string(index=False, float_format=lambda x: f"{x:,.4f}")


def intensity(abs_r: float) -> str:
    """Grille descriptive de |r| (Pearson). Ce n'est pas une causalite."""
    if abs_r < 0.10:
        return "negligeable"
    if abs_r < 0.30:
        return "faible"
    if abs_r < 0.50:
        return "moderee"
    if abs_r < 0.70:
        return "notable"
    if abs_r < 0.90:
        return "forte"
    return "tres forte"


def load_and_prepare() -> pd.DataFrame:
    """Meme extraction + preparation que le workflow actuel."""
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

    # Preparation : conversion date et indicateurs, sans toucher aux sources.
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


def group_kpis(df: pd.DataFrame, by: str, extra: list[str] | None = None) -> pd.DataFrame:
    """KPI moyens par modalite, avec volume."""
    agg = {
        "campaign_id": "count",
        "roi": "mean",
        "acquisition_cost": "mean",
        "conversion_rate": "mean",
        "ctr_percent": "mean",
        "engagement_score": "mean",
    }
    extra = extra or []
    for col in extra:
        agg[col] = "mean"
    out = df.groupby(by, dropna=False, as_index=False).agg(agg)
    rename_map = {
        "campaign_id": "n_campagnes",
        "roi": "roi_moyen",
        "acquisition_cost": "cout_moyen",
        "conversion_rate": "conversion_moyenne",
        "ctr_percent": "ctr_moyen_pct",
        "engagement_score": "engagement_moyen",
        "clicks": "clicks_moyens",
        "impressions": "impressions_moyennes",
    }
    # Ne pas renommer la cle de regroupement si c'est duration_days.
    if "duration_days" in extra:
        rename_map["duration_days"] = "duree_moyenne"
    out = out.rename(columns=rename_map)
    return out


def missing_combos(df: pd.DataFrame, col_a: str, col_b: str) -> list[tuple]:
    """Combinaisons du produit cartesien absentes du DataFrame."""
    expected = set(product(sorted(df[col_a].unique()), sorted(df[col_b].unique())))
    observed = set(zip(df[col_a], df[col_b]))
    return sorted(expected - observed)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 250)

    df = load_and_prepare()
    # Snapshot des valeurs sources pour le controle "aucune valeur originale modifiee".
    original_snapshot = df[ORIGINAL_COLS].copy()

    print_section("A. VUE D'ENSEMBLE")
    n_rows, n_cols = df.shape
    overview = pd.DataFrame(
        [
            ("n_campagnes", n_rows),
            ("n_colonnes", n_cols),
            ("date_min", df["campaign_date"].min()),
            ("date_max", df["campaign_date"].max()),
            ("n_company", df["company"].nunique()),
            ("n_campaign_type", df["campaign_type"].nunique()),
            ("n_channel_used", df["channel_used"].nunique()),
            ("n_location", df["location"].nunique()),
            ("n_customer_segment", df["customer_segment"].nunique()),
            ("n_target_audience", df["target_audience"].nunique()),
        ],
        columns=["indicateur", "valeur"],
    )
    print(overview.to_string(index=False))

    print_section("B. KPI GLOBAUX")
    kpi_specs = [
        ("roi", True, False),
        ("acquisition_cost", True, True),
        ("conversion_rate", True, False),
        ("ctr_percent", True, False),
        ("clicks", False, False),
        ("impressions", False, False),
        ("engagement_score", False, False),
        ("duration_days", False, False),
    ]
    kpi_rows = []
    for col, with_std, with_sum in kpi_specs:
        s = df[col]
        row = {
            "variable": col,
            "moyenne": s.mean(),
            "mediane": s.median(),
            "minimum": s.min(),
            "maximum": s.max(),
            "ecart_type": s.std(ddof=1) if with_std else np.nan,
            "total": s.sum() if with_sum else np.nan,
        }
        kpi_rows.append(row)
    kpi_tbl = pd.DataFrame(kpi_rows)
    print(fmt_table(kpi_tbl))

    print_section("C. ANALYSE PAR COMPANY")
    by_company = group_kpis(df, "company", extra=["duration_days"]).sort_values("company")
    print(fmt_table(by_company))
    print(f"somme n_campagnes = {int(by_company['n_campagnes'].sum())}")
    print("Comparaison descriptive uniquement : aucun classement 'meilleure entreprise'.")

    print_section("D. ANALYSE PAR CAMPAIGN_TYPE")
    by_type = group_kpis(df, "campaign_type").sort_values("campaign_type")
    print(fmt_table(by_type))
    print(f"somme n_campagnes = {int(by_type['n_campagnes'].sum())}")

    print_section("E. ANALYSE PAR CHANNEL_USED")
    by_channel = group_kpis(df, "channel_used", extra=["clicks", "impressions"]).sort_values(
        "channel_used"
    )
    print(fmt_table(by_channel))
    print(f"somme n_campagnes = {int(by_channel['n_campagnes'].sum())}")

    print_section("F. ANALYSE PAR TARGET_AUDIENCE")
    by_aud = group_kpis(df, "target_audience").sort_values("target_audience")
    print(fmt_table(by_aud))
    print(f"somme n_campagnes = {int(by_aud['n_campagnes'].sum())}")

    print_section("G. ANALYSE PAR CUSTOMER_SEGMENT")
    by_seg = group_kpis(df, "customer_segment").sort_values("customer_segment")
    print(fmt_table(by_seg))
    print(f"somme n_campagnes = {int(by_seg['n_campagnes'].sum())}")

    print_section("H. ANALYSE PAR LOCATION")
    by_loc = group_kpis(df, "location").sort_values("location")
    print(fmt_table(by_loc))
    print(f"somme n_campagnes = {int(by_loc['n_campagnes'].sum())}")

    print_section("I. ANALYSE TEMPORELLE")
    monthly = (
        df.groupby(["year", "month", "month_name"], dropna=False)
        .agg(
            n_campagnes=("campaign_id", "count"),
            roi_moyen=("roi", "mean"),
            cout_moyen=("acquisition_cost", "mean"),
            conversion_moyenne=("conversion_rate", "mean"),
            ctr_moyen_pct=("ctr_percent", "mean"),
            engagement_moyen=("engagement_score", "mean"),
            n_jours=("campaign_date", lambda s: int(s.dt.days_in_month.iloc[0])),
        )
        .reset_index()
        .sort_values(["year", "month"])
    )
    monthly["campagnes_par_jour"] = monthly["n_campagnes"] / monthly["n_jours"]
    print("Par mois (n_jours = longueur du mois civil, pas une tendance) :")
    print(fmt_table(monthly))
    print(f"somme n_campagnes mois = {int(monthly['n_campagnes'].sum())}")

    quarterly = (
        df.groupby("quarter", dropna=False)
        .agg(
            n_campagnes=("campaign_id", "count"),
            roi_moyen=("roi", "mean"),
            cout_moyen=("acquisition_cost", "mean"),
            conversion_moyenne=("conversion_rate", "mean"),
            ctr_moyen_pct=("ctr_percent", "mean"),
        )
        .reset_index()
        .sort_values("quarter")
    )
    print()
    print("Par trimestre :")
    print(fmt_table(quarterly))
    print(f"somme n_campagnes trimestres = {int(quarterly['n_campagnes'].sum())}")

    print_section("J. ANALYSE DE DURATION")
    by_dur = group_kpis(df, "duration_days").sort_values("duration_days")
    print(fmt_table(by_dur))
    print(f"somme n_campagnes = {int(by_dur['n_campagnes'].sum())}")

    print_section("K. ANALYSE ROI (classes)")
    # Classes calculees en serie, sans ecraser roi.
    roi_class = pd.cut(
        df["roi"],
        bins=[-np.inf, 4, 6, np.inf],
        labels=["Faible", "Moyen", "Eleve"],
        right=False,
    )
    # right=False : Faible ROI<4, Moyen 4<=ROI<6, Eleve ROI>=6
    roi_cls = (
        df.assign(roi_class=roi_class)
        .groupby("roi_class", observed=True)
        .agg(
            n_campagnes=("campaign_id", "count"),
            roi_moyen=("roi", "mean"),
            cout_moyen=("acquisition_cost", "mean"),
            conversion_moyenne=("conversion_rate", "mean"),
            ctr_moyen_pct=("ctr_percent", "mean"),
            engagement_moyen=("engagement_score", "mean"),
        )
        .reset_index()
    )
    roi_cls["proportion_pct"] = roi_cls["n_campagnes"] / EXPECTED_N * 100
    roi_cls = roi_cls[
        [
            "roi_class",
            "n_campagnes",
            "proportion_pct",
            "roi_moyen",
            "cout_moyen",
            "conversion_moyenne",
            "ctr_moyen_pct",
            "engagement_moyen",
        ]
    ]
    print(fmt_table(roi_cls))
    print(f"somme n_campagnes = {int(roi_cls['n_campagnes'].sum())}")

    print_section("L. RELATIONS NUMERIQUES (Pearson)")
    corr = df[CORR_COLS].corr(method="pearson")
    print("Matrice de correlation Pearson :")
    print(corr.to_string(float_format=lambda x: f"{x:8.4f}"))
    pairs = []
    cols = list(corr.columns)
    for i, a in enumerate(cols):
        for b in cols[i + 1 :]:
            r = float(corr.loc[a, b])
            pairs.append((a, b, r, abs(r)))
    pairs.sort(key=lambda x: x[3], reverse=True)
    print()
    print("Grille |r| : <0.10 negligeable ; 0.10-0.30 faible ; 0.30-0.50 moderee ;")
    print("0.50-0.70 notable ; 0.70-0.90 forte ; >=0.90 tres forte.")
    print("Une correlation n'est pas une causalite.")
    print()
    print("Paires |r| >= 0.10 (sinon: toutes les paires restent negligeables) :")
    important = [p for p in pairs if p[3] >= 0.10]
    if not important:
        print("Aucune paire avec |r| >= 0.10.")
    else:
        for a, b, r, ar in important:
            sens = "positive" if r > 0 else "negative"
            print(f"  {a} vs {b} : r={r:.4f}  sens={sens}  intensite={intensity(ar)}")
    print()
    print("Top 5 |r| (hors diagonale), a titre descriptif :")
    for a, b, r, ar in pairs[:5]:
        sens = "positive" if r > 0 else "negative"
        print(f"  {a} vs {b} : r={r:.4f}  sens={sens}  intensite={intensity(ar)}")

    print_section("M. ANALYSE CTR")
    ctr = df["ctr_percent"]
    ctr_stats = pd.DataFrame(
        [
            ("moyenne", ctr.mean()),
            ("mediane", ctr.median()),
            ("P25", ctr.quantile(0.25)),
            ("P75", ctr.quantile(0.75)),
            ("minimum", ctr.min()),
            ("maximum", ctr.max()),
            ("ecart_type", ctr.std(ddof=1)),
        ],
        columns=["statistique", "valeur"],
    )
    print(fmt_table(ctr_stats))
    ctr_class = pd.cut(
        df["ctr_percent"],
        bins=[-np.inf, 5, 15, np.inf],
        labels=["Faible", "Moyen", "Eleve"],
        right=False,
    )
    ctr_cls = (
        df.assign(ctr_class=ctr_class)
        .groupby("ctr_class", observed=True)
        .agg(
            n_campagnes=("campaign_id", "count"),
            roi_moyen=("roi", "mean"),
            conversion_moyenne=("conversion_rate", "mean"),
            engagement_moyen=("engagement_score", "mean"),
        )
        .reset_index()
    )
    ctr_cls["proportion_pct"] = ctr_cls["n_campagnes"] / EXPECTED_N * 100
    print()
    print("Classes CTR (<5, 5 a <15, >=15) :")
    print(fmt_table(ctr_cls))
    print(f"somme n_campagnes = {int(ctr_cls['n_campagnes'].sum())}")

    print_section("N. ANALYSE CONVERSION_RATE")
    cr = df["conversion_rate"]
    cr_stats = pd.DataFrame(
        [
            ("moyenne", cr.mean()),
            ("mediane", cr.median()),
            ("P25", cr.quantile(0.25)),
            ("P75", cr.quantile(0.75)),
            ("minimum", cr.min()),
            ("maximum", cr.max()),
            ("ecart_type", cr.std(ddof=1)),
            ("n_valeurs_distinctes", cr.nunique()),
        ],
        columns=["statistique", "valeur"],
    )
    print(fmt_table(cr_stats))
    by_cr = (
        df.groupby("conversion_rate", dropna=False)
        .agg(n_campagnes=("campaign_id", "count"), roi_moyen=("roi", "mean"))
        .reset_index()
        .sort_values("conversion_rate")
    )
    print()
    print("ROI moyen par valeur de conversion_rate :")
    print(fmt_table(by_cr))
    print(f"somme n_campagnes = {int(by_cr['n_campagnes'].sum())}")

    print_section("O. ANALYSE ENGAGEMENT")
    by_eng = (
        df.groupby("engagement_score", dropna=False)
        .agg(
            n_campagnes=("campaign_id", "count"),
            roi_moyen=("roi", "mean"),
            conversion_moyenne=("conversion_rate", "mean"),
            ctr_moyen_pct=("ctr_percent", "mean"),
        )
        .reset_index()
        .sort_values("engagement_score")
    )
    by_eng["proportion_pct"] = by_eng["n_campagnes"] / EXPECTED_N * 100
    print(fmt_table(by_eng))
    print(f"somme n_campagnes = {int(by_eng['n_campagnes'].sum())}")

    print_section("P. ANALYSES CROISEES")
    print("P1. Company x Channel_Used")
    p1 = (
        df.groupby(["company", "channel_used"], dropna=False)
        .agg(n_campagnes=("campaign_id", "count"), roi_moyen=("roi", "mean"))
        .reset_index()
        .sort_values(["company", "channel_used"])
    )
    print(fmt_table(p1))
    miss1 = missing_combos(df, "company", "channel_used")
    print(
        f"combinaisons observees = {len(p1)} ; "
        f"attendues = {df['company'].nunique() * df['channel_used'].nunique()} ; "
        f"absentes = {miss1 if miss1 else 'aucune'}"
    )
    print(f"somme n_campagnes = {int(p1['n_campagnes'].sum())}")

    print()
    print("P2. Campaign_Type x Channel_Used")
    p2 = (
        df.groupby(["campaign_type", "channel_used"], dropna=False)
        .agg(n_campagnes=("campaign_id", "count"), roi_moyen=("roi", "mean"))
        .reset_index()
        .sort_values(["campaign_type", "channel_used"])
    )
    print(fmt_table(p2))
    miss2 = missing_combos(df, "campaign_type", "channel_used")
    print(
        f"combinaisons observees = {len(p2)} ; "
        f"attendues = {df['campaign_type'].nunique() * df['channel_used'].nunique()} ; "
        f"absentes = {miss2 if miss2 else 'aucune'}"
    )
    print(f"somme n_campagnes = {int(p2['n_campagnes'].sum())}")

    print()
    print("P3. Target_Audience x Customer_Segment")
    p3 = (
        df.groupby(["target_audience", "customer_segment"], dropna=False)
        .agg(
            n_campagnes=("campaign_id", "count"),
            roi_moyen=("roi", "mean"),
            ctr_moyen_pct=("ctr_percent", "mean"),
        )
        .reset_index()
        .sort_values(["target_audience", "customer_segment"])
    )
    print(fmt_table(p3))
    miss3 = missing_combos(df, "target_audience", "customer_segment")
    print(
        f"combinaisons observees = {len(p3)} ; "
        f"attendues = {df['target_audience'].nunique() * df['customer_segment'].nunique()} ; "
        f"absentes = {miss3 if miss3 else 'aucune'}"
    )
    print(f"somme n_campagnes = {int(p3['n_campagnes'].sum())}")

    print()
    print("P4. Engagement_Score x ROI (ROI moyen par score)")
    print(fmt_table(by_eng[["engagement_score", "n_campagnes", "roi_moyen"]]))

    print()
    print("P5. Conversion_Rate x ROI")
    print(fmt_table(by_cr))

    print()
    print("P6. CTR x ROI (ROI moyen par classe de CTR)")
    print(fmt_table(ctr_cls[["ctr_class", "n_campagnes", "proportion_pct", "roi_moyen"]]))

    print_section("Q. EQUILIBRE DES CATEGORIES")
    imbalance_notes = []
    for col in CATEGORICAL_COLS:
        vc = df[col].value_counts(dropna=False)
        dist = vc.rename_axis("valeur").reset_index(name="nombre")
        dist["proportion_pct"] = dist["nombre"] / EXPECTED_N * 100
        print()
        print(f"--- {col} ---")
        print(fmt_table(dist))
        print(f"somme = {int(dist['nombre'].sum())}")
        pmin, pmax = dist["proportion_pct"].min(), dist["proportion_pct"].max()
        # Seuil descriptif : dominante > 40 % ou minoritaire < 5 %.
        if pmax >= 40:
            imbalance_notes.append(f"{col}: modalite dominante ({pmax:.2f} %)")
        if pmin < 5:
            imbalance_notes.append(f"{col}: modalite minoritaire ({pmin:.2f} %)")
        else:
            imbalance_notes.append(
                f"{col}: ecart max-min = {pmax - pmin:.2f} points (min {pmin:.2f} %, max {pmax:.2f} %)"
            )
    print()
    print("Lecture des equilibres :")
    for note in imbalance_notes:
        print(" -", note)

    print_section("R. CONTROLES POST-EDA")
    inf_count = int(np.isinf(df.select_dtypes(include=[np.number])).sum().sum())
    nan_count = int(df.isna().sum().sum())
    originals_present = all(c in df.columns for c in ORIGINAL_COLS)
    originals_unchanged = original_snapshot.equals(df[ORIGINAL_COLS])
    id_unique = bool(df["campaign_id"].is_unique)
    date_ok = bool(
        (df["campaign_date"].min() >= pd.Timestamp("2021-01-01"))
        and (df["campaign_date"].max() <= pd.Timestamp("2021-12-31"))
    )
    ctr_ok = bool(
        np.allclose(
            df["ctr"],
            np.where(df["impressions"] == 0, np.nan, df["clicks"] / df["impressions"]),
            equal_nan=True,
        )
        and np.allclose(df["ctr_percent"], df["ctr"] * 100, equal_nan=True)
    )
    checks = [
        ("n_lignes == 200005", n_rows == EXPECTED_N, n_rows),
        ("colonnes originales presentes", originals_present, None),
        ("valeurs originales inchangees", originals_unchanged, None),
        ("NaN totaux", nan_count == 0, nan_count),
        ("valeurs infinies", inf_count == 0, inf_count),
        ("campaign_id unique", id_unique, None),
        ("dates dans 2021-01-01 .. 2021-12-31", date_ok, None),
        ("ctr coherent clicks/impressions", ctr_ok, None),
    ]
    n_fail = 0
    print(f"{'controle':<42} | resultat")
    for label, ok, detail in checks:
        extra = f" ({detail})" if detail is not None else ""
        print(f"{label:<42} | {'OK' if ok else 'ECHEC'}{extra}")
        if not ok:
            n_fail += 1

    print_section("S. PRINCIPAUX CONSTATS DE L'EDA")
    roi_range_cat = (
        by_company["roi_moyen"].max() - by_company["roi_moyen"].min(),
        by_type["roi_moyen"].max() - by_type["roi_moyen"].min(),
        by_channel["roi_moyen"].max() - by_channel["roi_moyen"].min(),
        by_aud["roi_moyen"].max() - by_aud["roi_moyen"].min(),
        by_seg["roi_moyen"].max() - by_seg["roi_moyen"].min(),
        by_loc["roi_moyen"].max() - by_loc["roi_moyen"].min(),
        by_dur["roi_moyen"].max() - by_dur["roi_moyen"].min(),
        monthly["roi_moyen"].max() - monthly["roi_moyen"].min(),
    )
    print("Niveaux globaux des KPI")
    print(
        f"- n={n_rows} campagnes, {n_cols} colonnes, periode "
        f"{df['campaign_date'].min().date()} -> {df['campaign_date'].max().date()}."
    )
    print(
        f"- ROI moyen={df['roi'].mean():.4f}, mediane={df['roi'].median():.4f}, "
        f"min={df['roi'].min():.2f}, max={df['roi'].max():.2f}, std={df['roi'].std():.4f}."
    )
    print(
        f"- Cout moyen={df['acquisition_cost'].mean():.2f}, "
        f"total={df['acquisition_cost'].sum():.2f}."
    )
    print(
        f"- Conversion moyenne={df['conversion_rate'].mean():.4f} ; "
        f"CTR moyen (par campagne)={df['ctr_percent'].mean():.4f} % ; "
        f"CTR median={df['ctr_percent'].median():.4f} % ; "
        f"engagement moyen={df['engagement_score'].mean():.2f} ; "
        f"duree moyenne={df['duration_days'].mean():.2f} jours."
    )
    print()
    print("Ecarts entre categories")
    print(
        f"- Ecart de ROI moyen (max-min) : company {roi_range_cat[0]:.4f} ; "
        f"type {roi_range_cat[1]:.4f} ; canal {roi_range_cat[2]:.4f} ; "
        f"audience {roi_range_cat[3]:.4f} ; segment {roi_range_cat[4]:.4f} ; "
        f"location {roi_range_cat[5]:.4f} ; duree {roi_range_cat[6]:.4f}."
    )
    print("- Volumes par company/type/audience/segment/location proches de 20 % chacun.")
    print("- Canaux proches de 16-17 % chacun. Durees proches de 25 % chacune.")
    print()
    print("Relations numeriques")
    if important:
        for a, b, r, ar in important:
            print(
                f"- Correlation observee {a} vs {b} : r={r:.4f} "
                f"({('positive' if r > 0 else 'negative')}, {intensity(ar)}). "
                "Ce n'est pas une causalite."
            )
    else:
        print("- Aucune paire du panier KPI avec |r| >= 0.10 (relations negligeables).")
    print(
        f"- Top |r| hors diagonale : {pairs[0][0]} vs {pairs[0][1]} r={pairs[0][2]:.4f} "
        f"({intensity(pairs[0][3])})."
    )
    print()
    print("Temps")
    print(
        f"- 12 mois en 2021. Volume min={int(monthly['n_campagnes'].min())} "
        f"({monthly.loc[monthly['n_campagnes'].idxmin(), 'month_name']}), "
        f"max={int(monthly['n_campagnes'].max())} "
        f"({monthly.loc[monthly['n_campagnes'].idxmax(), 'month_name']})."
    )
    print(
        f"- ROI mensuel min={monthly['roi_moyen'].min():.4f} "
        f"({monthly.loc[monthly['roi_moyen'].idxmin(), 'month_name']}), "
        f"max={monthly['roi_moyen'].max():.4f} "
        f"({monthly.loc[monthly['roi_moyen'].idxmax(), 'month_name']}), "
        f"ecart={roi_range_cat[7]:.4f}."
    )
    print(
        "- Les volumes mensuels doivent etre lus avec n_jours "
        "(fevrier a 28 jours en 2021)."
    )
    print()
    print("Equilibres / anomalies")
    print(f"- Combinaisons company x canal absentes : {miss1 if miss1 else 'aucune'}.")
    print(f"- Combinaisons type x canal absentes : {miss2 if miss2 else 'aucune'}.")
    print(f"- Combinaisons audience x segment absentes : {miss3 if miss3 else 'aucune'}.")
    print(f"- Controles post-EDA en echec : {n_fail}.")
    print("- Aucune categorie < 5 % ni > 40 % sur les variables Q.")
    print()
    print("Visualisations a considerer a l'etape suivante (non realisees ici)")
    print("- Barres de volume par categorie (company, canal, type, audience, segment, location).")
    print("- Series mensuelles : n_campagnes et n_campagnes/jour, ROI moyen.")
    print("- Histogrammes ROI, CTR, conversion_rate, acquisition_cost.")
    print("- Heatmap de la matrice de correlation Pearson.")
    print("- Heatmaps des tableaux croises (ROI moyen company x canal, type x canal).")
    print("- Boxplots ROI/CTR par classe ROI et par classe CTR.")

    analyses = [
        "A vue d'ensemble",
        "B KPI globaux",
        "C company",
        "D campaign_type",
        "E channel_used",
        "F target_audience",
        "G customer_segment",
        "H location",
        "I temporel mois/trimestre",
        "J duration",
        "K classes ROI",
        "L correlations Pearson",
        "M CTR",
        "N conversion_rate",
        "O engagement",
        "P croisements",
        "Q equilibres",
        "R controles post-EDA",
        "S synthese",
    ]
    print()
    print("EDA TERMINEE")
    print(f"- lignes analysees : {n_rows}")
    print(f"- colonnes analysees : {n_cols}")
    print(f"- analyses realisees : {len(analyses)} ({', '.join(analyses)})")
    print(f"- controles post-EDA : {'OK' if n_fail == 0 else 'ECHEC'}")
    print(f"- anomalies detectees : {n_fail}")
    print(
        "- graphiques recommandes pour l'etape suivante : "
        "volumes par categorie, series mensuelles, histogrammes KPI, "
        "heatmap correlations, heatmaps croisees, boxplots classes ROI/CTR"
    )
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
