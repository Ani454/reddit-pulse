/* @bruin
name: analytics.viral_posts
type: duckdb.sql
depends:
  - staging.reddit_posts
materialization:
  type: table
  strategy: create+replace
@bruin */

SELECT
    post_id,
    title,
    subreddit,
    author,
    score,
    num_comments,
    engagement_score,
    post_hour,
    day_of_week,
    title_length,
    flair,
    post_date,

    -- Rank posts within each subreddit per day
    RANK() OVER (
        PARTITION BY subreddit, post_date
        ORDER BY engagement_score DESC
    ) AS daily_rank

FROM staging.reddit_posts
QUALIFY daily_rank <= 10
ORDER BY post_date DESC, engagement_score DESC