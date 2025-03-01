from spotipy.client import Spotify
import helper as h
import contants as c
import os
import pandas as pd


def extract_data():
    sp = h.authenticate()
    user_playlists = h.get_user_playlists(sp)
    year_end_lists = h.get_year_end_list(user_playlists)
    fact_year_end_track = h.get_fact_list(sp, year_end_lists)
    dim_album = h.get_dim_album(sp, fact_year_end_track)
    dim_artist = h.get_dim_artist(sp, fact_year_end_track)

    # return fact_year_end_track
    return fact_year_end_track, dim_album, dim_artist


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


def update_database():
    h.postgres_handling("create")
    h.postgres_handling("truncate")
    h.postgres_handling("insert", "fact_year_end_track",
                        "data/fact_year_end_track.csv")
    h.postgres_handling("insert", "dim_album", "data/dim_album.csv")
    h.postgres_handling("insert", "dim_artist", "data/dim_artist.csv")


def main():
    fact_year_end_track, dim_album, dim_artist = extract_data()
    dump_to_csv(fact_year_end_track, "fact_year_end_track.csv")
    dump_to_csv(dim_album, "dim_album.csv")
    dump_to_csv(dim_artist, "dim_artist.csv")

    update_database()


if __name__ == "__main__":
    main()
