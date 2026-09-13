from pathlib import Path
import pandas as pd
from math import erfc, sqrt

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "processed"


GROUP = "test group"
OUTCOME = "converted"
GUARDRAIL = "total ads"
CONTROL = "psa"
TREATMENT = "ad"
ALPHA = 0.05  # порог значимости


def load_tables() -> pd.DataFrame:
    return pd.read_parquet(OUT_DIR / "clean.parquet")


def ztest(clean: pd.DataFrame) -> None:
    a = clean.loc[clean[GROUP] == CONTROL, OUTCOME]
    b = clean.loc[clean[GROUP] == TREATMENT, OUTCOME]
    # размер и доли
    n_c, n_t = len(a), len(b)
    rate_c, rate_t = a.mean(), b.mean()  # доля покупок (mean 0/1)
    diff = rate_t - rate_c  # ad - psa
    # z-test двух долей
    p_pool = (a.sum() + b.sum()) / (n_c + n_t)
    se = sqrt(p_pool * (1 - p_pool) * (1 / n_c + 1 / n_t))
    z = diff / se if se > 0 else 0.0
    p_val = erfc(abs(z) / sqrt(2))
    se_diff = sqrt(rate_c * (1 - rate_c) / n_c + rate_t * (1 - rate_t) / n_t)
    ci_lo = diff - 1.96 * se_diff
    ci_hi = diff + 1.96 * se_diff
    print("n control  / test:", n_c, n_t)
    print("rate control - > test:", round(rate_c * 100, 2), round(rate_t * 100, 2))
    print("diff pp(test-control):", round(diff * 100, 2))
    print("z:", round(z, 4), "p_val", round(p_val, 4))
    print("CI95 pp:", round(ci_lo * 100, 2), round(ci_hi * 100, 2))
    med_c = clean.loc[clean[GROUP] == CONTROL, GUARDRAIL].median()
    med_t = clean.loc[clean[GROUP] == TREATMENT, GUARDRAIL].median()
    verdict(diff, p_val, med_c, med_t)


def guardrail_ads(clean: pd.DataFrame) -> None:
    # total ads — сколько показов увидели
    print("--- guardrail total ads ---")
    s_c = clean.loc[clean[GROUP] == CONTROL, GUARDRAIL]
    s_t = clean.loc[clean[GROUP] == TREATMENT, GUARDRAIL]
    print(CONTROL, "n", len(s_c), "median", s_c.median(), "mean", round(s_c.mean(), 2))
    print(TREATMENT, "n", len(s_t), "median", s_t.median(), "mean", round(s_t.mean(), 2))


def verdict(diff, p_val, med_c, med_t) -> None:
    if p_val < ALPHA and diff > 0:
        print(
            "ВЕРДИКТ: катим ads — conversion у ad выше psa",
            f"({diff * 100:.2f} pp, p={p_val:.4f});",
            f"total ads median psa={med_c:.0f} / ad={med_t:.0f}",
        )
    elif p_val < ALPHA and diff < 0:
        print("ВЕРДИКТ: ads хуже psa", f"({diff * 100:.2f} pp, p={p_val:.4f}) — не катим")
    else:
        print("ВЕРДИКТ: не катим без доп. данных")


def main() -> None:
    clean = load_tables()
    ztest(clean)
    guardrail_ads(clean)


if __name__ == "__main__":
    main()
