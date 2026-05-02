import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('diets', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weight',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='weights',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='diet',
            name='subscriber',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='diets',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name='weight',
            index=models.Index(fields=['user', 'created'], name='weight_user_created_idx'),
        ),
        migrations.AddConstraint(
            model_name='diet',
            constraint=models.UniqueConstraint(
                condition=models.Q(is_active=True),
                fields=('subscriber',),
                name='unique_active_diet_per_user',
            ),
        ),
        migrations.CreateModel(
            name='SmsDeliveryLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal', models.CharField(choices=[('breakfast', 'Breakfast'), ('lunch', 'Lunch'), ('dinner', 'Dinner')], max_length=20)),
                ('sent_for_date', models.DateField()),
                ('scheduled_for', models.DateTimeField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('provider_sid', models.CharField(blank=True, max_length=80)),
                ('error', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('diet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sms_logs', to='diets.diet')),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.AddConstraint(
            model_name='smsdeliverylog',
            constraint=models.UniqueConstraint(
                fields=('diet', 'meal', 'sent_for_date'),
                name='unique_sms_delivery_per_meal_day',
            ),
        ),
    ]
