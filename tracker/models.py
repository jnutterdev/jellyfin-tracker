import uuid

from django.db import models
from django.db.models.functions import Lower


# Create your models here.
class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jellyfin_id = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=255)
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
    production_year = models.IntegerField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True)  # Jellyfin's DateCreated
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = [Lower("artist__name"), Lower("name")]

    def __str__(self):
        return f"{self.artist} - {self.name}"
