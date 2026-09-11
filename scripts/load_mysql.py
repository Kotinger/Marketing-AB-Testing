from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT/"data"/"processed"

CLEAN_RENAME = {
    "user id": "user_id",
    "test group": "test_group",
    "converted": "converted",
    "total ads": "total_ads",
    "most ads day": "most_ads_day",
    "most ads hour": "most_ads_hour",
}

DB_USER = os.getenv("MYSQL_USER", "root")
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_NAME = os.getenv("MYSQL_DATABASE", "marketing_ab")


def read_password() -> str:
    env = os.environ.get("MYSQL_PASSWORD")
    if env:
        return env.strip()
    pass_file = ROOT/"pass.txt"
    if pass_file.exists():
        for line in pass_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                return line
    raise SystemExit("Нет пароля: MYSQL_PASSWORD или pass.txt")


def main() -> None:
    url = f"mysql+pymysql://{DB_USER}:{read_password()}@{DB_HOST}/{DB_NAME}"
    engine = create_engine(url)

    clean = pd.read_parquet(OUT_DIR/"clean.parquet")
    missing = [c for c in CLEAN_RENAME if c not in clean.columns]
    if missing:
        raise SystemExit(f"В clean.parquet нет колонок: {missing}")

    clean = clean[list(CLEAN_RENAME.keys())].rename(columns=CLEAN_RENAME)

    with engine.begin() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"))
        conn.execute(text(f"USE `{DB_NAME}`"))

    clean.to_sql("clean_users", engine, if_exists="replace", index=False, chunksize=5000)
    print("clean_users", len(clean))


if __name__ == "__main__":
    main()
