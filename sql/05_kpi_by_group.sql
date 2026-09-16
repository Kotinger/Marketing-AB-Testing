-- по группам: n / conversion / ads - те же цифры что в report
-- psa 1.79% | ad 2.55% | median 12 vs 13
-- median одним проходом (без коррелированных подзапросов - на 500k+ виснет)
USE marketing_ab;

WITH ranked AS (
  SELECT
    test_group,
    total_ads,
    ROW_NUMBER() OVER (PARTITION BY test_group ORDER BY total_ads) AS rn,
    COUNT(*) OVER (PARTITION BY test_group) AS cnt
  FROM clean_users
),
med AS (
  SELECT
    test_group,
    ROUND(AVG(total_ads), 0) AS ads_median
  FROM ranked
  WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2))
  GROUP BY test_group
)
SELECT
  g.test_group,
  COUNT(*) AS n,
  SUM(g.converted) AS converted_n,
  ROUND(100 * AVG(g.converted), 2) AS converted_pct,
  ROUND(AVG(g.total_ads), 2) AS ads_mean,
  m.ads_median
FROM clean_users g
JOIN med m ON m.test_group = g.test_group
GROUP BY g.test_group, m.ads_median
ORDER BY g.test_group;
