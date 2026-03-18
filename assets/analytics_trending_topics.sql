/* @bruin
name: analytics.trending_topics
type: duckdb.sql
depends:
  - staging.reddit_posts
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
    post_date,
    subreddit,
    COUNT(*)                        AS total_posts,
    SUM(score)                      AS total_upvotes,
    SUM(num_comments)               AS total_comments,
    AVG(engagement_score)           AS avg_engagement,
    MAX(score)                      AS top_post_score,

    -- Most common flairs (top topic proxy)
    MODE(flair)                     AS dominant_flair

FROM staging.reddit_posts
GROUP BY post_date, subreddit
ORDER BY post_date DESC, total_upvotes DESC