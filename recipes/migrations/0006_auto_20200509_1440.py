# Generated by Django 2.0 on 2020-05-09 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_recipe_recipe_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='recipe_description',
            field=models.TextField(),
        ),
    ]
