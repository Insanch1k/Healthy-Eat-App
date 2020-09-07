from django.contrib import admin
from .models import Notes
# Register your models here.


@admin.register(Notes)
class AdminNotes(admin.ModelAdmin):
    list_display = ['title', 'body', 'created']


