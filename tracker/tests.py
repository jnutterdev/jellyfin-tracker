from django.test import TestCase
from django.urls import reverse

# Create your tests here.
from .models import Album, Artist


class ArtistTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create()

    def test_artist_is_not_null(self):
        self.assertIsNotNone(self.artist)


class AlbumTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.artist = Artist.objects.create()
        cls.album = Album.objects.create(artist=cls.artist)

    def test_album_is_not_null(self):
        self.assertIsNotNone(self.album)
