SELECT DISTINCT
  `by` /* by is a keyword so we have to backtick it... */
FROM `bigquery-public-data.hacker_news.full` 
WHERE
  type = "comment"
AND
  text is not NULL

ORDER BY
  FARM_FINGERPRINT(`by`) /* Essentially order by RAND(seed) (AND takes no seed args in standard SQL). */
LIMIT
  10000;
