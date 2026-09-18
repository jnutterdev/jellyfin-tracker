# from django.shortcuts import render
from django.views.generic import ListView

from .models import Album, Artist


# Create your views here.
class ArtistListView(ListView):
    model = Artist
    template_name = "artist_list.html"


class AlbumListView(ListView):
    model = Album
    template_name = "album_list.html"
