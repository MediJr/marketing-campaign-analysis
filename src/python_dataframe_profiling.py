"""Profilage et preparation du DataFrame (Python/Pandas, PostgreSQL en lecture seule)."""

from __future__ import annotations

import getpass
import io
import sys
from urllib.parse import quote_plus

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text

HOST = "127.0.0.1"
PORT = 5432
USER = "data_project"
DATABASE = "marketing_analysis"
EXPECTED_EXTRACT_SHAPE = (200005, 15)
PREVIOUS_MEMORY_BYTES = 42_848_679

SQL = """
SELECT *
FROM public.marketing_campaigns
ORDER BY campaign_id
"""

CATEGORICAL_COLS = [
    "company",
    "campaign_type",
    "target_audience",
    "channel_used",
    "location",
    "customer_segment",
]

NUMERIC_COLS = [
    "duration_days",
    "conversion_rate",
    "acquisition_cost",
    "roi",
    "clicks",
    "impressions",
    "engagement_score",
]

FREQ_COLS = CATEGORICAL_COLS + ["duration_days"]


def fmt_ok(ok: bool) -> str:
    return "OK" if ok else "ANOMALIE"


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def numeric_profile(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    rows = []
    for col in columns:
        s = pd.to_numeric(frame[col], errors="coerce")
        rows.append(
            {
                "Variable": col,
                "Count": int(s.count()),
                "Mean": s.mean(),
                "Median": s.median(),
                "Std": s.std(ddof=1),
                "Min": s.min(),
                "P25": s.quantile(0.25),
                "P75": s.quantile(0.75),
                "Max": s.max(),
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_rows", 200)
    pd.set_option("display.float_format", lambda x: f"{x:.6f}".rstrip("0").rstrip("."))

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

    print_section("1. CHARGEMENT")
    print("PostgreSQL : lecture seule, SELECT * ORDER BY campaign_id")
    print(f"DataFrame cree : oui  shape={df.shape}")

    print_section("2. PROFILAGE STRUCTUREL")
    print("df.shape :", df.shape)
    print("df.columns.tolist() :")
    print(df.columns.tolist())
    print()
    print("df.dtypes :")
    print(df.dtypes.to_string())
    print()
    print("df.info() :")
    buf = io.StringIO()
    df.info(buf=buf)
    print(buf.getvalue().rstrip())
    shape_ok = df.shape == EXPECTED_EXTRACT_SHAPE
    print()
    print(f"Verification df.shape == (200005, 15) : {fmt_ok(shape_ok)}")

    print_section("3. VALEURS MANQUANTES")
    n = len(df)
    null_count = df.isna().sum()
    missing = pd.DataFrame(
        {
            "column": df.columns,
            "null_count": null_count.values,
            "null_percent": (null_count.values / n * 100).round(4),
        }
    )
    print(missing.to_string(index=False))
    missing_ok = int(null_count.sum()) == 0
    print()
    print(f"Aucune valeur manquante : {fmt_ok(missing_ok)}")

    print_section("4. DOUBLONS")
    n_dup_rows = int(df.duplicated().sum())
    n_dup_ids = int(df["campaign_id"].duplicated().sum())
    id_unique = bool(df["campaign_id"].is_unique)
    print(f"Lignes dupliquees (toutes colonnes) : {n_dup_rows}")
    print(f"campaign_id dupliques               : {n_dup_ids}")
    print(f'df["campaign_id"].is_unique         : {id_unique}')
    print("Aucune suppression effectuee.")

    print_section("5. CARDINALITE DES VARIABLES CATEGORIELLES")
    for col in CATEGORICAL_COLS:
        vc = df[col].value_counts(dropna=False)
        print()
        print(f"--- {col} ---")
        print(f"Modalites uniques : {df[col].nunique(dropna=False)}")
        print("Liste :", vc.index.tolist())
        freq = vc.rename_axis("valeur").reset_index(name="nombre")
        print(freq.to_string(index=False))

    print_section("6. VARIABLES NUMERIQUES")
    numeric_like = df.select_dtypes(include=["number"]).columns.tolist()
    print("Colonnes numeriques detectees :", numeric_like)
    print()
    print("df.describe() :")
    print(df[NUMERIC_COLS].describe(percentiles=[0.25, 0.5, 0.75]).to_string())
    print()
    num_tbl = numeric_profile(df, NUMERIC_COLS)
    print("Tableau lisible :")
    print(num_tbl.to_string(index=False))

    print_section("7. VARIABLES DATE")
    print("dtype avant conversion :", df["campaign_date"].dtype)
    df["campaign_date"] = pd.to_datetime(df["campaign_date"], errors="coerce")
    n_years = int(df["campaign_date"].dt.year.nunique(dropna=False))
    n_null_dates = int(df["campaign_date"].isna().sum())
    date_min = df["campaign_date"].min()
    date_max = df["campaign_date"].max()
    n_unique_dates = int(df["campaign_date"].nunique(dropna=False))
    print("dtype apres conversion :", df["campaign_date"].dtype)
    print("min :", date_min)
    print("max :", date_max)
    print("dates uniques :", n_unique_dates)
    print("nombre d'annees :", n_years)
    print("NULL apres conversion :", n_null_dates)

    df["year"] = df["campaign_date"].dt.year.astype("int64")
    df["month"] = df["campaign_date"].dt.month.astype("int64")
    df["month_name"] = df["campaign_date"].dt.month_name()
    df["quarter"] = "Q" + df["campaign_date"].dt.quarter.astype("int64").astype(str)
    print()
    print("Colonnes ajoutees (campaign_date conserve) : year, month, month_name, quarter")
    print("year dtype        :", df["year"].dtype)
    print("month dtype       :", df["month"].dtype)
    print("month_name dtype  :", df["month_name"].dtype)
    print("quarter dtype     :", df["quarter"].dtype)
    print("quarters observes :", sorted(df["quarter"].unique().tolist()))

    print_section("8. VARIABLES CALCULEES")
    impressions = pd.to_numeric(df["impressions"], errors="coerce")
    clicks = pd.to_numeric(df["clicks"], errors="coerce")
    df["ctr"] = np.where(impressions == 0, np.nan, clicks / impressions)
    df["ctr_percent"] = df["ctr"] * 100
    ctr = df["ctr"]
    n_inf = int(np.isinf(ctr).sum())
    n_null_ctr = int(pd.isna(ctr).sum())
    print("ctr = clicks / impressions  (NaN si impressions == 0)")
    print("ctr_percent = ctr * 100")
    print("clicks et impressions conserves.")
    print(f"valeurs infinies : {n_inf}")
    print(f"valeurs NULL     : {n_null_ctr}")
    print(f"min              : {ctr.min()}")
    print(f"mediane          : {ctr.median()}")
    print(f"moyenne          : {ctr.mean()}")
    print(f"max              : {ctr.max()}")

    print_section("9. CONTROLES METIER DE BASE")
    print(f"{'controle':<42} | {'resultat':<8} | nombre_anomalies")
    n_anom_total = 0
    n_min_ok = int(df["campaign_id"].min()) == 1
    n_max_ok = int(df["campaign_id"].max()) == 200005
    n_unique_ok = bool(df["campaign_id"].is_unique)
    rows_checks = [
        ("campaign_id min = 1", n_min_ok, 0 if n_min_ok else 1),
        ("campaign_id max = 200005", n_max_ok, 0 if n_max_ok else 1),
        ("campaign_id unique", n_unique_ok, int(df["campaign_id"].duplicated().sum())),
        ("clicks <= impressions", int((df["clicks"] > df["impressions"]).sum()) == 0, int((df["clicks"] > df["impressions"]).sum())),
        (
            "engagement_score entre 1 et 10",
            int(((df["engagement_score"] < 1) | (df["engagement_score"] > 10)).sum()) == 0,
            int(((df["engagement_score"] < 1) | (df["engagement_score"] > 10)).sum()),
        ),
        (
            "conversion_rate entre 0 et 1",
            int(((df["conversion_rate"] < 0) | (df["conversion_rate"] > 1)).sum()) == 0,
            int(((df["conversion_rate"] < 0) | (df["conversion_rate"] > 1)).sum()),
        ),
        ("acquisition_cost >= 0", int((df["acquisition_cost"] < 0).sum()) == 0, int((df["acquisition_cost"] < 0).sum())),
        ("roi >= 0", int((df["roi"] < 0).sum()) == 0, int((df["roi"] < 0).sum())),
        (
            "duration_days dans {15, 30, 45, 60}",
            int((~df["duration_days"].isin([15, 30, 45, 60])).sum()) == 0,
            int((~df["duration_days"].isin([15, 30, 45, 60])).sum()),
        ),
    ]
    for label, ok, n_anom in rows_checks:
        print(f"{label:<42} | {fmt_ok(ok):<8} | {n_anom}")
        n_anom_total += n_anom
    print("Aucune ligne modifiee.")

    print_section("10. DISTRIBUTION DES VARIABLES CATEGORIELLES")
    for col in FREQ_COLS:
        vc = df[col].value_counts(dropna=False)
        dist = vc.rename_axis("valeur").reset_index(name="nombre")
        dist["pourcentage"] = (dist["nombre"] / 200005 * 100).round(4)
        print()
        print(f"--- {col} ---")
        print(dist.to_string(index=False))
        print(f"somme nombre : {int(dist['nombre'].sum())}")

    print_section("11. STATISTIQUES DESCRIPTIVES")
    desc_cols = NUMERIC_COLS + ["ctr", "ctr_percent"]
    desc_tbl = numeric_profile(df, desc_cols)
    print(desc_tbl.to_string(index=False))

    print_section("12. MEMOIRE")
    mem_bytes = int(df.memory_usage(deep=True).sum())
    mem_mb = mem_bytes / (1024 * 1024)
    prev_mb = PREVIOUS_MEMORY_BYTES / (1024 * 1024)
    print(f"memory_usage(deep=True).sum() : {mem_bytes} octets")
    print(f"Taille actuelle               : {mem_mb:.2f} MB")
    print(f"Taille extraction precedente  : {prev_mb:.2f} MB")
    print(f"Ecart                         : {mem_mb - prev_mb:+.2f} MB")

    print_section("13. PREPARATION FINALE")
    print("Aucune ligne supprimee, aucune colonne source supprimee.")
    print("Pas de recodage numerique des categories, pas de standardisation.")
    print("shape final :", df.shape)
    print("dtypes finaux :")
    print(df.dtypes.to_string())

    print_section("14. PYTHON DATA PROFILING")
    print("PYTHON DATA PROFILING")
    print("---------------------")
    print(f"Shape : {df.shape}")
    print(f"Colonnes : {len(df.columns)}")
    print(f"Valeurs NULL : {int(df.isna().sum().sum())}")
    print(f"Doublons : {n_dup_rows}")
    print(f"Campaign_ID unique : {id_unique}")
    print(f"Date min : {date_min}")
    print(f"Date max : {date_max}")
    print(f"Dates uniques : {n_unique_dates}")
    print(f"CTR calcule : oui (infinis={n_inf}, NULL={n_null_ctr})")
    print(f"Anomalies metier : {n_anom_total}")
    print(f"Memoire DataFrame : {mem_mb:.2f} MB")
    print()
    print("DATAFRAME READY FOR ANALYSIS")
    print(f"shape final : {df.shape}")
    print("dtypes finaux :")
    print(df.dtypes.to_string())
    return 0 if shape_ok and missing_ok and id_unique and n_anom_total == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
