import helper as h


def main():
    skip_extract = False

    if skip_extract is False:
        fact_year_end_track, dim_album, dim_artist = h.extract_data()
        dim_album = h.update_missing_genres(dim_album)

        h.dump_to_csv(fact_year_end_track, "fact_year_end_track.csv")
        h.dump_to_csv(dim_album, "dim_album.csv")
        h.dump_to_csv(dim_artist, "dim_artist.csv")

    h.update_database()


if __name__ == "__main__":
    main()
