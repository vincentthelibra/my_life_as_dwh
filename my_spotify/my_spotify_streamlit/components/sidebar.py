import streamlit as st
import pandas as pd


def initialize_session_state():
    """Initialize filter values in session state if they don't exist"""
    if "selected_decade" not in st.session_state:
        st.session_state.selected_decade = "All"
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "All"
    if "selected_genre" not in st.session_state:
        st.session_state.selected_genre = "All"
    if "selected_artist" not in st.session_state:
        st.session_state.selected_artist = "All"


def get_filtered_data(df: pd.DataFrame, exclude_filter: str = None) -> pd.DataFrame:
    """
    Apply all current filters EXCEPT the one specified in exclude_filter.
    This allows each filter to show options valid for all OTHER selections.
    """
    filtered_df = df.copy()
    filtered_df["decade"] = (filtered_df["calendar_year"] // 10) * 10

    # Apply decade filter (unless we're calculating decade options)
    if exclude_filter != "decade":
        selected_decade = st.session_state.get("selected_decade", "All")
        if selected_decade != "All":
            filtered_df = filtered_df[filtered_df["decade"] == selected_decade]

    # Apply year filter (unless we're calculating year options)
    if exclude_filter != "year":
        selected_year = st.session_state.get("selected_year", "All")
        if selected_year != "All":
            filtered_df = filtered_df[filtered_df["calendar_year"] == selected_year]

    # Apply genre filter (unless we're calculating genre options)
    if exclude_filter != "genre":
        selected_genre = st.session_state.get("selected_genre", "All")
        if selected_genre != "All":
            filtered_df = filtered_df[filtered_df["album_genre"] == selected_genre]

    # Apply artist filter (unless we're calculating artist options)
    if exclude_filter != "artist":
        selected_artist = st.session_state.get("selected_artist", "All")
        if selected_artist != "All":
            filtered_df = filtered_df[filtered_df["artist_name"] == selected_artist]

    return filtered_df


def render_sidebar(df: pd.DataFrame) -> dict:
    """Render sidebar filters with bidirectional cross-filtering"""

    # Initialize session state
    initialize_session_state()

    st.sidebar.header("Filters")

    with st.sidebar:
        # Clear All Button
        if st.button("Clear All Filters", use_container_width=True):
            st.session_state.selected_decade = "All"
            st.session_state.selected_year = "All"
            st.session_state.selected_genre = "All"
            st.session_state.selected_artist = "All"
            st.rerun()

        st.write("")

        # Add decade column to original df
        df_with_decade = df.copy()
        df_with_decade["decade"] = (df_with_decade["calendar_year"] // 10) * 10

        # ===== DECADE FILTER =====
        with st.container(border=True):
            df_for_decades = get_filtered_data(df_with_decade, exclude_filter="decade")
            available_decades = sorted(df_for_decades["decade"].unique())
            decade_options = ["All"] + available_decades

            # Check if current selection is still valid
            if st.session_state.selected_decade not in decade_options:
                st.session_state.selected_decade = "All"

            # Get the index of the current selection
            current_index = decade_options.index(st.session_state.selected_decade)

            selected_decade = st.selectbox(
                "Decade",
                decade_options,
                index=current_index,
                key="selected_decade",
            )

            if selected_decade != "All":
                filtered_decades = [selected_decade]
            else:
                filtered_decades = available_decades

        # ===== YEAR FILTER =====
        with st.container(border=True):
            df_for_years = get_filtered_data(df_with_decade, exclude_filter="year")
            available_years = sorted(df_for_years["calendar_year"].unique())
            year_options = ["All"] + list(available_years)

            # Check if current selection is still valid
            if st.session_state.selected_year not in year_options:
                st.session_state.selected_year = "All"

            current_index = year_options.index(st.session_state.selected_year)

            selected_year = st.selectbox(
                "Year",
                year_options,
                index=current_index,
                key="selected_year",
            )

            if selected_year != "All":
                filtered_years = [selected_year]
            else:
                filtered_years = available_years

        # ===== GENRE FILTER =====
        with st.container(border=True):
            df_for_genres = get_filtered_data(df_with_decade, exclude_filter="genre")
            available_genres = sorted(df_for_genres["album_genre"].unique())
            genre_options = ["All"] + available_genres

            # Check if current selection is still valid
            if st.session_state.selected_genre not in genre_options:
                st.session_state.selected_genre = "All"

            current_index = genre_options.index(st.session_state.selected_genre)

            selected_genre = st.selectbox(
                "Genre",
                genre_options,
                index=current_index,
                key="selected_genre",
            )

            if selected_genre != "All":
                filtered_genres = [selected_genre]
            else:
                filtered_genres = available_genres

        # ===== ARTIST FILTER =====
        with st.container(border=True):
            df_for_artists = get_filtered_data(df_with_decade, exclude_filter="artist")
            available_artists = sorted(df_for_artists["artist_name"].unique())
            artist_options = ["All"] + available_artists

            # Check if current selection is still valid
            if st.session_state.selected_artist not in artist_options:
                st.session_state.selected_artist = "All"

            current_index = artist_options.index(st.session_state.selected_artist)

            selected_artist = st.selectbox(
                "Artist",
                artist_options,
                index=current_index,
                key="selected_artist",
            )

            if selected_artist != "All":
                filtered_artists = [selected_artist]
            else:
                filtered_artists = available_artists

    return {
        "decades": filtered_decades,
        "years": filtered_years,
        "genres": filtered_genres,
        "artists": filtered_artists,
    }
