# ------------------------------------------------------- Imports ------------------------------------------------------
import requests
import json

# --------------------------------------------------- Main Class -------------------------------------------------------
class MusicBrainzAPI:
    def __init__(self, base_url='https://musicbrainz.org/ws/2/'):
        self.base_url = base_url
        self.user_agent = 'MusicBrainz API Client/1.0'

    def search_releases(self, query):
        url = f'{self.base_url}release/?query={query}&fmt=json'
        headers = {'User-Agent': self.user_agent}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if 'releases' in data and len(data['releases']) > 0:
                release_id = data['releases'][0]['id']
                cover_art_url = f'https://coverartarchive.org/release/{release_id}'
                try:
                    cover_art_response = requests.get(cover_art_url)
                    cover_art_response.raise_for_status()
                    return cover_art_response.json()
                except requests.exceptions.RequestException as e:
                    print(f"Error retrieving cover art: {e}")
                    return None
            else:
                print("No releases found.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None

# ----------------------------------------------------- Debug ----------------------------------------------------------
if __name__ == '__main__':
    api = MusicBrainzAPI()
    title = "Tonight (I’m Lovin’ You)"
    artist = "Enrique Iglesias"
    search_results = api.search_releases(f'release:{title} AND artist:{artist}')