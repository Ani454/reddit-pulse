"""@bruin
name: raw.reddit_posts
type: python
connection: "duckdb-default"
materialization:
  type: table
  strategy: append
columns:
  - name: post_id
    type: string
  - name: title
    type: string
  - name: selftext
    type: string
  - name: author
    type: string
  - name: subreddit
    type: string
  - name: score
    type: integer
  - name: num_comments
    type: integer
  - name: created_utc
    type: timestamp
  - name: url
    type: string
  - name: flair
    type: string
@bruin"""

import time
import requests
import pandas as pd
from datetime import datetime, timezone

# ✅ No credentials needed — uses Reddit's public JSON endpoint
HEADERS = {"User-Agent": "RedditPulse/1.0 (data engineering project)"}

SUBREDDITS = [
    "AI",
    "AITrending",
    "Claude",
    "ChatGPT",
    "AIAgents",
    "OpenClaw",
    "dataengineering",
    "technology"
]

def fetch_subreddit_posts(subreddit: str, limit: int = 100) -> list:
    """Fetch hot posts from a subreddit using public JSON endpoint."""
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        posts = []
        for item in data["data"]["children"]:
            p = item["data"]

            # Skip stickied mod posts (not real content)
            if p.get("stickied"):
                continue

            posts.append({
                "post_id":      p["id"],
                "title":        p["title"],
                "selftext":     p.get("selftext", "")[:500],
                "author":       str(p.get("author", "[unknown]")),
                "subreddit":    subreddit,
                "score":        int(p.get("score", 0)),
                "num_comments": int(p.get("num_comments", 0)),
                "created_utc":  datetime.fromtimestamp(
                                    p["created_utc"], tz=timezone.utc
                                ),
                "url":          p.get("url", ""),
                "flair":        p.get("link_flair_text") or ""
            })

        return posts

    except requests.RequestException as e:
        print(f"⚠️  Failed to fetch r/{subreddit}: {e}")
        return []

def materialize():
    """Main function Bruin calls to run this asset."""
    all_posts = []

    for subreddit in SUBREDDITS:
        print(f"📥 Fetching r/{subreddit}...")
        posts = fetch_subreddit_posts(subreddit)
        all_posts.extend(posts)
        print(f"   ✅ Got {len(posts)} posts")

        # ⏳ Be polite — wait 2 seconds between requests
        # Reddit rate limits aggressive scrapers
        time.sleep(2)

    df = pd.DataFrame(all_posts)
    print(f"\n🎉 Total posts collected: {len(df)}")
    return df