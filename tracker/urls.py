from django.urls import path

from .views import (
    AlbumDetailView,
    AlbumListView,
    ArtistDetailView,
    ArtistListView,
    PlaylistDetailView,
    PlaylistListView,
    sync_jellyfin,
)

urlpatterns = [
    path("", ArtistListView.as_view(), name="artist_list"),
    path("albums/", AlbumListView.as_view(), name="album_list"),
    path("sync/", sync_jellyfin, name="sync"),
    path("playlists/", PlaylistListView.as_view(), name="playlist_list"),
    path("albums/<slug:slug>/", AlbumDetailView.as_view(), name="album_detail"),
    path("artists/<slug:slug>/", ArtistDetailView.as_view(), name="artist_detail"),
    path("playlists/<slug:slug>", PlaylistDetailView.as_view(), name="playlist_detail"),
]
