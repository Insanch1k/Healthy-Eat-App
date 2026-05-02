from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0019_auto_20200925_1411'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AlterIndexTogether(
                    name='recipe',
                    index_together=set(),
                ),
            ],
            database_operations=[],
        ),
        migrations.AddIndex(
            model_name='recipe',
            index=models.Index(fields=['id', 'slug'], name='recipe_id_slug_idx'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='favorite',
            field=models.ManyToManyField(
                blank=True,
                related_name='favorite_recipes',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
