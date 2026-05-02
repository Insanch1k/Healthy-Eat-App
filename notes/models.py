from django.conf import settings
from django.db import models


class Note(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notes",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.title
