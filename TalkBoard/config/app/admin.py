from django.contrib import admin
from app import models

# Register your models here.

admin.site.register(models.Board)
admin.site.register(models.Comment)
admin.site.register(models.Favorite)
admin.site.register(models.Contact)
admin.site.register(models.Profile)