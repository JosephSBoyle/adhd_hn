SELECT DISTINCT
  `by` /* by is a keyword so we have to backtick it... */
FROM `bigquery-public-data.hacker_news.full` 
WHERE
  type = "comment"
AND
  text is not NULL
AND
  deleted is NULL /* respect user's privacy, if they've deleted a comment don't download it. */
AND
    /* (?i) enables case insensitivity. */
    regexp_contains(text, "(?i)I (am|was|have been) diagnosed with (ADHD|ADD)")
  OR
    regexp_contains(text, "(?i)As (someone|a person|an individual) (living|) with (ADHD|ADD)")
  OR
    regexp_contains(text, "(?i)I have (ADHD|ADD)")

ORDER BY
  `by`
LIMIT
  10000; /* There are fewer users than this anyways. */
