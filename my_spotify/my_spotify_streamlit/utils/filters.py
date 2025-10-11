import pandas as pd


def apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Apply all filters to the dataframe"""
    filtered_df = df.copy()

    # Add decade column if needed
    filtered_df["decade"] = (filtered_df["calendar_year"] // 10) * 10

    # Apply filters
    filtered_df = filtered_df[
        (filtered_df["calendar_year"].isin(filters["years"]))
        & (filtered_df["decade"].isin(filters["decades"]))
        & (filtered_df["album_genre"].isin(filters["genres"]))
        & (filtered_df["artist_name"].isin(filters["artists"]))
    ]

    return filtered_df
