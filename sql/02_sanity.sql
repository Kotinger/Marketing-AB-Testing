-- сколько строк и как разбились группы (с pipeline)
-- у меня было: 588101 | psa 4% | ad 96%
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
