import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
from django.db.models import Count


def normalize_weight_dates_and_diets(apps, schema_editor):
    Diet = apps.get_model('diets', 'Diet')
    Weight = apps.get_model('diets', 'Weight')

    orphan_ids = list(
        Diet.objects.filter(subscriber__isnull=True).values_list('id', flat=True)[:20]
    )
    if orphan_ids:
        raise RuntimeError(
            'Cannot make Diet.subscriber non-null while orphan diets exist. '
            f'Diet ids without subscriber: {orphan_ids}'
        )

    for weight in Weight.objects.all().only('id', 'created').iterator():
        created = weight.created
        if created is None:
            entry_date = django.utils.timezone.localdate()
        elif django.utils.timezone.is_aware(created):
            entry_date = django.utils.timezone.localtime(created).date()
        else:
            entry_date = created.date()
        Weight.objects.filter(id=weight.id).update(date=entry_date)

    duplicate_keys = (
        Weight.objects.values('user_id', 'date')
        .annotate(count=Count('id'))
        .filter(count__gt=1)
    )
    for duplicate in duplicate_keys:
        records = Weight.objects.filter(
            user_id=duplicate['user_id'],
            date=duplicate['date'],
        ).order_by('-created', '-id')
        keep_id = records.values_list('id', flat=True).first()
        records.exclude(id=keep_id).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('diets', '0002_modernize_diet_and_sms_delivery'),
    ]

    operations = [
        migrations.AddField(
            model_name='weight',
            name='date',
            field=models.DateField(db_index=True, null=True),
        ),
        migrations.RunPython(
            normalize_weight_dates_and_diets,
            migrations.RunPython.noop,
        ),
        migrations.RemoveIndex(
            model_name='weight',
            name='weight_user_created_idx',
        ),
        migrations.AlterField(
            model_name='diet',
            name='breakfast',
            field=models.ManyToManyField(
                blank=True,
                related_name='breakfast_diets',
                to='recipes.recipe',
            ),
        ),
        migrations.AlterField(
            model_name='diet',
            name='dinner',
            field=models.ManyToManyField(
                blank=True,
                related_name='dinner_diets',
                to='recipes.recipe',
            ),
        ),
        migrations.AlterField(
            model_name='diet',
            name='lunch',
            field=models.ManyToManyField(
                blank=True,
                related_name='lunch_diets',
                to='recipes.recipe',
            ),
        ),
        migrations.AlterField(
            model_name='diet',
            name='subscriber',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='diets',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='weight',
            name='date',
            field=models.DateField(
                db_index=True,
                default=django.utils.timezone.localdate,
            ),
        ),
        migrations.AddIndex(
            model_name='weight',
            index=models.Index(fields=['user', 'date'], name='weight_user_date_idx'),
        ),
        migrations.AddConstraint(
            model_name='weight',
            constraint=models.UniqueConstraint(
                fields=('user', 'date'),
                name='unique_weight_per_user_date',
            ),
        ),
    ]
