from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

'''Table for description Notes'''

class Notes(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name="owner", on_delete=models.CASCADE, blank=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return self.title
