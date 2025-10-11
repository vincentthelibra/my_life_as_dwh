import streamlit as st
from components.charts import (
    render_genre_share_chart,
    render_songs_by_decade_chart,
    render_top_albums_chart,
    render_top_artists_chart,
)
from components.header import render_header
from components.metrics import render_metrics
from components.sidebar import render_sidebar
from components.table import render_song_table
from data.loader import load_songs, load_trend_data
from utils.filters import apply_filters
from utils.styling import load_css

st.set_page_config(
    page_title="Billboard Dashboard",
    layout="wide",
    page_icon=":material/music_note:",
    initial_sidebar_state="collapsed",
)


def main():
    load_css()
    render_header()

    # Load data (cached)
    df_songs = load_songs()
    df_trend = load_trend_data()

    # Get filters from sidebar
    filters = render_sidebar(df_songs)

    # Apply filters
    filtered_songs = apply_filters(df_songs, filters)

    # Render dashboard sections
    st.markdown("---")

    render_metrics(filtered_songs)
    st.write("")

    # Charts section
    with st.container(horizontal=True, horizontal_alignment="center", gap="medium"):
        with st.container(horizontal=False, gap="small"):
            render_genre_share_chart(df_trend)

        with st.container(horizontal=False, gap="small"):
            render_songs_by_decade_chart(filtered_songs)

    st.write("")

    # Bottom charts
    with st.container(horizontal=True, horizontal_alignment="center", gap="medium"):
        with st.container(horizontal=False, gap="small"):
            render_top_artists_chart(filtered_songs)

        with st.container(horizontal=False, gap="small"):
            render_top_albums_chart(filtered_songs)

    st.write("")
    st.write("")

    # Table
    render_song_table(filtered_songs)


if __name__ == "__main__":
    main()
