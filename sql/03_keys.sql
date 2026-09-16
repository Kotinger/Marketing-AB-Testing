-- дубли userid и кривые группы - должно быть 0 и 0
USE marketing_ab;

SELECT
  COUNT(*) - COUNT(DISTINCT user_id) AS dup_user_id
FROM clean_users;

SELECT
  COUNT(*) AS bad_group
FROM clean_users
WHERE test_group NOT IN ('psa', 'ad');
