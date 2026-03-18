/* @bruin
name: staging.reddit_posts
type: duckdb.sql
depends:
  - raw.reddit_posts
materialization:
  type: table
  strategy: create+replace
columns:
  - name: post_id
    type: string
    checks:
      - name: unique
      - name: not_null
  - name: title
    type: string
    checks:
      - name: not_null
  - name: score
    type: integer
    checks:
      - name: non_negative
@bruin */

SELECT
    post_id,
    TRIM(title)                                         AS title,
    TRIM(selftext)                                      AS selftext,
    author,
    subreddit,
    score,
    num_comments,
    created_utc,
    DATE_TRUNC('day', created_utc)                      AS post_date,
    EXTRACT(hour FROM created_utc)                      AS post_hour,
    DAYOFWEEK(created_utc)                              AS day_of_week,
    url,
    flair,
    LENGTH(title)                                       AS title_length,
    (score + num_comments)                              AS engagement_score

FROM raw.reddit_posts

-- Remove deleted posts
WHERE author != '[deleted]'
  AND title != '[removed]'

-- Deduplicate
QUALIFY ROW_NUMBER() OVER (PARTITION BY post_id ORDER BY created_utc DESC) = 1
