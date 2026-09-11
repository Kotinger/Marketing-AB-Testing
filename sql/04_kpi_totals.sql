-- totals = report (якорь)
-- ожидание: users 588101 | converted ~2.52% | total_ads mean ~24.82 | median ~13
USE marketing_ab;

WITH ranked AS (
  SELECT
    total_ads,
    ROW_NUMBER() OVER (ORDER BY total_ads) AS rn,
    COUNT(*) OVER () AS cnt
  FROM clean_users
),
med AS (
  SELECT ROUND(AVG(total_ads), 0) AS ads_median
  FROM ranked
  WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2))
)
SELECT
  COUNT(*) AS users,
  ROUND(100 * AVG(converted), 2) AS converted_pct,
  ROUND(AVG(total_ads), 2) AS ads_mean,
  (SELECT ads_median FROM med) AS ads_median
FROM clean_users;
