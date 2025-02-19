"""
* Steps below:
*   0. Create Class
*   0.1 Playlist
*   0.2 Album
*   0.3 Artist
*   1. Authenticate
*   2. Make API calls
*       2.1 Get the correct user id for user MD132
*       2.2 Find all the playlists under the id found in 2.1 with key words "Year End"
*       2.3 For each playlist found in 2.2
*           2.3.1 get the items(tracks) under this class
*           2.3.2 append to the class Playlist
*           2.3.3 for each Playlist.Track
*               2.3.3.1 get Tract info
*               2.3.3.1 append each attribute to Playlist.Track
*               2.3.3.2 for Playlist.Track.Album
*                   2.3.2.3 get Album info
*                   2.3.2.4 append to Album class
*                   2.3.2.3 get Artist info
*                   2.3.2.4 append to Artist class
"""

from spotipy.client import Spotify
import helper as h
import contants as c
import pandas as pd


def main():
    sp = h.authenticate()
    user_playlists = h.get_user_playlists(sp)
    year_end_lists = h.get_year_end_list(user_playlists)
    df_fact_year_end_list = h.get_fact_list(sp, year_end_lists)
    df_dim_album = h.get_dim_album(sp, df_fact_year_end_list)


if __name__ == "__main__":
    main()
