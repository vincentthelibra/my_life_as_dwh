import time
import xml.etree.ElementTree as ET
import requests


class MusicBrainzHandler:
    def __init__(self):
        self.baseurl = "https://musicbrainz.org/ws/2/release/"

    def searchByRelease(self, release_name):
        # Fix the typo in the query parameter (was "releare", should be "release")
        query_param = str.replace(release_name, " ", "%20")
        url = f"{self.baseurl}?query=release:{query_param}"

        headers = {"User-Agent": "MusicBrainzTestScript/1.0"}

        print(f"Searching for: {release_name}")
        print(f"URL: {url}")

        response = requests.request("GET", url, headers=headers)
        print(f"Response status: {response.status_code}")

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return None

        root = ET.fromstring(response.text)
        namespaces = {
            "ns": "http://musicbrainz.org/ns/mmd-2.0#",
            "ns2": "http://musicbrainz.org/ns/ext#-2.0",
        }

        # Only get releases with score 100
        releases = root.findall('.//ns:release[@ns2:score="100"]', namespaces)
        print(f"Found {len(releases)} releases with score 100")

        valid_releases = []
        for release in releases:
            release_id = release.get("id")

            date_elem = release.find("ns:date", namespaces)
            if date_elem is not None and date_elem.text:
                date_str = date_elem.text.strip()
            else:
                print(f"Skipping release {release_id}: no date")
                continue

            tag_list = release.find("ns:tag-list", namespaces)
            if tag_list is None or len(tag_list) == 0:
                print(f"Skipping release {release_id}: no tags")
                continue

            first_tag = tag_list.find("ns:tag/ns:name", namespaces)
            if first_tag is not None and first_tag.text:
                genre = first_tag.text.strip()
                print(f"Found genre '{genre}' for release {release_id}")
            else:
                print(f"Skipping release {release_id}: no genre tag")
                continue

            valid_releases.append((release_id, date_str, genre))

        if not valid_releases:
            print("No valid releases found with genre information")
            return None

        # No sorting - use API order (most relevant first)
        print("Using first result from API order")
        print(f"Returning genre: {valid_releases[0][2]}")
        return valid_releases[0][2]

    def get_genres_for_albums(self, albums):
        results = []
        for i, album in enumerate(albums, 1):
            print(f"\nProcessing album {i} of {len(albums)}: {album['album_name']}")
            try:
                genre = self.searchByRelease(album["album_name"])
                results.append({"album_id": album["album_id"], "genre": genre})
                time.sleep(1)  # Be respectful to the API
            except Exception as e:
                print(f"Failed to get genre for album {album['album_name']}: {e}")
                results.append({"album_id": album["album_id"], "genre": None})
        return results


# Test the functionality
if __name__ == "__main__":
    handler = MusicBrainzHandler()

    # Test with some well-known albums
    test_albums = [
        {"album_id": 1, "album_name": "Abbey Road"},
        {"album_id": 2, "album_name": "Dark Side of the Moon"},
        {"album_id": 3, "album_name": "Thriller"},
        {"album_id": 4, "album_name": "Nevermind"},
    ]

    print("Testing individual album search:")
    print("=" * 50)

    # Test single album first
    # test_album = "Abbey Road"
    # genre = handler.searchByRelease(test_album)
    # print(f"\nResult: '{test_album}' -> Genre: {genre}")
    #
    # print("\n" + "=" * 50)
    # print("Testing batch processing:")
    # print("=" * 50)

    # Test batch processing (comment out if you want to test just one)
    results = handler.get_genres_for_albums(test_albums)

    print("\nFinal Results:")
    for result in results:
        print(f"Album ID {result['album_id']}: {result['genre']}")
