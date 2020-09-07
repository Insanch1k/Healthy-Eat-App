# Generated by Django 2.2 on 2020-08-08 13:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diets', '0009_auto_20200808_1345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diet',
            name='subscriber',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subscriber', to=settings.AUTH_USER_MODEL),
        ),
    ]
