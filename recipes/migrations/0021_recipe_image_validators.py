import django.core.validators
from django.db import migrations, models

import recipes.models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_modernize_recipe_indexes_and_user_relations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(
                blank=True,
                upload_to='recipe/%Y/%m/%d',
                validators=[
                    django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
                    recipes.models.validate_image_size,
                ],
            ),
        ),
    ]
