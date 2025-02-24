from spotipy.client import Spotify
import helper as h
import contants as c
import pandas as pd


def extract_data():
    sp = h.authenticate()
    user_playlists = h.get_user_playlists(sp)
    year_end_lists = h.get_year_end_list(user_playlists)
    fact_year_end_track = h.get_fact_list(sp, year_end_lists)
    dim_album = h.get_dim_album(sp, fact_year_end_track)
    dim_artist = h.get_dim_artist(sp, fact_year_end_track)

    return fact_year_end_track, dim_album, dim_artist


def update_database(fact_data, dim_album_data, dim_artist_data):
    h.postgres_handling("create")
    h.postgres_handling("insert", fact_data, dim_album_data, dim_artist_data)


def main():
    fact_year_end_track, dim_album, dim_artist = extract_data()
    update_database(fact_year_end_track, dim_album, dim_artist)


if __name__ == "__main__":
    main()
