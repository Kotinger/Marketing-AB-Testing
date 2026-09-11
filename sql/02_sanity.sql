-- sanity = report.sanity_srm
-- ожидание: rows 588101 | user_id unique 588101 | psa 23524 (4%) | ad 564577 (96%)
USE marketing_ab;

SELECT COUNT(*) AS rows_n FROM clean_users;

SELECT COUNT(DISTINCT user_id) AS users_n FROM clean_users;

SELECT
  test_group,
  COUNT(*) AS n,
  ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM clean_users), 2) AS share_pct
FROM clean_users
GROUP BY test_group
ORDER BY test_group;

SELECT
  MIN(total_ads) AS ads_min,
  ROUND(AVG(total_ads), 2) AS ads_mean,
  MAX(total_ads) AS ads_max
FROM clean_users;
