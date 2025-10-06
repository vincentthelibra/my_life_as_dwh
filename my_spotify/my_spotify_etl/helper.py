import os

import constants as c
import pandas as pd
from spotify_handler import SpotifyHandler
from postgres_handler import Postgres

from genre_handler import GenreHandler
from musicBrainz_handler import MusicBrainzHandler


def extract_data():
    sph = SpotifyHandler()
    sph.authenticate()
    user_playlists = sph.get_user_playlists()
    year_end_lists = sph.get_year_end_list(user_playlists)
    fact_year_end_track_list = sph.get_fact_list(year_end_lists)
    fact_year_end_track = pd.DataFrame(fact_year_end_track_list)

    dim_album_list = sph.get_dim_album(fact_year_end_track_list)
    dim_album = pd.DataFrame(dim_album_list)

    dim_artist_list = sph.get_dim_artist(fact_year_end_track_list)
    dim_artist = pd.DataFrame(dim_artist_list)

    album_genre = GenreHandler()
    album_genre.authenticate()
    albums = dim_album_list
    dim_album_genre_list = album_genre.get_genres_for_albums(albums)

    genre_mapping = {item["album_id"]: item["genre"] for item in dim_album_genre_list}
    dim_album["genre"] = dim_album["album_id"].replace(genre_mapping)

    # return fact_year_end_track
    return fact_year_end_track, dim_album, dim_artist


def update_missing_genres(dim_album):
    null_genre_albums = dim_album[dim_album["genre"].isnull()]

    if len(null_genre_albums) == 0:
        return dim_album

    print(
        f"Found {len(null_genre_albums)} albums without genres. Attempting alternative lookup..."
    )

    musicBranz = MusicBrainzHandler()

    null_genre_albums_list = null_genre_albums.to_dict("records")

    additional_genres = musicBranz.get_genres_for_albums(null_genre_albums_list)

    for genre_item in additional_genres:
        album_id = genre_item["album_id"]
        genre = genre_item["genre"]
        dim_album.loc[dim_album["album_id"] == album_id, "genre"] = genre

    return dim_album


def dump_to_csv(data, file_name):
    # Better check for empty DataFrames
    if data is None or (hasattr(data, "empty") and data.empty):
        print(f"No data to dump for {file_name}.")
        return

    directory = "data/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, file_name)
    data.to_csv(filepath, index=False)
    print(f"Data dumped to {filepath}.")


def postgres_handling(
    action: str, table_name: str | None = None, file_path: str | None = None
) -> None:
    pg = Postgres()
    if pg.connect():
        if action == "create":
            try:
                pg.execute_query(c.CREATE_FACT_YEAR_TRACK)
                print("fact table created if not exists already.")
                pg.execute_query(c.CREATE_DIM_ALBUM)
                print("dim_album table created if not exists already.")
                pg.execute_query(c.CREATE_DIM_ARTIST)
                print("dim_artist table created if not exists already.")
            except Exception as e:
                print(e)
        elif action == "truncate":
            try:
                pg.truncate_table("fact_year_end_track")
                print("fact table truncated.")
                pg.truncate_table("dim_album")
                print("dim_album table truncated.")
                pg.truncate_table("dim_artist")
                print("dim_artist table truncated.")
            except Exception as e:
                print(e)
        elif action == "insert":
            try:
                if pg.load_from_file(table_name, file_path):
                    print(f"{table_name} table loaded.")
            except Exception as e:
                print(f"Error loading {table_name} table: {e}")
        else:
            print("Action not defined yet.")


def update_database():
    postgres_handling("create")
    postgres_handling("truncate")
    postgres_handling("insert", "fact_year_end_track", "data/fact_year_end_track.csv")
    postgres_handling("insert", "dim_album", "data/dim_album.csv")
    postgres_handling("insert", "dim_artist", "data/dim_artist.csv")
