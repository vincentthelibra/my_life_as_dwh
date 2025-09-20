import os
import time

import requests
from dotenv import load_dotenv


class GenreHandler_Two:
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

    def get_genre_by_album(
        self,
        album_id: str | None = None,
        album_name: str | None = None,
        artist_name: str | None = None,
        timeout: int = 30,
    ) -> str | None:
        if not self.genre_access_token:
            raise ValueError("Must authenticate first before making API calls")

        url = "https://api.getgenre.com/search"

        params: dict[str, str | int] = {"timeout": timeout}

        if album_id:
            params["album_id"] = album_id
        if album_name:
            params["album_name"] = album_name
        if artist_name:
            params["artist_name"] = artist_name

        headers = self.get_auth_headers()

        display_parts = []
        if album_name:
            display_parts.append(f"Album: {album_name}")
        if artist_name:
            display_parts.append(f"Artist: {artist_name}")
        if album_id and not display_parts:
            display_parts.append(f"Album ID: {album_id}")
        display_name = ", ".join(display_parts)

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            genre_data = response.json()
            top_genres = genre_data.get("top_genres", [])
            first_genre = top_genres[0] if top_genres else None
            print(
                f"Successfully retrieved genre data for {display_name}: {first_genre}"
            )
            return first_genre

        except requests.exceptions.RequestException as e:
            print(f"Error getting genre for {display_name}: {e}")
            raise
        except ValueError as e:
            print(f"Error parsing JSON response: {e}")
            raise

    def get_genres_for_albums(self, albums: list[dict], timeout: int = 30) -> list:
        if not self.genre_access_token:
            raise ValueError("Must authenticate first before making API calls")

        results = []

        for i, album in enumerate(albums, 1):
            print(f"Processing album {i} of {len(albums)}: {album['album_name']}")

            try:
                genre = self.get_genre_by_album(
                    album_name=album["album_name"],
                    artist_name=album["artist_name"],
                    timeout=timeout,
                )

                # Final fallback to artist name only
                if not genre:
                    genre = self.get_genre_by_album(
                        artist_name=album["artist_name"], timeout=timeout
                    )

                results.append({"album_id": album["album_id"], "genre": genre})

                time.sleep(0.5)

            except Exception as e:
                print(f"Failed to get genre for album {album['album_id']}: {e}")
                results.append({"album_id": album["album_id"], "genre": None})

        return results
