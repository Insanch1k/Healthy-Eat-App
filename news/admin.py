from django.contrib import admin

from .models import Comment, Post

# Register your models here.


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created', 'updated', 'body', 'image', 'video', 'author')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created'
    search_fields = ('title', 'body')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('body', 'created', 'post')
    search_fields = ('body', 'post')

