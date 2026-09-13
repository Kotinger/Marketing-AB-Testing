from pathlib import Path
import os
import pandas as pd
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "processed"

DB_USER = os.getenv("MYSQL_USER", "root")
DB_HOST = os.getenv("MYSQL_HOST", "localhost")
DB_NAME = os.getenv("MYSQL_DATABASE", "marketing_ab")

RENAME = {
    "user id": "user_id",
    "test group": "test_group",
    "converted": "converted",
    "total ads": "total_ads",
    "most ads day": "most_ads_day",
    "most ads hour": "most_ads_hour",
}


def read_password() -> str:
    # сначала env, потом pass.txt
    if os.environ.get("MYSQL_PASSWORD"):
        return os.environ["MYSQL_PASSWORD"].strip()
    p = ROOT / "pass.txt"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                return line.strip()
    raise SystemExit("нет пароля: MYSQL_PASSWORD или pass.txt")


def main() -> None:
    engine = create_engine(
        f"mysql+pymysql://{DB_USER}:{read_password()}@{DB_HOST}/{DB_NAME}"
    )
    clean = pd.read_parquet(OUT_DIR / "clean.parquet")
    clean = clean.rename(columns=RENAME)

    with engine.begin() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`"))
        conn.execute(text(f"USE `{DB_NAME}`"))
    clean.to_sql("clean_users", engine, if_exists="replace", index=False, chunksize=5000)
    print("clean_users", len(clean))


if __name__ == "__main__":
    main()
