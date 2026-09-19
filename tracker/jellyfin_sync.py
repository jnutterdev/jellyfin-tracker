from .jellyfin_client import fetch_items
from .models import Album, Artist


def sync_artists() -> None:
    start_index = 0
    limit = 100

    while True:
        response = fetch_items("MusicArtist", start_index, limit)
        for item in response["Items"]:
            Artist.objects.update_or_create(
                jellyfin_id=item["Id"],
                defaults={"name": item["Name"]},
            )
        start_index += limit
        if start_index >= response["TotalRecordCount"]:
            break


def sync_albums() -> None:
    start_index = 0
    limit = 100

    while True:
        response = fetch_items("MusicAlbum", start_index, limit)
        for item in response["Items"]:
            artist_list = (
                item["AlbumArtists"] if item["AlbumArtists"] else item["ArtistItems"]
            )

            if artist_list:
                artist = Artist.objects.get(jellyfin_id=artist_list[0]["Id"])
            else:
                artist, created = Artist.objects.get_or_create(
                    jellyfin_id="unknown",
                    defaults={"name": "Unknown Artist"},
                )

            Album.objects.update_or_create(
                jellyfin_id=item["Id"],
                defaults={
                    "name": item["Name"],
                    "artist": artist,
                    "production_year": item.get("ProductionYear"),
                    "date_added": item.get("DateCreated"),
                },
            )

        start_index += limit
        if start_index >= response["TotalRecordCount"]:
            break
