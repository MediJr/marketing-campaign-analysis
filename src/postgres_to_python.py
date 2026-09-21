"""Extraction PostgreSQL -> Pandas (lecture seule, inspection uniquement)."""

from __future__ import annotations

import getpass
import sys
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text

HOST = "127.0.0.1"
PORT = 5432
USER = "data_project"
DATABASE = "marketing_analysis"
TABLE = "public.marketing_campaigns"
EXPECTED_SHAPE = (200005, 15)

SQL = """
SELECT *
FROM public.marketing_campaigns
ORDER BY campaign_id
"""


def fmt_bool(ok: bool) -> str:
    return "OK" if ok else "ECHEC"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 40)

    password = getpass.getpass("Mot de passe data_project: ")
    url = (
        f"postgresql+psycopg2://{USER}:{quote_plus(password)}"
        f"@{HOST}:{PORT}/{DATABASE}"
    )
    engine = create_engine(url)

    try:
        with engine.connect() as conn:
            info = conn.execute(
                text("SELECT current_database() AS db, current_user AS usr")
            ).mappings().one()
            db_name = info["db"]
            pg_user = info["usr"]

        print()
        print("A. Connexion")
        print("------------")
        print("Connexion : reussie")
        print(f"Base      : {db_name}")
        print(f"Utilisateur PostgreSQL : {pg_user}")
        print()

        df = pd.read_sql(text(SQL), engine)

        n_rows, n_cols = df.shape
        print("B. Structure du resultat")
        print("------------------------")
        print(f"Nombre de lignes   : {n_rows}")
        print(f"Nombre de colonnes : {n_cols}")
        print("Liste des colonnes :")
        for col in df.columns.tolist():
            print(f"  - {col}")
        print()

        print("C. Types Pandas")
        print("---------------")
        print(df.dtypes.to_string())
        print()

        print("D. Apercu (5 premieres lignes)")
        print("------------------------------")
        print(df.head(5).to_string(index=False))
        print()

        print("E. Fin du DataFrame (5 dernieres lignes)")
        print("----------------------------------------")
        print(df.tail(5).to_string(index=False))
        print()

        mem_bytes = int(df.memory_usage(deep=True).sum())
        mem_mb = mem_bytes / (1024 * 1024)
        print("F. Memoire")
        print("----------")
        print(f"memory_usage(deep=True).sum() : {mem_bytes} octets")
        print(f"Taille                        : {mem_mb:.2f} MB")
        print()

        print("G. Controles")
        print("------------")
        shape_ok = df.shape == EXPECTED_SHAPE
        id_unique = bool(df["campaign_id"].is_unique)
        id_min = int(df["campaign_id"].min())
        id_max = int(df["campaign_id"].max())
        id_min_ok = id_min == 1
        id_max_ok = id_max == EXPECTED_SHAPE[0]
        nulls = df.isna().sum()
        all_empty = [col for col in df.columns if int(nulls[col]) == n_rows]
        unexpected_nulls = {col: int(nulls[col]) for col in df.columns if int(nulls[col]) > 0}
        nulls_ok = len(all_empty) == 0 and len(unexpected_nulls) == 0

        print(f"shape == {EXPECTED_SHAPE} : {fmt_bool(shape_ok)}  (observe : {df.shape})")
        print(f"campaign_id unique        : {fmt_bool(id_unique)}")
        print(f"campaign_id min = 1       : {fmt_bool(id_min_ok)}  (observe : {id_min})")
        print(f"campaign_id max = 200005  : {fmt_bool(id_max_ok)}  (observe : {id_max})")
        print(
            "colonne entierement vide  : "
            + ("aucune" if not all_empty else ", ".join(all_empty))
        )
        if unexpected_nulls:
            print("NULL inattendus           :")
            for col, n in unexpected_nulls.items():
                print(f"  - {col}: {n}")
        else:
            print("NULL inattendus           : aucun (0 NULL sur toutes les colonnes)")
        print()

        print("Extraction PostgreSQL -> Python")
        print("------------------------------")
        print("Statut connexion : reussie")
        print(f"Base : {db_name}")
        print(f"Table : {TABLE}")
        print(f"Lignes : {n_rows}")
        print(f"Colonnes : {n_cols}")
        print(f"DataFrame cree : {'oui' if n_rows > 0 else 'non'}")
        print(f"Types verifies : {fmt_bool(n_cols == EXPECTED_SHAPE[1])}")
        print(
            "Identifiants verifies : "
            + fmt_bool(id_unique and id_min_ok and id_max_ok)
        )
        print(f"NULL verifies : {fmt_bool(nulls_ok)}")
        return 0 if shape_ok and id_unique and id_min_ok and id_max_ok and nulls_ok else 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
