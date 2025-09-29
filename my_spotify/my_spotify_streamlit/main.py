import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Billboard Dashboard",
    layout="centered",
    initial_sidebar_state="collapsed",
)

conn = st.connection("postgresql", type="sql")

sql_query = """
WITH all_years AS (
    SELECT DISTINCT calendar_year
    FROM gold.fact_year_end_track
),
all_genres AS (
    SELECT DISTINCT album_genre
    FROM gold.dim_album
    WHERE album_genre IS NOT NULL
),
all_year_genre AS (
    SELECT 
        y.calendar_year,
        g.album_genre
    FROM all_years y
    CROSS JOIN all_genres g
),
actual_counts AS (
    SELECT
        fact.calendar_year,
        album.album_genre,
        COUNT(*) AS genre_count
    FROM gold.fact_year_end_track fact
    LEFT JOIN gold.dim_album album
        ON fact.album_id = album.album_id
    WHERE album.album_genre IS NOT NULL
    GROUP BY fact.calendar_year, album.album_genre
)
SELECT
    ayg.calendar_year,
    ayg.album_genre,
    COALESCE(ac.genre_count, 0) AS genre_count
FROM all_year_genre ayg
LEFT JOIN actual_counts ac
    ON ayg.calendar_year = ac.calendar_year
    AND ayg.album_genre = ac.album_genre
ORDER BY
    ayg.calendar_year,
    genre_count DESC;
"""

df = conn.query(sql_query, ttl=600)


st.markdown(
    "<h1 style='text-align: center; color: #1DB954;'>🎵 Billboard Year-End Top 100 Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

genre_colors = {
    "Rock": "#E74C3C",  # Red
    "Pop": "#3498DB",  # Blue
    "Hip Hop": "#9B59B6",  # Purple
    "R&B": "#E67E22",  # Orange
    "Country": "#F39C12",  # Yellow/Gold
    "Jazz": "#1ABC9C",  # Turquoise
    "Electronic": "#2ECC71",  # Green
    "Classical": "#34495E",  # Dark Gray
    "Latin": "#E91E63",  # Pink
    "Alternative": "#16A085",  # Teal
}

fig = px.bar(
    df,
    x="genre_count",
    y="album_genre",
    color="album_genre",
    animation_frame="calendar_year",
    orientation="h",
    # range_x=[0, 100],
    title="Genre Count Over Time",
    labels={"genre_count": "Count", "album_genre": "Genre"},
    color_discrete_map=genre_colors,
)

fig.update_layout(
    height=650,
    yaxis={
        "categoryorder": "total ascending",
        "title": "",
    },
    xaxis={
        "title": "",
        "showticklabels": False,
    },
    showlegend=False,
)

st.plotly_chart(fig, use_container_width=True)
