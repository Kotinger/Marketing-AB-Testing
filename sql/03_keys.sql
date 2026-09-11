-- keys: user_id уникален (1 юзер = 1 строка)
-- ожидание: dup_user_id 0 | bad_group 0
USE marketing_ab;

SELECT
  COUNT(*) - COUNT(DISTINCT user_id) AS dup_user_id
FROM clean_users;

SELECT
  COUNT(*) AS bad_group
FROM clean_users
WHERE test_group NOT IN ('psa', 'ad');
