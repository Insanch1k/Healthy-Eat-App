# Generated by Django 2.2 on 2020-06-25 00:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diets', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weight',
            options={'ordering': ('created',)},
        ),
    ]
