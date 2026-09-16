-- общая конверсия и показы по всем
-- converted 2.52% | ads mean 24.82
USE marketing_ab;

SELECT
  COUNT(*) AS users,
  SUM(converted) AS converted_n,
  ROUND(100 * AVG(converted), 2) AS converted_pct,
  ROUND(AVG(total_ads), 2) AS ads_mean
FROM clean_users;
