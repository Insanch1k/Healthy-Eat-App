# Generated by Django 2.0 on 2020-05-09 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hairstyle', '0003_auto_20200509_1437'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ('-created',)},
        ),
    ]
