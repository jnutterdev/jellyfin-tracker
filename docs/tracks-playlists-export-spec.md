# Tracks, Playlists, and Car Export — Feature Spec (Next Session)

Three related features, meant to be tackled in order since each builds on the
last: tracks must exist locally before playlists can reference them, and
playlists must exist before there's anything to export.

## 1. Album Detail Page (Track List)

**Goal:** clicking an album shows its track list.

**New model — `Track`:**

```python
class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jellyfin_id = models.CharField(max_length=64, unique=True, db_index=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="tracks")
    name = models.CharField(max_length=255)
    track_number = models.IntegerField(null=True, blank=True)  # Jellyfin's IndexNumber
    disc_number = models.IntegerField(null=True, blank=True)   # Jellyfin's ParentIndexNumber
    duration_seconds = models.IntegerField(null=True, blank=True)  # RunTimeTicks / 10,000,000
    container = models.CharField(max_length=16, blank=True)  # e.g. "mp3", confirmed field exists
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["disc_number", "track_number"]
```

**Jellyfin endpoint (confirmed working):**
`GET /Items?parentId={album.jellyfin_id}&includeItemTypes=Audio&recursive=true`
— verified live against the server; returns `IndexNumber`, `Name`, `Container`,
`RunTimeTicks` per track exactly as expected. Note Jellyfin's `RunTimeTicks`
are in 100-nanosecond units — divide by 10,000,000 for seconds.

**Open decision:** sync tracks eagerly (as part of `sync_all()`, one API call
per album — ~1,115+ requests, meaningfully slower) vs. lazily (fetch + cache
only when a user actually opens that album's detail page). Given most albums
in a library this size won't be viewed in any given session, lazy-on-view
with local caching is probably the better default — decide at the start of
next session.

**New view/URL:** `AlbumDetailView(DetailView)`, `path("albums/<uuid:pk>/", ...)`.
Update `album_list.html` so each `<li>` links to its detail page.

## 2. Playlist Builder

**New models:**

```python
class Playlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


class PlaylistTrack(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name="playlist_tracks")
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    position = models.IntegerField()  # drives play order

    class Meta:
        ordering = ["position"]
```

**Views needed:**

- `PlaylistListView` — a dedicated `/playlists/` page, same pattern as
  `ArtistListView`/`AlbumListView` (paginated, alphabetical by name, linked
  from `.site-nav` alongside Artists/Albums).
- Create a playlist.
- `PlaylistDetailView` — view a single playlist's ordered tracks.
- Add a track to a playlist (button from the album detail page).
- Remove a track, reorder tracks.

**Reorder UX:** Sortable.js (vanilla JS, no framework, no build step — new
dependency but a lightweight one). It operates directly on the existing
server-rendered `<ul>` of tracks; on drop, a small `fetch()` POST updates
each `PlaylistTrack.position` via a new Django endpoint. Deliberately not
using a framework like Preact/React here — that would mean converting just
this one page to client-rendered while everything else in the app stays
server-rendered Django templates, an inconsistent split not justified by
this feature.

## 3. MP3 Export for USB / Car Playback (investigate)

**Confirmed feasible:** Jellyfin exposes `GET /Items/{itemId}/Download`
(verified in the OpenAPI spec — not deprecated, single `itemId` param) which
returns the original media file for a track. This is the endpoint to use for
downloading actual audio files.

**Confirmed via a live check:** spot-checked one album's tracks
(`(ghost) - Everything We Touch Turns To Dust`) and every track already has
`Container: "mp3"` — no transcoding needed for at least that album. First
step next session: scan the full library's `Container` values to see if
everything is already mp3, or if some albums are FLAC/other formats (which
would need `ffmpeg` transcoding — a much bigger addition: new dependency,
processing time, bitrate/quality decisions).

**Car-specific consideration worth remembering:** most car head units read
files off a USB drive in filename alphabetical order, not by embedded
metadata or playlist order. Exported filenames will likely need a numeric
prefix derived from `PlaylistTrack.position` (e.g. `01 - Track Name.mp3`) so
the car actually plays them in the intended order.

**Open decisions for next session:**
1. Confirm library-wide file format mix (mp3 vs. other).
2. Where should exported files land — a fixed local folder, or a
   user-chosen path each time? (App is local-only, so direct filesystem
   writes are on the table, no cloud/browser-download complexity needed.)
3. Export as a synchronous action, or a background task like `sync_all()`
   (relevant if playlists get large — copying many files could take a while)?
