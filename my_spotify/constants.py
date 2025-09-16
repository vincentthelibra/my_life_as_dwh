import os

SCOPE = "playlist-read-private playlist-read-collaborative"
USER_ID = "ox84sc336khxqyai5aoqy87g7"

CONNECTION_PARAMS = {
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DATABASE"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
}

CREATE_FACT_YEAR_TRACK = """--sql
    CREATE TABLE IF NOT EXISTS
    bronze.fact_year_end_track
    (
        calendar_year   int,
        track_id        varchar(255),
        track_name      varchar(255),
        popularity      int,
        external_link   varchar(255),
        album_id        varchar(255),
        artist_id       varchar(255),
        tract_image     varchar(255)
        )
"""
CREATE_DIM_ALBUM = """--sql
    CREATE TABLE IF NOT EXISTS
    bronze.dim_album
    (
        album_id        varchar(255),
        album_name      varchar(255),
        label           varchar(255),
        external_link   varchar(255),
        album_image     varchar(255),
        artist_name     varchar(255)
        )
"""
CREATE_DIM_ARTIST = """--sql
    CREATE TABLE IF NOT EXISTS
    bronze.dim_artist
    (
        artist_id       varchar(255),
        artist_name     varchar(255),
        external_link   varchar(255),
        artist_image    varchar(255)
        )
"""
CREATE_DIM_ALBUM_GENRE = """--sql
    CREATE TABLE IF NOT EXISTS
    bronze.dim_album_genre
    (
        album_id        varchar(255),
        album_genre      varchar(255)
        )
"""

INSERT_QUERY = """INSERT INTO "%s" (data) VALUES (%%s)"""
