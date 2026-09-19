import json
import urllib.parse
import urllib.request

from django.conf import settings

url = settings.JELLYFIN_BASE_URL
token = settings.JELLYFIN_API_KEY
headers = {"Authorization": f'MediaBrowser Token="{token}"'}


def fetch_items(include_item_types: str, start_index: int, limit: int) -> dict:
    fetched_items_object = {
        "includeItemTypes": include_item_types,
        "startIndex": start_index,
        "limit": limit,
        "recursive": "true",
    }
    encoded_items = urllib.parse.urlencode(fetched_items_object)
    full_url = f"{url}/Items?{encoded_items}"
    request = urllib.request.Request(full_url, headers=headers)

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read())
        return data
