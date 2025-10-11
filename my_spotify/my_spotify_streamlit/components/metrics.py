import streamlit as st
import pandas as pd


def render_metrics(df: pd.DataFrame):
    """Render the 4 metric cards"""
    with st.container(horizontal=True, horizontal_alignment="distribute", gap="large"):
        song_count = len(df)
        st.metric(label="Songs", border=True, value=song_count)

        unique_artists = int(df["artist_id"].nunique())
        st.metric(label="Unique Artists", border=True, value=unique_artists)

        unique_albums = int(df["album_id"].nunique())
        st.metric(label="Unique Albums", border=True, value=unique_albums)

        if len(df) > 0:
            genre_counts = df["album_genre"].value_counts()
            top_genre = genre_counts.index[0]
        else:
            top_genre = "N/A"

        st.metric(label="Most Represented Genre", border=True, value=top_genre)
