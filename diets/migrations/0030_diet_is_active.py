# Generated by Django 2.2 on 2020-08-17 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diets', '0029_diet_second_lunch_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='diet',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]
