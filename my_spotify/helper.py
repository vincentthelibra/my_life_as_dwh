from spotipy.client import Spotify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import contants as c
from pandas import DataFrame
import pandas as pd
import time


def authenticate() -> Spotify:
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=c.SCOPE))


def get_user_playlists(sp: Spotify) -> list:
    all_playlists = []
    limit = 50
    offset = 0

    total_nbr_of_playlists = sp.user_playlists(c.USER_ID)['total']

    while offset < total_nbr_of_playlists:
        user_playlists_page = sp.user_playlists(c.USER_ID,
                                                limit=limit,
                                                offset=offset)
        all_playlists.extend(user_playlists_page['items'])

        offset += limit

    return all_playlists


def get_year_end_list(user_playlist: list) -> list:
    year_end_lists = [(playlist['name'], playlist['id'])
                      for playlist in user_playlist
                      if playlist['name'].endswith('Year End')]
    return year_end_lists


def get_playlist_tracks(sp: Spotify, playlist: tuple) -> DataFrame:
    tracks = []
    limit = 100
    offset = 0
    year_nbr = playlist[0][0:4]

    print(f"Fetching playlist tracks for year {year_nbr}...")
    total_tracks = sp.playlist_tracks(playlist[1])['total']

    request_count = 1

    while offset < total_tracks:
        try:
            tracks_page = sp.playlist_items(playlist[1],
                                            limit=limit,
                                            offset=offset)
        except Exception as e:
            print(e)

        request_count += 1

        tracks.extend([{
            'year': year_nbr,
            'track_id': item['track']['id'],
            'track_name': item['track']['name'],
            'popularity': item['track']['popularity'],
            'url': item['track']['external_urls']['spotify'],
            'album_id': item['track']['album']['id'],
            'artist_id': item['track']['artists'][0]['id']
        } for item in tracks_page['items']
                       if item.get('track', {}).get('external_urls', {})])

        offset += limit

    print(f"Completed fetching {total_tracks} items for year {year_nbr}")
    return pd.DataFrame(tracks)


def get_fact_list(sp: Spotify, year_end_lists: list) -> DataFrame:
    year_end_lists_dfs = [
        get_playlist_tracks(sp, item) for item in year_end_lists
    ]

    df_fact_year_end_list = pd.concat(year_end_lists_dfs, ignore_index=True)
    return df_fact_year_end_list


def get_dim_album(sp: Spotify, df_fact_table: DataFrame) -> DataFrame:

    album_ids = df_fact_table['album_id'].tolist()
    batch_size = 20
    album_batches = [
        album_ids[i:i + batch_size]
        for i in range(0, len(album_ids), batch_size)
    ]

    albums = []
    batch_order = 0
    for batch in album_batches:
        batch_order += 1
        print(f'Processing {batch_order} of {len(album_batches)} batches...')
        try:
            batch_result = sp.albums(batch)
            for album in batch_result['albums']:
                albums.extend([{
                    'album_id': album['id'],
                    'album_name': album['name'],
                    'label': album['label'],
                    'url': album['external_urls']['spotify']
                }])
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)

        albums.extend(batch_result)

    return pd.DataFrame(albums)
