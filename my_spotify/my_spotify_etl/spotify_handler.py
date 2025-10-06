import spotipy
from spotipy.oauth2 import SpotifyOAuth
import constants as c
import time


class SpotifyHandler:
    def __init__(self):
        self.scope = c.SCOPE
        self.user_id = c.USER_ID
        self.sp = None

    def authenticate(self) -> None:
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))

    def get_user_playlists(self) -> list:
        all_playlists = []
        limit = 50
        offset = 0

        if self.sp is not None:
            user_playlists_response = self.sp.user_playlists(self.user_id)

            if user_playlists_response is not None:
                total_nbr_of_playlists = user_playlists_response["total"]

                while offset < total_nbr_of_playlists:
                    user_playlists_page = self.sp.user_playlists(
                        self.user_id, limit=limit, offset=offset
                    )
                    if user_playlists_page is not None:
                        all_playlists.extend(user_playlists_page["items"])

                    offset += limit

        return all_playlists

    def get_year_end_list(self, user_playlist: list) -> list:
        year_end_lists = [
            (playlist["name"], playlist["id"])
            for playlist in user_playlist
            if "billboard year end hot 100" in playlist["name"].lower()
        ]
        return year_end_lists

    def get_playlist_tracks(self, playlist: tuple) -> list:
        tracks = []
        limit = 100
        offset = 0
        year_nbr = playlist[0][0:4]

        print(f"Fetching playlist tracks for year {year_nbr}...")
        if self.sp is not None:
            playlist_tracks_response = self.sp.playlist_tracks(playlist[1])
            if playlist_tracks_response is not None:
                total_tracks = playlist_tracks_response["total"]

                request_count = 1

                while offset < total_tracks:
                    tracks_page = None
                    try:
                        tracks_page = self.sp.playlist_items(
                            playlist[1], limit=limit, offset=offset
                        )
                        time.sleep(2)
                    except Exception as e:
                        print(e)

                    if tracks_page is not None:
                        request_count += 1

                        tracks.extend(
                            [
                                {
                                    "year": year_nbr,
                                    "track_id": item["track"]["id"],
                                    "track_name": item["track"]["name"],
                                    "popularity": item["track"]["popularity"],
                                    "external_link": item["track"]["external_urls"][
                                        "spotify"
                                    ],
                                    "album_id": item["track"]["album"]["id"],
                                    "artist_id": item["track"]["artists"][0]["id"],
                                    "track_image": item["track"]["preview_url"]
                                    if item["track"]["preview_url"] is not None
                                    else "No preview available",
                                }
                                for item in tracks_page["items"]
                                if item.get("track", {}).get("external_urls", {})
                            ]
                        )

                    offset += limit

                print(f"Completed fetching {total_tracks} items for year {year_nbr}")
        return tracks

    def get_fact_list(self, year_end_lists: list) -> list:
        year_end_tracks = []

        for item in year_end_lists:
            year_end_tracks.extend(self.get_playlist_tracks(item))

        return year_end_tracks

    def get_dim_album(self, df_fact_table: list) -> list:
        album_ids = [item["album_id"] for item in df_fact_table]
        batch_size = 20
        album_batches = [
            album_ids[i : i + batch_size] for i in range(0, len(album_ids), batch_size)
        ]

        albums = []
        batch_order = 0
        for batch in album_batches:
            batch_order += 1
            print(f"Processing {batch_order} of {len(album_batches)} batches...")
            if self.sp is not None:
                try:
                    batch_result = self.sp.albums(batch)
                    time.sleep(5)
                    if batch_result is not None:
                        for album in batch_result["albums"]:
                            albums.extend(
                                [
                                    {
                                        "album_id": album["id"],
                                        "album_name": album["name"],
                                        "label": album["label"],
                                        "external_link": album["external_urls"][
                                            "spotify"
                                        ],
                                        "album_image": album["images"][0]["url"]
                                        if album["images"]
                                        else "No image available",
                                        "artist_name": album["artists"][0]["name"],
                                    }
                                ]
                            )
                except spotipy.exceptions.SpotifyException as e:
                    print(f"An unexpected error occurred: {e}")
                    raise

        return albums

    def get_dim_artist(self, df_fact_table: list) -> list:
        artist_ids = [item["artist_id"] for item in df_fact_table]
        batch_size = 50
        artist_batches = [
            artist_ids[i : i + batch_size]
            for i in range(0, len(artist_ids), batch_size)
        ]

        artists = []
        batch_order = 0
        for batch in artist_batches:
            batch_order += 1
            print(f"Processing {batch_order} of {len(artist_batches)} batches...")
            if self.sp is not None:
                try:
                    batch_result = self.sp.artists(batch)
                    time.sleep(5)
                    if batch_result is not None:
                        for artist in batch_result["artists"]:
                            artists.extend(
                                [
                                    {
                                        "artist_id": artist["id"],
                                        "artist_name": artist["name"],
                                        # 'genres': artist['genres'],
                                        "external_link": artist["external_urls"][
                                            "spotify"
                                        ],
                                        "artist_image": artist["images"][0]["url"]
                                        if artist["images"]
                                        else "No image available",
                                    }
                                ]
                            )
                except Exception as e:
                    print(type(e))
                    print(e.args)
                    print(e)

        return artists
