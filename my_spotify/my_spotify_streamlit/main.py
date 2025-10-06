import plotly.express as px
import streamlit as st
import constants as c
import pathlib


st.set_page_config(
    page_title="Billboard Dashboard",
    layout="wide",
    page_icon=":material/music_note:",
    initial_sidebar_state="collapsed",
)

script_dir = pathlib.Path(__file__).parent
css_path = script_dir / "style.css"

with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    "<h1><span>🎵</span> Billboard Year-End Top 100 Dashboard</h1>",
    unsafe_allow_html=True,
)

conn = st.connection("postgresql", type="sql")


st.sidebar.header("Filters")

with st.sidebar:
    # ADD CLEAR ALL BUTTON at the top
    if st.button("Clear All Filters", use_container_width=True):
        st.session_state.selected_decade = "All"
        st.session_state.selected_year = "All"
        st.session_state.selected_genre = "All"
        st.session_state.selected_artist = "All"
        st.rerun()

    st.write("")  # Add some spacing

    filter_decade = st.container(border=True)
    filter_year = st.container(border=True)
    filter_genre = st.container(border=True)
    filter_artist = st.container(border=True)

    with filter_decade:
        sql_query = c.SQL_QUERY_YEARS
        df_years = conn.query(sql_query, ttl=600)

        df_decades = df_years.copy()
        df_decades["decade"] = (df_decades["calendar_year"] // 10) * 10
        decades = sorted(df_decades["decade"].unique().tolist())
        decade_options = ["All"] + decades

        selected_decade = st.selectbox(
            "Decade",
            decade_options,
            key="selected_decade",  # Add key
        )

        if selected_decade == "All":
            filtered_decade = decades
        else:
            filtered_decade = [selected_decade]

    with filter_year:
        sql_query = c.SQL_QUERY_YEARS
        df_years = conn.query(sql_query, ttl=600)
        year_options = ["All"] + df_years["calendar_year"].tolist()

        selected_year = st.selectbox(
            "Year",
            year_options,
            key="selected_year",  # Add key
        )

        if selected_year == "All":
            filtered_year = df_years["calendar_year"].tolist()
        else:
            filtered_year = [selected_year]

    with filter_genre:
        sql_query = c.SQL_QUERY_GENRES
        df_genres = conn.query(sql_query, ttl=600)
        genre_options = ["All"] + df_genres["genre"].tolist()

        selected_genre = st.selectbox(
            "Genre",
            genre_options,
            key="selected_genre",  # Add key
        )

        if selected_genre == "All":
            filtered_genre = df_genres["genre"].tolist()
        else:
            filtered_genre = [selected_genre]

    with filter_artist:
        sql_query = c.SQL_QUERY_ARTISTS
        df_artists = conn.query(sql_query, ttl=600)
        artist_options = ["All"] + df_artists["artist_name"].tolist()

        selected_artist = st.selectbox(
            "Artist",
            artist_options,
            key="selected_artist",  # Add key
        )

        if selected_artist == "All":
            filtered_artist = df_artists["artist_name"].tolist()
        else:
            filtered_artist = [selected_artist]

main_col1, main_col2, main_col3 = st.columns([1, 9, 1])


with main_col2:
    st.markdown("---")

    (
        metric_col_song_count,
        metric_col_artist_count,
        metric_col_album_count,
        metric_col_top_genre,
    ) = st.columns(4, gap="large")

    sql_query = c.SQL_QUERY_SONGS
    df_songs = conn.query(sql_query, ttl=600)

    if selected_year != "All":
        filtered_songs = df_songs[df_songs["calendar_year"] == selected_year]
    else:
        filtered_songs = df_songs

    if selected_decade != "All":
        filtered_songs["decade"] = (filtered_songs["calendar_year"] // 10) * 10
        filtered_songs = filtered_songs[filtered_songs["decade"] == selected_decade]

    if selected_genre != "All":
        filtered_songs = filtered_songs[filtered_songs["album_genre"] == selected_genre]

    if selected_artist != "All":
        filtered_songs = filtered_songs[
            filtered_songs["artist_name"] == selected_artist
        ]

    unique_albums = int(filtered_songs["album_id"].nunique())

    sql_query = c.SQL_QUERY_TREND
    df_trend = conn.query(sql_query, ttl=600)

    if selected_year != "All":
        filtered_trend = df_trend[df_trend["calendar_year"] == selected_year]
    else:
        filtered_trend = df_trend

    top_genre_row = filtered_trend[
        filtered_trend["genre_count"] == filtered_trend["genre_count"].max()
    ]

    if len(filtered_songs) > 0:
        genre_counts = filtered_songs["album_genre"].value_counts()
        top_genre_name = genre_counts.index[0]
    else:
        top_genre_name = "N/A"

    with metric_col_song_count:
        song_count = len(filtered_songs)
        st.metric(label="Songs", border=True, value=song_count)

    with metric_col_artist_count:
        if selected_artist != "All":
            unique_artists = filtered_songs[
                filtered_songs["artist_name"] == selected_artist
            ]["artist_id"].nunique()
        else:
            unique_artists = int(filtered_songs["artist_id"].nunique())
        st.metric(label="Unique Artists", border=True, value=unique_artists)

    with metric_col_album_count:
        st.metric(label="Unique Albums", border=True, value=unique_albums)

    with metric_col_top_genre:
        st.metric(
            label="Most Represented Genre",
            border=True,
            value=top_genre_name,
        )

    # st.markdown("---")

    st.write("")

    chart_col1, chart_col2 = st.columns(2, gap="large")

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
            labels={"genre_count": "Count", "album_genre": "Genre"},
            color_discrete_map=genre_colors,
        )

        fig.update_layout(
            height=400,
            margin=dict(l=120, r=20, t=40, b=40),
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
        st.subheader("Songs by genre and decade")

        df_songs_copy = df_songs.copy()

        df_songs_copy["decade"] = (df_songs_copy["calendar_year"] // 10) * 10

        if selected_year != "All":
            df_songs_copy = df_songs_copy[
                df_songs_copy["calendar_year"] == selected_year
            ]

        if selected_genre != "All":
            df_songs_copy = df_songs_copy[
                df_songs_copy["album_genre"] == selected_genre
            ]

        if selected_artist != "All":
            df_songs_copy = df_songs_copy[
                df_songs_copy["artist_name"] == selected_artist
            ]

        songs_by_genre_decade = (
            df_songs_copy.groupby(["decade", "album_genre"])
            .size()
            .reset_index(name="song_count")
        )

        genre_order = (
            songs_by_genre_decade.groupby("album_genre")["song_count"]
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
        )

        songs_by_genre_decade["decade"] = songs_by_genre_decade["decade"].astype(str)

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

        # Create grouped bar chart
        fig = px.bar(
            songs_by_genre_decade,
            x="decade",
            y="song_count",
            color="album_genre",
            labels={
                "decade": "Decade",
                "song_count": "Number of Songs",
                "album_genre": "Genre",
            },
            color_discrete_map=genre_colors,
            barmode="group",
            category_orders={"album_genre": genre_order},
        )

        fig.update_layout(
            height=400,
            margin=dict(l=50, r=20, t=40, b=40),
            xaxis={"title": ""},
            yaxis={"title": ""},
            legend_title_text="Genre",
            showlegend=True,
        )

        st.plotly_chart(fig, use_container_width=True)

    st.write("")

    # Bottom charts section
    chart_col3, chart_col4 = st.columns(2, gap="large")

    with chart_col3:
        st.subheader("Top 10 artists")
        artist_counts = (
            filtered_songs.groupby("artist_name")
            .size()
            .reset_index(name="song_count")
            .sort_values("song_count", ascending=False)
            .head(10)
        )

        fig = px.bar(
            artist_counts,
            x="song_count",
            y="artist_name",
            orientation="h",
            labels={"song_count": "", "artist_name": ""},
            color="song_count",
            color_continuous_scale="Teal",
            text="song_count",
        )

        fig.update_traces(
            textposition="outside",
        )

        fig.update_layout(
            height=400,
            margin=dict(l=150, r=20, t=40, b=40),
            yaxis={
                "categoryorder": "total ascending",
                "title": "",
            },
            xaxis={
                "title": "",
                "showticklabels": False,
            },
            showlegend=False,
            coloraxis_showscale=False,
        )

        st.plotly_chart(fig, use_container_width=True)

    with chart_col4:
        st.subheader("Top 10 Albums")

        album_counts = (
            filtered_songs.groupby("album_name")
            .size()
            .reset_index(name="song_count")
            .sort_values("song_count", ascending=False)
            .head(10)
        )

        fig = px.bar(
            album_counts,
            x="song_count",
            y="album_name",
            orientation="h",
            labels={"song_count": "", "album_name": ""},
            color="song_count",
            color_continuous_scale="blues",
            text="song_count",
        )

        fig.update_traces(
            textposition="outside",
        )

        fig.update_layout(
            height=400,
            margin=dict(l=150, r=20, t=40, b=40),
            yaxis={
                "categoryorder": "total ascending",
                "title": "",
            },
            xaxis={
                "title": "",
                "showticklabels": False,
            },
            showlegend=False,
            coloraxis_showscale=False,
        )

        st.plotly_chart(fig, use_container_width=True)

st.write("")
st.write("")

# TABLE SECTION
st.subheader("Song Details")

if len(filtered_songs) > 0:
    # Select columns with correct names
    table_data = filtered_songs[
        [
            "calendar_year",
            "track_name",
            "track_external_link",
            "artist_name",
            "artist_image",
            "album_name",
            "album_image",
            "album_genre",
        ]
    ].copy()

    table_data = table_data.rename(
        columns={
            "calendar_year": "Year",
            "track_name": "Song",
            "track_external_link": "Spotify",
            "artist_name": "Artist",
            "artist_image": "Artist Image",
            "album_name": "Album",
            "album_image": "Album Cover",
            "album_genre": "Genre",
        }
    )

    # Sort by year (most recent first)
    table_data = table_data.sort_values("Year", ascending=False)

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "Album Cover": st.column_config.ImageColumn(
                "Album Cover",
                width="small",
            ),
            "Artist Image": st.column_config.ImageColumn(
                "Artist Image",
                width="small",
            ),
            "Year": st.column_config.NumberColumn(
                "Year",
                width="small",
            ),
            "Spotify": st.column_config.LinkColumn(
                "🎵 Spotify",
                display_text="Listen",
                width="small",
            ),
            "Genre": st.column_config.TextColumn(
                "Genre",
                width="small",
            ),
        },
    )

    st.caption(f"Showing {len(table_data)} songs")
else:
    st.info("No songs match the selected filters.")
