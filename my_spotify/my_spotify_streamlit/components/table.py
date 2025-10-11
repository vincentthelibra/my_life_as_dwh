import streamlit as st
import pandas as pd


def render_song_table(df: pd.DataFrame):
    """Render the song details table"""
    st.subheader("Song Details")

    if len(df) == 0:
        st.info("No songs match the selected filters.")
        return

    table_data = df[
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

    table_data = table_data.sort_values("Year", ascending=False)

    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True,
        height=500,
        column_config={
            "Album Cover": st.column_config.ImageColumn("Album Cover", width="small"),
            "Artist Image": st.column_config.ImageColumn("Artist Image", width="small"),
            "Year": st.column_config.NumberColumn("Year", width="small"),
            "Spotify": st.column_config.LinkColumn(
                "🎵 Spotify", display_text="Listen", width="small"
            ),
            "Genre": st.column_config.TextColumn("Genre", width="small"),
        },
    )

    st.caption(f"Showing {len(table_data)} songs")
