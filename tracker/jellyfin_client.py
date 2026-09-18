import json
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

url = settings.JELLYFIN_BASE_URL
token = settings.JELLYFIN_API_KEY
headers = {"Authorization": f'MediaBrowser Token="{token}"'}

artist_items_param = {
    "includeItemTypes": "MusicArtist",
    "recursive": "true",
    "startIndex": "0",
    "limit": "100",
}

get_artists = urllib.parse.urlencode(artist_items_param)

full_url = f"{url}/Items?{get_artists}"


request = urllib.request.Request(full_url, headers=headers)

try:
    with urllib.request.urlopen(request) as response:
        print("status:", response.status)
        data = json.loads(response.read())
        print("data:", data)
except Exception as e:
    print("ERROR:", type(e).__name__, e)
