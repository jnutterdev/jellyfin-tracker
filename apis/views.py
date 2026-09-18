from rest_framework import generics

from tracker.models import Artist

from .serializers import ArtistSerializer


class ArtistAPIView(generics.ListAPIView):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
