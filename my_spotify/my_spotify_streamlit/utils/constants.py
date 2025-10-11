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

SQL_QUERY_SONGS = """
SELECT
    *
FROM
    gold.v_year_end_track
"""

GENRE_COLORS = {
    "Rock": "#E74C3C",
    "Pop": "#3498DB",
    "Hip Hop": "#9B59B6",
    "R&B": "#E67E22",
    "Country": "#F39C12",
    "Jazz": "#1ABC9C",
    "Electronic": "#2ECC71",
    "Classical": "#34495E",
    "Latin": "#E91E63",
    "Alternative": "#16A085",
}
