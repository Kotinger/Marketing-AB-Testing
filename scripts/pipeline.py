from pathlib import Path
import pandas as pd
from math import erfc, sqrt

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT/"data"/"marketing_AB.csv"


USER_COL = "user id"
GROUP_COL = "test group" # "ad"/"psa"
CONTROL = "psa"          # контроль
TREATMENT = "ad"         # тест
OUTCOME_COLS = ["converted"]   
GUARDRAIL_COLS = ["total ads"] 



def load_data(path: Path)-> pd.DataFrame:
    df = pd.read_csv(path)
    #df.columns=df.columns.str.strip()
    #print("colums", df.columns.to_list())
    #print("shape", df.shape)
    #print(df.head(3))
    #print(df.isna().sum())
    #print(df.dtypes)
    #print(df[GROUP_COL].value_counts())
    #print(df[OUTCOME_COLS[0]].value_counts)
    #print(df[GUARDRAIL_COLS[0]].describe())
    return df

def cheсk_grain(df: pd.DataFrame)->str:
    rows = len(df)
    users=df[USER_COL].nunique()
    if rows > users*1.2:
        grain="event" 
    else:
        grain = "user"
    print("rows", rows, "users", users, "grain -> ", grain)
    return grain

def prepare_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df[USER_COL]= df[USER_COL].astype(str).str.strip()
    df[GROUP_COL]= df[GROUP_COL].astype(str).str.strip()
    for c in OUTCOME_COLS:
        df[c] = df[c].astype(int)
    for c in GUARDRAIL_COLS:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    #print("groups", df[GROUP_COL].value_counts().to_dict())
    #print("converted mean", df["converted"].mean())
    return df

def build_clean(df: pd.DataFrame) -> pd.DataFrame:
    clean= df.copy()
    # тут в отичае от класики ecom важно проверить: 
    # 1 может ли один юзер быть сразу в двух группах 
    # 2 может ли юзер встретиться дважды, проще сразу зачистить без проверок
    chek_users= clean.groupby(USER_COL)[GROUP_COL].nunique()
    print("user >1 group =  ", int((chek_users>1).sum()))
    print("dup id =", clean[USER_COL].duplicated().sum())
    clean = clean[clean[GROUP_COL].isin([CONTROL, TREATMENT])]  # тоже самое clean = clean[clean[GROUP_COL].isin(["psa", "ad"])] 
    clean = clean.dropna(subset=[USER_COL, GROUP_COL] + OUTCOME_COLS)
    #print("clean", len(clean))
    return clean

def expected_shares(n_control: int, n_treatment: int) -> tuple[float, float]:
    #в описание датасета majority = ads, small portion = psa.
    # исходя из результата srm будет 4% / 96%
    return 0.04, 0.96

def srm_check(clean: pd.DataFrame) -> None:
    n = len(clean)
    n_c = int((clean[GROUP_COL] == CONTROL).sum())
    n_t = int((clean[GROUP_COL] == TREATMENT).sum())
    # просто посмотрел формула SRM, по сути тест на совпадение груп 
    # с ожидаемым выше сплитом
    p_c, p_t = expected_shares(n_c, n_t) 
    exp_c = n * p_c # сколько control должны были получить и сравниваем с фактом
    exp_t = n * p_t
    chi2 = (n_c - exp_c) ** 2 / exp_c + (n_t - exp_t) ** 2 / exp_t
    p_srm = erfc(sqrt(chi2 / 2.0))  
    print("n", n, "control", n_c, f"{n_c/n*100:.2f}%", "treatment", n_t, f"{n_t/n*100:.2f}%")
    print("SRM chi2", round(chi2, 4), "p", round(p_srm, 4))

def sanity_check (raw: pd.DataFrame, clean: pd.DataFrame) -> None:
    #ниче не изменилось, просто пробежались по датасету разобрались
    print("---sanity---")
    print("rows", len(raw), "clean rows->", len(clean))

def add_key(clean: pd.DataFrame)->pd.DataFrame:
    #по сути мы уже знаем что у нас 1 строка = 1 юзер, 
    # так как для данной задачи нам это и нужно
    clean = clean.copy()
    assert clean[USER_COL].nunique() == len(clean)
    print("---keys=rows---")
    return clean

def save_tables(clean: pd.DataFrame) -> None:
    out = ROOT / "data" / "processed"
    out.mkdir(parents=True, exist_ok=True)
    clean.to_parquet(out / "clean.parquet", index=False)
    back = pd.read_parquet(out / "clean.parquet")  
    print("save", len(back))
 

def main()-> None:
    raw=load_data(RAW_PATH)
    cheсk_grain(raw)
    dtype=prepare_types(raw)
    clean=build_clean(dtype)
    srm_check(clean)
    sanity_check(raw, clean)   
    clean = add_key(clean)
    save_tables(clean)

if __name__ == "__main__":
    main()