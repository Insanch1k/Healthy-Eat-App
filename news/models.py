from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# Create your models here.


class Post(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=250, unique_for_date='created')
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to='images', blank=True)
    video = models.URLField(blank=True)
    author = models.ForeignKey(User, related_name="author", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:article_detail', args=[self.id, self.slug])


class Comment(models.Model):
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name="comment_author", on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return 'Comment for {}'.format(self.post)
