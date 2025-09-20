import os

import constants as c
import pandas as pd
from spotify_handler import SpotifyHandler
from postgres_handler import Postgres

from genre_handler import GenreHandler


def extract_data():
    sph = SpotifyHandler()
    sph.authenticate()
    user_playlists = sph.get_user_playlists()
    year_end_lists = sph.get_year_end_list(user_playlists)
    fact_year_end_track = sph.get_fact_list(year_end_lists)
    dim_album = sph.get_dim_album(fact_year_end_track)
    dim_artist = sph.get_dim_artist(fact_year_end_track)
    album_genre = GenreHandler()
    album_genre.authenticate()
    albums = dim_album
    dim_album_genre = album_genre.get_genres_for_albums(albums)

    # return fact_year_end_track
    return fact_year_end_track, dim_album, dim_artist, dim_album_genre


def dump_to_csv(data, file_name):
    if not data:
        print("No data to dump for {file_name}.")
        return

    df = pd.DataFrame(data)
    directory = "data/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, file_name)
    df.to_csv(filepath, index=False)
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
                pg.execute_query(c.CREATE_DIM_ALBUM_GENRE)
                print("dim_album_genre table created if not exists already.")
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
                pg.truncate_table("dim_album_genre")
                print("dim_album_genre table truncated.")
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
    postgres_handling("insert", "dim_album_genre", "data/dim_album_genre.csv")
