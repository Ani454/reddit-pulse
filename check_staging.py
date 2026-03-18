import duckdb

conn = duckdb.connect("reddit_pulse.db")

print("\n✅ ROW COUNT")
print("========================")
count = conn.execute("SELECT COUNT(*) as total_rows FROM staging.reddit_posts").df()
print(count)

print("\n📋 SAMPLE POSTS (First 10)")
print("========================")
sample = conn.execute("""
    SELECT 
        post_id,
        title,
        subreddit,
        score,
        num_comments,
        engagement_score,
        post_date,
        post_hour,
        --sentiment_label
    FROM staging.reddit_posts
    ORDER BY engagement_score DESC
    LIMIT 10
""").df()
print(sample)

print("\n📊 POSTS PER SUBREDDIT")
print("========================")
per_sub = conn.execute("""
    SELECT 
        subreddit,
        COUNT(*)            AS total_posts,
        AVG(score)          AS avg_score,
        AVG(num_comments)   AS avg_comments,
        MAX(score)          AS top_score
    FROM staging.reddit_posts
    GROUP BY subreddit
    ORDER BY total_posts DESC
""").df()
print(per_sub)

print("\n⏰ BEST HOURS TO POST")
print("========================")
hours = conn.execute("""
    SELECT 
        post_hour,
        COUNT(*)            AS total_posts,
        AVG(engagement_score) AS avg_engagement
    FROM staging.reddit_posts
    GROUP BY post_hour
    ORDER BY avg_engagement DESC
    LIMIT 5
""").df()
print(hours)

conn.close()