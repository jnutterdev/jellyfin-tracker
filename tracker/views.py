# from django.shortcuts import render
from django.views.generic import ListView

from .models import Album, Artist


# Create your views here.
class ArtistListView(ListView):
    paginate_by = 20
    model = Artist


class AlbumListView(ListView):
    paginate_by = 20
    model = Album
