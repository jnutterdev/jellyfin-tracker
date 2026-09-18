from rest_framework import serializers

from tracker.models import Artist


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ("id", "jellyfin_id", "name")
