import duckdb

conn = duckdb.connect("reddit_pulse.db")

print("\n📈 TRENDING TOPICS")
print("========================")
trending = conn.execute("""
    SELECT 
        subreddit,
        total_posts,
        total_upvotes,
        total_comments,
        ROUND(avg_engagement, 2) AS avg_engagement,
        dominant_flair
    FROM analytics.trending_topics
    ORDER BY total_upvotes DESC
""").df()
print(trending)

print("\n🔥 VIRAL POSTS (Top 3 per Subreddit)")
print("========================")
viral = conn.execute("""
    SELECT 
        title,
        subreddit,
        score,
        num_comments,
        engagement_score,
        post_hour,
        daily_rank
    FROM analytics.viral_posts
    WHERE daily_rank <= 3
    ORDER BY subreddit, daily_rank
""").df()
print(viral)

conn.close()