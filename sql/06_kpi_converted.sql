-- разница ad - psa в pp (z/p в report)
USE marketing_ab;

SELECT
  ROUND(100 * (
    AVG(CASE WHEN test_group = 'ad' THEN converted END)
    - AVG(CASE WHEN test_group = 'psa' THEN converted END)
  ), 2) AS converted_diff_pp
FROM clean_users;
