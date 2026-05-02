import django.core.validators
from django.db import migrations, models

import news.models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0009_auto_20200613_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True,
                upload_to='images',
                validators=[
                    django.core.validators.FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
                    news.models.validate_image_size,
                ],
            ),
        ),
    ]
