import plotly.express as px
import streamlit as st
import pandas as pd

conn = st.connection("postgresql", type="sql")

sql_query = """
SELECT
	DISTINCT fact.calendar_year,
	album.album_genre,
	COUNT(album.album_genre) OVER ( PARTITION BY fact.calendar_year, album.album_genre) AS genre_count
FROM
	gold.fact_year_end_track fact
LEFT JOIN
	gold.dim_album album
	ON fact.album_id = album.album_id
ORDER BY
	fact.calendar_year;
"""

df = conn.query(sql_query, ttl=600)

# Create a complete grid of all years x all genres
all_years = df["calendar_year"].unique()
all_genres = df["album_genre"].unique()
complete_grid = pd.MultiIndex.from_product(
    [all_years, all_genres], names=["calendar_year", "album_genre"]
).to_frame(index=False)

# Merge with actual data, filling missing combinations with 0
df = complete_grid.merge(df, on=["calendar_year", "album_genre"], how="left")
df["genre_count"] = df["genre_count"].fillna(0)

df = df.sort_values(["calendar_year", "genre_count"], ascending=[True, False])

st.title("Billboard Year End Top 100 Dashboard")

fig = px.bar(
    df,
    x="genre_count",
    y="album_genre",
    color="album_genre",
    animation_frame="calendar_year",
    orientation="h",
    range_x=[0, 100],
    title="Genre Count Over Time",
    labels={"genre_count": "Count", "album_genre": "Genre"},
)

fig.update_layout(
    yaxis={"categoryorder": "total ascending"},
)

st.plotly_chart(fig, use_container_width=True)
