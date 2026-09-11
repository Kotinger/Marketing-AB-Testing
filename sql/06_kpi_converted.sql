-- converted A/B = report.kpi_converted (n / rate / diff pp)
-- ожидание:
-- psa n=23524 rate 1.79% | ad n=564577 rate 2.55% | diff +0.77 pp
-- (z-test / p-value — в report.py; SQL даёт n и rates для сверки)
USE marketing_ab;

SELECT
  test_group,
  COUNT(*) AS n,
  SUM(converted) AS converted_n,
  ROUND(100 * AVG(converted), 2) AS converted_pct
FROM clean_users
GROUP BY test_group
ORDER BY test_group;

-- diff pp: treatment(ad) − control(psa)
SELECT
  ROUND(100 * (
    AVG(CASE WHEN test_group = 'ad' THEN converted END)
    - AVG(CASE WHEN test_group = 'psa' THEN converted END)
  ), 2) AS converted_diff_pp
FROM clean_users;
