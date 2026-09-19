from django.urls import path

from .views import AlbumDetailView, AlbumListView, ArtistListView, sync_jellyfin

urlpatterns = [
    path("", ArtistListView.as_view(), name="artist_list"),
    path("albums/", AlbumListView.as_view(), name="album_list"),
    path("sync/", sync_jellyfin, name="sync"),
    path("albums/<uuid:pk>/", AlbumDetailView.as_view(), name="album_detail"),
]
