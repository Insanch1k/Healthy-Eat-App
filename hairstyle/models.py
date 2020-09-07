from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('hairstyle:recipes_by', args = [self.slug])

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey(Category, related_name='recipes', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='recipe/%Y/%m/%d', blank=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ingredients = models.TextField(blank=True)
    step1 = models.TextField(blank=True)
    step2 = models.TextField(blank=True)
    step3 = models.TextField(blank=True)
    step4 = models.TextField(blank=True)
    servings = models.IntegerField(default=2)
    sugar = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    calories = models.IntegerField(blank=True, default=1)
    protein = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    carbohydrates = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    fat = models.DecimalField(max_digits=4, decimal_places=1, default=1)
    favorite = models.ManyToManyField(User, related_name='favorite',  blank=True)

    class Meta:
        ordering = ('-created',)
        index_together = (('id', 'slug'),)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('hairstyle:recipe_detail', args=[self.id,self.slug])


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=13, blank=True)

    def __str__(self):
        return f'Profile for {self.user.username}'

