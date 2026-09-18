from django.contrib import admin

# Register your models here.
from .models import Album, Artist

admin.site.register(Album)
admin.site.register(Artist)
