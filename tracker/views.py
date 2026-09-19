from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from django_q.tasks import async_task

from .models import Album, Artist


class ArtistListView(ListView):
    paginate_by = 20
    model = Artist

    def get_queryset(self):
        queryset = Artist.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset


class AlbumListView(ListView):
    paginate_by = 20
    model = Album

    def get_queryset(self):
        queryset = Album.objects.all()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset


@require_POST
def sync_jellyfin(request):
    async_task("tracker.jellyfin_sync.sync_all")
    return redirect("artist_list")
