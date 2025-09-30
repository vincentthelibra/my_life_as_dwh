SQL_QUERY_TREND = """
SELECT
    calendar_year,
    album_genre,
    genre_count
FROM
    gold.v_year_end_genre_trend_complete
"""

SQL_QUERY_YEARS = """
SELECT
    distinct calendar_year
FROM
    gold.fact_year_end_track
ORDER BY
    calendar_year DESC
"""

SQL_QUERY_GENRES = """
SELECT
    distinct genre
FROM
    gold.dim_genre_mapping
ORDER BY
    genre
"""

SQL_QUERY_ARTISTS = """
SELECT
    distinct artist_name
FROM
    gold.dim_artist
ORDER BY
    artist_name
"""
