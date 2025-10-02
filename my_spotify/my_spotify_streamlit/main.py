import plotly.express as px
import streamlit as st
import constants as c


st.set_page_config(
    page_title="Billboard Dashboard",
    layout="wide",
    page_icon=":material/music_note:",
    initial_sidebar_state="collapsed",
)


# CSS
st.markdown(
    """
    <style>
    /* Center selectbox labels */
    label[data-testid="stWidgetLabel"] {
        text-align: center !important;
        justify-content: center !important;
    }
    
    /* Increase font size of label text */
    label[data-testid="stWidgetLabel"] p {
        font-size: 20px !important;
        font-weight: bold !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; color: #1DB954;'>🎵 Billboard Year-End Top 100 Dashboard</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

conn = st.connection("postgresql", type="sql")


sql_query = c.SQL_QUERY_YEARS
df_years = conn.query(sql_query, ttl=600)


filter_col_year, filter_col_genre, filter_col_artist = st.columns(3)

with filter_col_year:
    with st.container(border=True):
        selected_year = st.selectbox(
            "Year",
            (df_years["calendar_year"]),
        )

with filter_col_genre:
    sql_query = c.SQL_QUERY_GENRES
    df_genres = conn.query(sql_query, ttl=600)
    with st.container(border=True):
        selected_genre = st.selectbox("Genre", (df_genres["genre"]))

with filter_col_artist:
    sql_query = c.SQL_QUERY_ARTISTS
    df_artists = conn.query(sql_query, ttl=600)
    with st.container(border=True):
        selected_artist = st.selectbox("Artist", (df_artists["artist_name"]))

st.markdown("---")

(
    metric_col_song_count,
    metric_col_artist_count,
    metric_col_album_count,
    metric_col_top_genre,
) = st.columns(4)

sql_query = c.SQL_QUERY_SONGS
df_songs = conn.query(sql_query, ttl=600)

filtered_songs = df_songs[df_songs["calendar_year"] == selected_year]

song_count = len(filtered_songs)
unique_artists = int(filtered_songs["artist_id"].nunique())  # type: ignore[attr-defined]
unique_albums = int(filtered_songs["album_id"].nunique())  # type: ignore[attr-defined]


sql_query = c.SQL_QUERY_TREND
df_trend = conn.query(sql_query, ttl=600)

filtered_trend = df_trend[df_trend["calendar_year"] == selected_year]
top_genre_row = filtered_trend[
    filtered_trend["genre_count"] == filtered_trend["genre_count"].max()
]
top_genre_name = top_genre_row["album_genre"].values[0]  # type: ignore[attr-defined]

with metric_col_song_count:
    st.metric(label="Songs", border=True, value=song_count)

with metric_col_artist_count:
    st.metric(label="Unique Artists", border=True, value=unique_artists)

with metric_col_album_count:
    st.metric(label="Unique Albums", border=True, value=unique_albums)

with metric_col_top_genre:
    st.metric(
        label="Most Represented Genre",
        border=True,
        value=top_genre_name,
    )

st.markdown("---")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Genre share by year")

    # Fetch data
    sql_query = c.SQL_QUERY_TREND
    df = conn.query(sql_query, ttl=600)

    # Define colors
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

    # Create chart
    fig = px.bar(
        df,
        x="genre_count",
        y="album_genre",
        color="album_genre",
        animation_frame="calendar_year",
        orientation="h",
        # title="Genre Count Over Time",
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

with chart_col2:
    st.subheader("Artist diversity")
    st.info("Chart Placeholder")
    st.caption(
        "Distinct artist_name per year. Optional: Herfindahl index of artist concentration."
    )

# Bottom charts section
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Top artists by appearances (selected period)")
    st.info("Chart Placeholder")

with chart_col4:
    st.subheader("Top albums contributing songs")
    st.info("Chart Placeholder")
