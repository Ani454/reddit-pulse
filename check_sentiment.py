import duckdb

conn = duckdb.connect("reddit_pulse.db")

print("\n🧠 SENTIMENT OVERVIEW")
print("========================")
overview = conn.execute("""
    SELECT 
        sentiment_label,
        COUNT(*)                        AS total_posts,
        ROUND(AVG(sentiment_score), 3)  AS avg_score,
        ROUND(AVG(score), 0)            AS avg_upvotes
    FROM analytics.sentiment
    GROUP BY sentiment_label
    ORDER BY total_posts DESC
""").df()
print(overview)

print("\n📊 SENTIMENT BY SUBREDDIT")
print("========================")
by_sub = conn.execute("""
    SELECT 
        subreddit,
        COUNT(*)                                                    AS total_posts,
        SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) AS positive,
        SUM(CASE WHEN sentiment_label = 'neutral'  THEN 1 ELSE 0 END) AS neutral,
        SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) AS negative,
        ROUND(AVG(sentiment_score), 3)                              AS avg_sentiment
    FROM analytics.sentiment
    GROUP BY subreddit
    ORDER BY avg_sentiment DESC
""").df()
print(by_sub)

print("\n😊 TOP 5 MOST POSITIVE POSTS")
print("========================")
positive = conn.execute("""
    SELECT 
        title,
        subreddit,
        score,
        ROUND(sentiment_score, 3) AS sentiment_score
    FROM analytics.sentiment
    WHERE sentiment_label = 'positive'
    ORDER BY sentiment_score DESC
    LIMIT 5
""").df()
print(positive)

print("\n😡 TOP 5 MOST NEGATIVE POSTS")
print("========================")
negative = conn.execute("""
    SELECT 
        title,
        subreddit,
        score,
        ROUND(sentiment_score, 3) AS sentiment_score
    FROM analytics.sentiment
    WHERE sentiment_label = 'negative'
    ORDER BY sentiment_score ASC
    LIMIT 5
""").df()
print(negative)

print("\n🏆 MOST UPVOTED BY SENTIMENT")
print("========================")
upvoted = conn.execute("""
    SELECT 
        sentiment_label,
        title,
        subreddit,
        score
    FROM analytics.sentiment
    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY sentiment_label 
        ORDER BY score DESC
    ) = 1
    ORDER BY score DESC
""").df()
print(upvoted)

conn.close()