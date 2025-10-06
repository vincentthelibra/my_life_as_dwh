import helper as h

import pandas as pd

from genre_handler2 import GenreHandler_Two

album_genre = GenreHandler_Two()
album_genre.authenticate()
albums = pd.read_csv("./data/album_nogenre.csv").to_dict("records")
dim_album_genre = album_genre.get_genres_for_albums(albums)

h.dump_to_csv(dim_album_genre, "dim_album_genre2.csv")

h.update_database()
