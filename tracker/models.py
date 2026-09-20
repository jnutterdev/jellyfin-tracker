import uuid

from django.db import models
from django.db.models.functions import Lower


# Create your models here.
class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jellyfin_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = [Lower("name")]

    def __str__(self):
        return self.name


class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jellyfin_id = models.CharField(max_length=64, unique=True, db_index=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="albums")
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    production_year = models.IntegerField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True)  # Jellyfin's DateCreated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = [Lower("artist__name"), Lower("name")]

    def __str__(self):
        return f"{self.artist} - {self.name}"


class Track(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jellyfin_id = models.CharField(max_length=64, unique=True, db_index=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="tracks")
    name = models.CharField(max_length=255)
    track_number = models.IntegerField(null=True, blank=True)
    disc_number = models.IntegerField(null=True, blank=True)
    duration_seconds = models.IntegerField(null=True, blank=True)
    container = models.CharField(max_length=16, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["disc_number", "track_number"]

    def __str__(self):
        return self.name
