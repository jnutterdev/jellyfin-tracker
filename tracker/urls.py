from django.urls import path

from .views import (
    AlbumDetailView,
    AlbumListView,
    ArtistDetailView,
    ArtistListView,
    sync_jellyfin,
)

urlpatterns = [
    path("", ArtistListView.as_view(), name="artist_list"),
    path("albums/", AlbumListView.as_view(), name="album_list"),
    path("sync/", sync_jellyfin, name="sync"),
    path("albums/<slug:slug>/", AlbumDetailView.as_view(), name="album_detail"),
    path("artists/<slug:slug>/", ArtistDetailView.as_view(), name="artist_detail"),
]
