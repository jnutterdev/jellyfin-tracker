from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from django_q.tasks import async_task

from .jellyfin_sync import sync_tracks_for_album
from .models import Album, Artist, Playlist


class ArtistListView(ListView):
    paginate_by = 20
    model = Artist

    def get_queryset(self):
        queryset = Artist.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset


class ArtistDetailView(DetailView):
    model = Artist


class AlbumListView(ListView):
    paginate_by = 20
    model = Album

    def get_queryset(self):
        queryset = Album.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset


class AlbumDetailView(DetailView):
    model = Album

    def get_object(self, queryset=None):
        album = super().get_object(queryset)
        if not album.tracks.exists():
            sync_tracks_for_album(album)
        return album


class PlaylistListView(ListView):
    model = Playlist
    paginate_by = 20

    def get_queryset(self):
        queryset = Playlist.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset


class PlaylistDetailView(DetailView):
    model = Playlist


@require_POST
def sync_jellyfin(request):
    async_task("tracker.jellyfin_sync.sync_all")
    return redirect("artist_list")
