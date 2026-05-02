from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.urls import reverse


def validate_image_size(image):
    max_size = 5 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError('Image files must be 5 MB or smaller.')


class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True)
    slug = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes:recipes_by', args=[self.slug])


class Recipe(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey(Category, related_name='recipes', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(
        upload_to='recipe/%Y/%m/%d',
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']), validate_image_size],
    )
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
    favorite = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_recipes',
        blank=True,
    )

    class Meta:
        ordering = ('-created',)
        indexes = [
            models.Index(fields=['id', 'slug'], name='recipe_id_slug_idx'),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipes:recipe_detail', args=[self.id, self.slug])


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format '+123456789'. Up to 15 .",
    )
    phone = models.CharField(validators=[phone_regex], max_length=15)

    def __str__(self):
        return f'Profile for {self.user.username}'
