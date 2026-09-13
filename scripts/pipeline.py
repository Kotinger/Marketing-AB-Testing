from pathlib import Path
import pandas as pd
from math import erfc, sqrt

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "marketing_AB.csv"
#
USER_COL = "user id"
GROUP_COL = "test group"  # "ad"/"psa"
OUTCOME_COLS = ["converted"]
GUARDRAIL_COLS = ["total ads"]

CONTROL = "psa"  # контроль
TREATMENT = "ad"  # тест


def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    #print("columns", df.columns.to_list())
    #print(df.head(3))
    #print("shape", df.shape)
    #print("isna", df.isna().sum())
    #print("dtypes", df.dtypes)
    return df


def check_grain(df: pd.DataFrame) -> str:
    rows = len(df)
    users = df[USER_COL].nunique()
    if rows > users * 1.2:
        grain = "event"
    else:
        grain = "user"
    print("rows", rows, "users", users, "grain->", grain)
    # rows 588101 users 588101 grain-> user
    return grain


def prepare_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[USER_COL] = df[USER_COL].astype(str).str.strip()
    df[GROUP_COL] = df[GROUP_COL].astype(str).str.strip()
    for c in OUTCOME_COLS:
        df[c] = df[c].astype(int)
    for c in GUARDRAIL_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def build_clean(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.copy()
    # тут в отличие от классики ecom важно проверить:
    # 1 может ли один юзер быть сразу в двух группах
    # 2 может ли юзер встретиться дважды
    clean = clean.drop(columns=[c for c in clean.columns if str(c).startswith("Unnamed")], errors="ignore")
    chek_users = clean.groupby(USER_COL)[GROUP_COL].nunique()
    print("user >1 group =  ", int((chek_users > 1).sum()))
    print("dup id =", int(clean[USER_COL].duplicated().sum()))
    clean = clean[clean[GROUP_COL].isin([CONTROL, TREATMENT])]
    clean = clean.dropna(subset=[USER_COL, GROUP_COL] + OUTCOME_COLS)
    clean = clean.drop_duplicates(subset=[USER_COL], keep="first")
    print("groups", clean[GROUP_COL].value_counts().to_dict())
    print("outcome", clean[OUTCOME_COLS[0]].mean())
    return clean


def srm_check(clean: pd.DataFrame) -> None:
    # в описании датасета majority = ads, small portion = psa → 4% / 96%
    n = len(clean)
    n_c = int((clean[GROUP_COL] == CONTROL).sum())
    n_t = int((clean[GROUP_COL] == TREATMENT).sum())
    exp_c, exp_t = n * 0.04, n * 0.96
    chi2 = (n_c - exp_c) ** 2 / exp_c + (n_t - exp_t) ** 2 / exp_t
    p = erfc(sqrt(chi2 / 2))
    print(n, CONTROL, n_c, f"{100 * n_c / n:.2f}%", TREATMENT, n_t, f"{100 * n_t / n:.2f}%")
    print("chi2", round(chi2, 4), "p", round(p, 4))


def sanity_check(raw: pd.DataFrame, clean: pd.DataFrame) -> None:
    print("---sanity---")
    print("rows", len(raw), "clean rows->", len(clean))


def add_key(clean: pd.DataFrame) -> pd.DataFrame:
    assert clean[USER_COL].nunique() == len(clean)
    print("keys=rows", len(clean))
    return clean


def save_tables(clean: pd.DataFrame) -> None:
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    clean.to_parquet(out / "clean.parquet", index=False)
    back = pd.read_parquet(out / "clean.parquet")
    print("save", len(back))


def main() -> None:
    raw = load_data(RAW_PATH)
    check_grain(raw)
    dtype = prepare_types(raw)
    clean = build_clean(dtype)
    srm_check(clean)
    sanity_check(raw, clean)
    add_key(clean)
    save_tables(clean)


if __name__ == "__main__":
    main()
