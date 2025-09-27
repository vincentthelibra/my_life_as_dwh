import time
import xml.etree.ElementTree as ET
import requests


class MusicBrainzHandler:
    def __init__(self):
        self.baseurl = "https://musicbrainz.org/ws/2/release/"

    def searchByRelease(self, release_name):
        query_param = str.replace(release_name, " ", "%20")
        url = f"{self.baseurl}?query=release:{query_param}"

        headers = {"User-Agent": "python-musicbrainz/0.7.3"}

        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            print(f"Error response: {response.text}")
            return None

        root = ET.fromstring(response.text)
        namespaces = {
            "ns": "http://musicbrainz.org/ns/mmd-2.0#",
            "ns2": "http://musicbrainz.org/ns/ext#-2.0",
        }

        releases = root.findall('.//ns:release[@ns2:score="100"]', namespaces)

        valid_releases = []
        for release in releases:
            release_id = release.get("id")

            tag_list = release.find("ns:tag-list", namespaces)
            if tag_list is None or len(tag_list) == 0:
                continue

            first_tag = tag_list.find("ns:tag/ns:name", namespaces)
            if first_tag is not None and first_tag.text:
                genre = first_tag.text.strip()
                print(f"Found genre '{genre}' for release {release_id}")
            else:
                continue

            valid_releases.append((release_id, genre))

        if not valid_releases:
            print("No valid releases found with genre information")
            return None

        print(f"Returning genre: {valid_releases[0][1]}")
        return valid_releases[0][1]

    def get_genres_for_albums(self, albums):
        results = []
        for i, album in enumerate(albums, 1):
            print(f"\nProcessing album {i} of {len(albums)}: {album['album_name']}")
            try:
                genre = self.searchByRelease(album["album_name"])
                results.append({"album_id": album["album_id"], "genre": genre})
                time.sleep(0.5)
            except Exception as e:
                print(f"Failed to get genre for album {album['album_name']}: {e}")
                results.append({"album_id": album["album_id"], "genre": None})
        return results
