from pathlib import Path
import pandas as pd
from math import erfc, sqrt

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT/"data"/"processed"

USER_COL = "user id"
GROUP_COL = "test group" # "ad"/"psa"
CONTROL = "psa"          # контроль
TREATMENT = "ad"         # тест
OUTCOME_COLS = ["converted"]   
GUARDRAIL_COLS = ["total ads"] 


def load_tables()-> pd.DataFrame:
    return pd.read_parquet(OUT_DIR/"clean.parquet")

def expected_shares(n_control: int, n_treatment: int) -> tuple[float, float]:

    return 0.04, 0.96

def sanity_srm(clean: pd.DataFrame) -> None:
    # для наглядности дублирую
    print("--- SRM ---")
    n = len(clean)
    n_c = int((clean[GROUP_COL] == CONTROL).sum())
    n_t = int((clean[GROUP_COL] == TREATMENT).sum())
    p_c, p_t = expected_shares(n_c, n_t)
    exp_c = n * p_c
    exp_t = n * p_t
    chi2 = (n_c - exp_c) ** 2 / exp_c + (n_t - exp_t) ** 2 / exp_t
    p_srm = erfc(sqrt(chi2 / 2.0))
    print("users", n)
    print("psa", n_c, f"{n_c/n*100:.2f}%")
    print("ad", n_t, f"{n_t/n*100:.2f}%")
    print("SRM chi2", round(chi2, 4), "p", round(p_srm, 4))

def kpi_converted(clean: pd.DataFrame) -> None:
    # primary: купил / не купил по группам
    col = OUTCOME_COLS[0]
    a = clean.loc[clean[GROUP_COL] == CONTROL, col]
    b = clean.loc[clean[GROUP_COL] == TREATMENT, col]
    n1, n2 = len(a), len(b)
    x1, x2 = int(a.sum()), int(b.sum())
    p1, p2 = x1 / n1, x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se if se > 0 else 0.0
    p = erfc(abs(z) / sqrt(2.0))
    se_diff = sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    diff = p2 - p1
    ci_lo = diff - 1.96 * se_diff
    ci_hi = diff + 1.96 * se_diff
    print("---", col, "---")
    print("n psa", n1, "ad", n2)
    print("rate%", round(p1 * 100, 2), "->", round(p2 * 100, 2))
    print("diff pp", round(diff * 100, 2))
    print("z", round(z, 3), "p", round(p, 6))
    print("CI95 pp", round(ci_lo * 100, 2), round(ci_hi * 100, 2))
    # median ads нужен для фразы вердикта
    ads = GUARDRAIL_COLS[0]
    med_c = clean.loc[clean[GROUP_COL] == CONTROL, ads].median()
    med_t = clean.loc[clean[GROUP_COL] == TREATMENT, ads].median()
    verdict(diff, p, med_c, med_t)

def kpi_guardrail(clean: pd.DataFrame) -> None:
    # total ads — сколько показов увидел
    print("--- guardrail total ads ---")
    col = GUARDRAIL_COLS[0]
    s_c = clean.loc[clean[GROUP_COL] == CONTROL, col]
    s_t = clean.loc[clean[GROUP_COL] == TREATMENT, col]
    print(CONTROL, "n", len(s_c), "median", s_c.median(), "mean", round(s_c.mean(), 2))
    print(TREATMENT, "n", len(s_t), "median", s_t.median(), "mean", round(s_t.mean(), 2))

def verdict(diff, p, med_c, med_t)-> None:
    # смотрим: реклама (ad) лучше (psa) по покупкам или нет
    # p < 0.05 = разница не случайная; diff > 0 = у ad конверсия выше
    print("--- verdict ---")
    if p < 0.05 and diff > 0:
        # реклама реально поднимает покупки → катим ads
        print("ВЕРДИКТ: катим ads — conversion у ad выше psa", f"({diff*100:.2f} pp, p={p:.4f});",
              f"total ads median psa={med_c:.0f} / ad={med_t:.0f}")
    elif p < 0.05 and diff < 0:
        # с рекламой покупают реже — не катим
        print("ВЕРДИКТ: ads хуже psa", f"({diff*100:.2f} pp, p={p:.4f}) — не катим")
    else:
        # разница маленькая / не доказано 
        print("ВЕРДИКТ: inconclusive — разница ns", f"({diff*100:.2f} pp, p={p:.4f})")

def main()-> None:
    clean=load_tables()
    sanity_srm(clean)
    kpi_converted(clean)
    kpi_guardrail(clean)

if __name__ == "__main__":
    main()
