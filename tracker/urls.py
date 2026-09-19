from django.urls import path

from .views import AlbumListView, ArtistListView

urlpatterns = [
    path("", ArtistListView.as_view()),
    path("albums/", AlbumListView.as_view()),
]
