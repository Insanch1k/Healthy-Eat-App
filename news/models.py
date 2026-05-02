from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse


def validate_image_size(image):
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError('Image files must be 5 MB or smaller.')


'''Table for description Posts'''


class Post(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=250, unique_for_date='created')
    body = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='images',
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']), validate_image_size],
    )
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


'''Table for description Comments'''


class Comment(models.Model):
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name="comment_author", on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return 'Comment for {}'.format(self.post)
