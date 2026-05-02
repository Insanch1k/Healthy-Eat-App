from django.contrib import admin

from .models import Note


@admin.register(Note)
class AdminNotes(admin.ModelAdmin):
    list_display = ['title', 'body', 'created']

