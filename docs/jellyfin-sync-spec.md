# Jellyfin Sync — Tech Spec

## Goal

Let a user trigger (via a button in the UI) a sync that pulls Artists and Albums
from a Jellyfin server into the local `tracker` models, keyed on `jellyfin_id`.

## Auth / Config

Already in place, no changes needed:

- `JELLYFIN_BASE_URL` and `JELLYFIN_API_KEY` are read from environment variables
  in `django_project/settings.py` via `python-dotenv`.

## HTTP Client

Use `urllib.request` (stdlib) — no new dependency. The calls are simple
authenticated GET requests returning JSON; no need for sessions, retries, or
streaming, so `requests` isn't warranted here.

Jellyfin auth (confirmed via this server's `/api-docs/openapi.json`): pass the
API key via the `Authorization` header, formatted as
`Authorization: MediaBrowser Token="<api_key>"`. (A `?api_key=<key>` query
param also works as a fallback on most Jellyfin versions, if preferred.)

## Background Execution: Django-Q2

The library is large enough that a single request/response cycle isn't a good
fit — pagination alone doesn't solve a slow request potentially exceeding a
production WSGI worker timeout (gunicorn). Instead, the button enqueues a
background task and returns immediately.

**New dependency:** `django-q2` (PyPI: `django-q2`, import name `django_q`).
Chosen over Celery because it can use the existing SQLite DB as its broker
(`Q_CLUSTER = {"orm": "default"}`) — no Redis/RabbitMQ needed, consistent with
the "SQLite until it doesn't fit" default.

Settings changes needed in `django_project/settings.py`:

```python
INSTALLED_APPS = [
    ...
    "django_q",
]

Q_CLUSTER = {
    "name": "jellyfin_tracker",
    "orm": "default",
}
```

After adding the dependency, `migrate` is needed to create `django_q`'s
tables, and a separate worker process must be running for tasks to actually
execute: `manage.py qcluster`. Locally that's a second terminal; in
production (Railway/Fly/Render) it needs its own supervised process
alongside the web process — this is a deploy-config change to account for
later, not just a code change.

## File Layout

- `tracker/jellyfin_client.py` — low-level HTTP calls to the Jellyfin API.
  Typed functions that hit a paginated endpoint (`startIndex`/`limit`) and
  return parsed JSON. No Django ORM code here.
- `tracker/jellyfin_sync.py` — orchestration layer: `sync_artists()` and
  `sync_albums()`, each paging through results via `startIndex`/`limit` and
  `update_or_create()`-ing local rows keyed by `jellyfin_id`. Also
  `sync_all()`, which just calls `sync_artists()` then `sync_albums()` in
  order (artists must sync first since `Album` has a required FK to
  `Artist`) — this is the function actually handed to the task queue.
- `tracker/views.py` — a POST-only view (e.g. `SyncJellyfinView`) that calls
  `django_q.tasks.async_task("tracker.jellyfin_sync.sync_all")` and redirects
  back to the list page immediately (doesn't wait for the task to finish).
- `tracker/urls.py` — new `sync/` path wired to that view.
- Template — a `<form method="post">` with `{% csrf_token %}` wrapping the
  sync button (plain `<button type="submit">`, no JS needed for v1). A
  "last synced" or "sync in progress" indicator is a nice-to-have follow-up,
  not required for v1 — `django_q.models.Task` can be queried by the task id
  `async_task()` returns if we want that later.

## Data Flow

1. `GET /Items?includeItemTypes=MusicArtist&recursive=true` → for each item,
   `Artist.objects.update_or_create(jellyfin_id=item["Id"], defaults={"name": item["Name"]})`.
2. `GET /Items?includeItemTypes=MusicAlbum&recursive=true` → for each item,
   look up the already-synced `Artist` via `item["AlbumArtists"][0]["Id"]`
   (falls back to `ArtistItems` if `AlbumArtists` is empty), then
   `Album.objects.update_or_create(jellyfin_id=item["Id"], defaults={"artist": artist, "name": item["Name"], "production_year": item.get("ProductionYear"), "date_added": item.get("DateCreated")})`.

## Confirmed API Details

Pulled directly from `https://media.ashtephra.com/api-docs/openapi.json`:

- `/Artists` and `/Artists/AlbumArtists` are both marked `deprecated: true` in
  this server's spec — don't use them.
- `GET /Items` is the current, non-deprecated endpoint for listing artists
  and albums, filtered via `includeItemTypes`.
- `BaseItemDto` response fields relevant here: `Id` (uuid string), `Name`
  (string), `ProductionYear` (nullable int), `DateCreated` (nullable
  date-time string), `AlbumArtists` (array of `{Name, Id}` pairs), `ArtistItems`
  (same shape, alternate source for artist linkage).

## Error Handling

- Network failure / non-200 response inside `sync_all()`: let it raise.
  Django-Q2 records the failed task (with traceback) in `django_q.models.Task`
  rather than crashing a live request — nothing else to catch by hand.
