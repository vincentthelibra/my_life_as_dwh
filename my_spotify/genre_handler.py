import os
import time

import requests
from dotenv import load_dotenv


class GenreHandler:
    def __init__(self, env_file=".env"):
        load_dotenv(env_file)
        self.username = os.getenv("GENRE_API_USERNAME")
        self.password = os.getenv("GENRE_API_PASSWORD")

        self.genre_access_token = None
        self.genre_refresh_token = None
        self.genre_token_type = None
        self.genre_handler = None

    def authenticate(self) -> dict:
        """
        Authenticate with the Genre API and return the token response
        """
        url = "https://api.getgenre.com/token"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        payload = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "remember_me": True,
            "refresh_token": "",
        }

        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            token_data = response.json()

            self.genre_access_token = token_data.get("access_token")
            self.genre_refresh_token = token_data.get("refresh_token")
            self.genre_token_type = token_data.get("token_type", "Bearer")

            print("Genre API authentication successful")
            return token_data

        except requests.exceptions.RequestException as e:
            print(f"Error authenticating with Genre API: {e}")
            raise
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            raise

    def get_auth_headers(self) -> dict:
        """
        Get authorization headers for authenticated API calls

        Returns:
            dict: Headers with authorization token
        """
        if not self.genre_access_token:
            raise ValueError("Must authenticate first before making API calls")

        return {
            "Authorization": f"{self.genre_token_type} {self.genre_access_token}",
            "accept": "application/json",
        }

    def get_genre_by_album_id(
        self, album_name: str, artist_name: str, timeout: int = 30
    ) -> str | None:
        if not self.genre_access_token:
            raise ValueError("Must authenticate first before making API calls")

        url = "https://api.getgenre.com/search"

        params = {
            "album_name": album_name,
            "artist_name": artist_name,
            "timeout": timeout,
        }

        headers = self.get_auth_headers()

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            genre_data = response.json()
            top_genres = genre_data.get("top_genres", [])
            first_genre = top_genres[0] if top_genres else None
            print(f"Successfully retrieved genre data for album: {album_name}")
            return first_genre

        except requests.exceptions.RequestException as e:
            print(f"Error getting genre for album {album_name}: {e}")
            raise
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            raise

    def get_genres_for_albums(self, albums: list, timeout: int = 30) -> list:
        if not self.genre_access_token:
            raise ValueError("Must authenticate first before making API calls")

        results = []

        for i, album in enumerate(albums, 1):
            print(f"Processing album {i} of {len(albums)}: {album}")

            try:
                genre = self.get_genre_by_album_id(
                    album.album_name, album.artist_name, timeout
                )
                results.append({"album_id": album.album_id, "genre": genre})

                time.sleep(0.5)  # 500ms delay between requests

            except Exception as e:
                print(f"Failed to get genre for album {album.album_id}: {e}")
                results.append({"album_id": album.album_id, "genre": None})

        return results
