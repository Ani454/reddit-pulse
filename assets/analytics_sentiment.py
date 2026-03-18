"""@bruin
name: analytics.sentiment
type: python
connection: "duckdb-default"
depends:
  - staging.reddit_posts
materialization:
  type: table
  strategy: create+replace
columns:
  - name: post_id
    type: string
  - name: title
    type: string
  - name: subreddit
    type: string
  - name: score
    type: integer
  - name: post_date
    type: date
  - name: sentiment_score
    type: float
  - name: sentiment_label
    type: string
@bruin"""

import duckdb
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def materialize():
    # Load clean data from staging layer
    conn = duckdb.connect("reddit_pulse.db")
    df = conn.execute("SELECT * FROM staging.reddit_posts").df()
    conn.close()

    # Initialize sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()

    def get_sentiment(text: str) -> dict:
        """Score text and return a label + score."""
        scores = analyzer.polarity_scores(text)
        compound = scores["compound"]  # Ranges from -1 (negative) to +1 (positive)

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {"sentiment_score": compound, "sentiment_label": label}

    # Apply sentiment to every post title
    print("🧠 Analyzing sentiment...")
    sentiment_data = df["title"].apply(get_sentiment)
    df["sentiment_score"] = sentiment_data.apply(lambda x: x["sentiment_score"])
    df["sentiment_label"] = sentiment_data.apply(lambda x: x["sentiment_label"])

    print(df["sentiment_label"].value_counts())

    return df[[
        "post_id", "title", "subreddit", "score",
        "post_date", "sentiment_score", "sentiment_label"
    ]]