from django.utils.text import slugify

from .jellyfin_client import fetch_items
from .models import Album, Artist, Track


def sync_artists() -> None:
    start_index = 0
    limit = 100

    while True:
        response = fetch_items("MusicArtist", start_index, limit)
        for item in response["Items"]:
            name = item["Name"].strip()
            Artist.objects.update_or_create(
                jellyfin_id=item["Id"],
                defaults={
                    "name": name,
                    "slug": unique_slug(Artist, slugify(name), item["Id"]),
                },
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
                artist, _ = Artist.objects.get_or_create(
                    jellyfin_id="unknown",
                    defaults={"name": "Unknown Artist"},
                )

            name = item["Name"].strip()
            artist_and_album = f"{artist.name}-{name}"
            Album.objects.update_or_create(
                jellyfin_id=item["Id"],
                defaults={
                    "name": name,
                    "slug": unique_slug(Album, slugify(artist_and_album), item["Id"]),
                    "artist": artist,
                    "production_year": item.get("ProductionYear"),
                    "date_added": item.get("DateCreated"),
                },
            )

        start_index += limit
        if start_index >= response["TotalRecordCount"]:
            break


def sync_all() -> None:
    sync_artists()
    sync_albums()


def sync_tracks_for_album(album: Album) -> None:
    fetched_items = fetch_items("Audio", 0, 100, parent_id=album.jellyfin_id)

    for item in fetched_items["Items"]:
        run_time_ticks = item.get("RunTimeTicks")
        duration_seconds = (
            run_time_ticks // 10_000_000 if item.get("RunTimeTicks") else None
        )
        Track.objects.update_or_create(
            jellyfin_id=item["Id"],
            defaults={
                "disc_number": item.get("ParentIndexNumber"),
                "track_number": item.get("IndexNumber"),
                "album": album,
                "name": item.get("Name"),
                "duration_seconds": duration_seconds,
                "container": item.get("Container"),
            },
        )


def unique_slug(model, base_slug: str, jellyfin_id: str) -> str:
    if model.objects.filter(slug=base_slug).exclude(jellyfin_id=jellyfin_id).exists():
        return f"{base_slug}-{jellyfin_id[:8]}"
    return base_slug
