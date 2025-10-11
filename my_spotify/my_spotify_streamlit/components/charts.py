import streamlit as st
import pandas as pd
import plotly.express as px
from utils.constants import GENRE_COLORS


def render_genre_share_chart(df_trend: pd.DataFrame):
    """Render animated genre share by year chart"""
    st.subheader("Genre Share By Year")

    fig = px.bar(
        df_trend,
        x="genre_count",
        y="album_genre",
        color="album_genre",
        animation_frame="calendar_year",
        orientation="h",
        labels={"genre_count": "Count", "album_genre": "Genre"},
        color_discrete_map=GENRE_COLORS,
    )

    fig.update_layout(
        height=400,
        margin=dict(l=120, r=20, t=40, b=40),
        yaxis={"categoryorder": "total ascending", "title": ""},
        xaxis={"title": "", "showticklabels": False},
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


def render_songs_by_decade_chart(df: pd.DataFrame):
    """Render songs by genre and decade chart"""
    st.subheader("Songs By Genre and Decade")

    df_copy = df.copy()
    df_copy["decade"] = (df_copy["calendar_year"] // 10) * 10

    songs_by_genre_decade = (
        df_copy.groupby(["decade", "album_genre"]).size().reset_index(name="song_count")
    )

    genre_order = (
        songs_by_genre_decade.groupby("album_genre")["song_count"]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    songs_by_genre_decade["decade"] = songs_by_genre_decade["decade"].astype(str)

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
        color_discrete_map=GENRE_COLORS,
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

    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


def render_top_artists_chart(df: pd.DataFrame):
    """Render top 10 artists chart"""
    st.subheader("Top 10 Artists")

    artist_counts = (
        df.groupby("artist_name")
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

    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=400,
        margin=dict(l=150, r=20, t=40, b=40),
        yaxis={"categoryorder": "total ascending", "title": ""},
        xaxis={"title": "", "showticklabels": False},
        showlegend=False,
        coloraxis_showscale=False,
    )

    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})


def render_top_albums_chart(df: pd.DataFrame):
    """Render top 10 albums chart"""
    st.subheader("Top 10 Albums")

    album_counts = (
        df.groupby("album_name")
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

    fig.update_traces(textposition="outside")
    fig.update_layout(
        height=400,
        margin=dict(l=150, r=20, t=40, b=40),
        yaxis={"categoryorder": "total ascending", "title": ""},
        xaxis={"title": "", "showticklabels": False},
        showlegend=False,
        coloraxis_showscale=False,
    )

    st.plotly_chart(fig, use_container_width=True, config={"responsive": True})
