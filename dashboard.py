import duckdb
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(
    page_title="Reddit Pulse",
    page_icon="🔴",
    layout="wide"
)

st.title("🔴 Reddit Pulse Dashboard")
st.caption("What is the internet talking about today?")

@st.cache_data
def load_data():
    conn = duckdb.connect("reddit_pulse.db")

    metrics = conn.execute("""
        SELECT
            COUNT(*)               AS total_posts,
            SUM(score)             AS total_upvotes,
            ROUND(AVG(score), 0)   AS avg_score,
            SUM(num_comments)      AS total_comments
        FROM staging.reddit_posts
    """).df()

    sentiment_pct = conn.execute("""
        SELECT
            ROUND(100.0 * SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) / COUNT(*), 1) AS positive_pct
        FROM analytics.sentiment
    """).df()

    upvotes_by_sub = conn.execute("""
        SELECT subreddit, SUM(total_upvotes) AS total_upvotes
        FROM analytics.trending_topics
        GROUP BY subreddit
        ORDER BY total_upvotes DESC
    """).df()

    sentiment_overall = conn.execute("""
        SELECT sentiment_label, COUNT(*) AS count
        FROM analytics.sentiment
        GROUP BY sentiment_label
        ORDER BY count DESC
    """).df()

    sentiment_by_sub = conn.execute("""
        SELECT
            subreddit,
            SUM(CASE WHEN sentiment_label = 'positive' THEN 1 ELSE 0 END) AS positive,
            SUM(CASE WHEN sentiment_label = 'neutral'  THEN 1 ELSE 0 END) AS neutral,
            SUM(CASE WHEN sentiment_label = 'negative' THEN 1 ELSE 0 END) AS negative
        FROM analytics.sentiment
        GROUP BY subreddit
        ORDER BY subreddit
    """).df()

    best_hours = conn.execute("""
        SELECT
            post_hour,
            ROUND(AVG(engagement_score), 0) AS avg_engagement
        FROM staging.reddit_posts
        GROUP BY post_hour
        ORDER BY post_hour
    """).df()

    viral_posts = conn.execute("""
        SELECT
            v.title,
            v.subreddit,
            v.score,
            v.num_comments,
            v.engagement_score,
            s.sentiment_label
        FROM analytics.viral_posts v
        LEFT JOIN analytics.sentiment s ON v.post_id = s.post_id
        WHERE v.daily_rank <= 5
        ORDER BY v.engagement_score DESC
        LIMIT 5
    """).df()

    trending = conn.execute("""
        SELECT
        subreddit,
        SUM(total_posts)             AS total_posts,
        SUM(total_upvotes)           AS total_upvotes,
        SUM(total_comments)          AS total_comments,
        ROUND(AVG(avg_engagement),0) AS avg_engagement
    FROM analytics.trending_topics
    GROUP BY subreddit
    ORDER BY total_upvotes DESC
    """).df()

    conn.close()
    return metrics, sentiment_pct, upvotes_by_sub, sentiment_overall, sentiment_by_sub, best_hours, viral_posts, trending

metrics, sentiment_pct, upvotes_by_sub, sentiment_overall, sentiment_by_sub, best_hours, viral_posts, trending = load_data()

# ── Metric cards ──────────────────────────────────────────────
st.subheader("Overview")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total posts collected",  f"{int(metrics['total_posts'][0]):,}")
col2.metric("Total upvotes",          f"{int(metrics['total_upvotes'][0]):,}")
col3.metric("Avg score per post",     f"{int(metrics['avg_score'][0]):,}")
col4.metric("Positive sentiment",     f"{sentiment_pct['positive_pct'][0]}%")

st.divider()

# ── Row 1: Upvotes by subreddit + Sentiment donut ─────────────
st.subheader("Engagement & Sentiment")
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        upvotes_by_sub,
        x="subreddit",
        y="total_upvotes",
        title="Total upvotes by subreddit",
        color="subreddit",
        color_discrete_sequence=["#378ADD", "#1D9E75", "#7F77DD", "#EF9F27"],
        labels={"total_upvotes": "Total upvotes", "subreddit": ""}
    )
    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)")
    fig.update_yaxes(gridcolor="rgba(0,0,0,0.06)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    color_map = {"positive": "#639922", "neutral": "#888780", "negative": "#E24B4A"}
    fig = px.pie(
        sentiment_overall,
        names="sentiment_label",
        values="count",
        title="Overall sentiment breakdown",
        color="sentiment_label",
        color_discrete_map=color_map,
        hole=0.6
    )
    fig.update_layout(showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Row 2: Sentiment by subreddit ─────────────────────────────
st.subheader("Sentiment by Subreddit")

sentiment_melted = sentiment_by_sub.melt(
    id_vars="subreddit",
    value_vars=["positive", "neutral", "negative"],
    var_name="sentiment",
    value_name="count"
)

fig = px.bar(
    sentiment_melted,
    x="subreddit",
    y="count",
    color="sentiment",
    title="Positive vs neutral vs negative per community",
    barmode="stack",
    color_discrete_map={"positive": "#639922", "neutral": "#888780", "negative": "#E24B4A"},
    labels={"count": "Number of posts", "subreddit": ""}
)
fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
fig.update_yaxes(gridcolor="rgba(0,0,0,0.06)")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Row 3: Best hours + Trending table ────────────────────────
st.subheader("Posting Patterns & Trending")
col1, col2 = st.columns(2)

with col1:
    fig = px.line(
        best_hours,
        x="post_hour",
        y="avg_engagement",
        title="Best hours to post (UTC)",
        markers=True,
        labels={"post_hour": "Hour (UTC)", "avg_engagement": "Avg engagement score"}
    )
    fig.update_traces(line_color="#7F77DD", marker_color="#7F77DD")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    fig.update_yaxes(gridcolor="rgba(0,0,0,0.06)")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("**Daily trending summary**")
    st.dataframe(
        trending,
        use_container_width=True,
        hide_index=True,
        column_config={
            "subreddit":      st.column_config.TextColumn("Subreddit"),
            "total_posts":    st.column_config.NumberColumn("Posts"),
            "total_upvotes":  st.column_config.NumberColumn("Upvotes"),
            "total_comments": st.column_config.NumberColumn("Comments"),
            "avg_engagement": st.column_config.NumberColumn("Avg engagement"),
        }
    )

st.divider()

# ── Row 4: Viral posts ────────────────────────────────────────
st.subheader("Top Viral Posts Today")

def sentiment_badge(label):
    colors = {
        "positive": "🟢",
        "negative": "🔴",
        "neutral":  "⚪"
    }
    return colors.get(label, "⚪")

for i, row in viral_posts.iterrows():
    with st.container():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"**{i+1}. {row['title']}**")
            st.caption(f"r/{row['subreddit']} · {int(row['score']):,} upvotes · {int(row['num_comments']):,} comments")
        with col2:
            label = row.get('sentiment_label', 'neutral')
            st.markdown(f"{sentiment_badge(label)} `{label}`")
        st.divider()