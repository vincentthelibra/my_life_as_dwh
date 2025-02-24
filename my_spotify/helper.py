from spotipy.client import Spotify
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import contants as c
from pandas import DataFrame
import pandas as pd
import time
from postgres_handler import Postgres
from requests.exceptions import ReadTimeout
import logging


class RateLimitHandler(logging.Handler):

    def emit(self, record):
        if "rate/request limit" in record.getMessage():
            retry_time = int(record.getMessage().split("after: ")[-1])
            print(
                f"Rate limit reached. Retrying after {retry_time} seconds...")
            time.sleep(retry_time / 1000)


# Configure logging to catch Spotipy warnings
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger('spotipy')

# Add the custom handler to the Spotipy logger
logger.addHandler(RateLimitHandler())


def authenticate() -> Spotify:
    return spotipy.Spotify(auth_manager=SpotifyOAuth(scope=c.SCOPE),
                           requests_timeout=10,
                           retries=0)


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


def get_playlist_tracks(sp: Spotify, playlist: tuple) -> list:
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
            'year':
            year_nbr,
            'track_id':
            item['track']['id'],
            'track_name':
            item['track']['name'],
            'popularity':
            item['track']['popularity'],
            'external_link':
            item['track']['external_urls']['spotify'],
            'album_id':
            item['track']['album']['id'],
            'artist_id':
            item['track']['artists'][0]['id']
        } for item in tracks_page['items']
                       if item.get('track', {}).get('external_urls', {})])

        offset += limit

    print(f"Completed fetching {total_tracks} items for year {year_nbr}")
    return tracks


def get_fact_list(sp: Spotify, year_end_lists: list) -> list:
    year_end_tracks = []

    for item in year_end_lists:
        year_end_tracks.extend(get_playlist_tracks(sp, item))

    return year_end_tracks


def get_dim_album(sp: Spotify, df_fact_table: list) -> list:

    album_ids = [item['album_id'] for item in df_fact_table]
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
                    'album_id':
                    album['id'],
                    'album_name':
                    album['name'],
                    'label':
                    album['label'],
                    'external_link':
                    album['external_urls']['spotify']
                }])
        except Exception as e:
            if type(e) == ReadTimeout:
                print('Spotify timed out... trying again...')
            print(e)

    return albums


def get_dim_artist(sp: Spotify, df_fact_table: list) -> list:

    artist_ids = [item['artist_id'] for item in df_fact_table]
    batch_size = 50
    artist_batches = [
        artist_ids[i:i + batch_size]
        for i in range(0, len(artist_ids), batch_size)
    ]

    artists = []
    batch_order = 0
    for batch in artist_batches:
        batch_order += 1
        print(f'Processing {batch_order} of {len(artist_batches)} batches...')
        try:
            batch_result = sp.artists(batch)
            for artist in batch_result['artists']:
                artists.extend([{
                    'artist_id':
                    artist['id'],
                    'artist_name':
                    artist['name'],
                    # 'genres': artist['genres'],
                    'external_link':
                    artist['external_urls']['spotify']
                }])
        except Exception as e:
            print(type(e))
            print(e.args)
            print(e)

    return artists


def postgres_handling(action: str,
                      fact_year_end_track=None,
                      dim_album_data=None,
                      dim_artist_data=None) -> None:
    pg = Postgres()
    if pg.connect():
        if action == 'create':
            try:
                pg.execute_query(c.CREATE_FACT_YEAR_TRACK)
                print('fact table created.')
                pg.execute_query(c.CREATE_DIM_ALBUM)
                print('dim_album table created.')
                pg.execute_query(c.CREATE_DIM_ARTIST)
                print('dim_artist table created.')
            except Exception as e:
                print(e)
        elif action == 'insert':
            try:
                pg.insert_data('fact_year_end_track', fact_year_end_track)
                print('fact table updated with new data.')
                pg.insert_data('dim_album', dim_album_data)
                print('dim_album table updated with new data.')
                pg.insert_data('dim_artist', dim_artist_data)
                print('dim_artist table updated with new data.')
            except Exception as e:
                print(e)
        else:
            print('Action not defined yet.')
