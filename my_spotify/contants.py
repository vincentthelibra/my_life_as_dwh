import os

SCOPE = "playlist-read-private playlist-read-collaborative"
USER_ID = 'ox84sc336khxqyai5aoqy87g7'
CONNECTION_PARAMS = {
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DATABASE"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD")
}

CREATE_FACT_YEAR_TRACK = """--sql
    CREATE TABLE IF NOT EXISTS
    bronze.fact_year_end_track
    (
        calendar_year   int,
        track_id        int PRIMARY KEY,
        track_name      varchar(255) NOT NULL,
        popularity      int,
        external_link   varchar(255),
        album_id        int,
        artist_id       int,
        tract_image     varchar(255)
        )
"""
CREATE_DIM_ALBUM = """--sql
    CREATE TABLE IF NOT EXISTS
    bronze.dim_album
    (
        album_id        int PRIMARY KEY,
        album_name      varchar(255) NOT NULL,
        label           varchar(50),
        external_link   varchar(255),
        album_image     varchar(255)
        )
"""
CREATE_DIM_ARTIST = """--sql
    CREATE TABLE IF NOT EXISTS
    bronze.dim_artist
    (
        artist_id       int PRIMARY KEY,
        artist_name     varchar(255) NOT NULL,
        external_link   varchar(255),
        artist_image    varchar(255)
        )
"""

INSERT_QUERY = """INSERT INTO "%s" (data) VALUES (%%s)"""
