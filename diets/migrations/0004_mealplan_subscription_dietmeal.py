import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def infer_program_kind(title):
    normalized = (title or '').lower()
    if 'gain' in normalized:
        return 'gain'
    if 'lose' in normalized:
        return 'lose'
    if 'stable' in normalized:
        return 'stable'
    return ''


def migrate_diet_domain(apps, schema_editor):
    MealPlan = apps.get_model('diets', 'MealPlan')
    DietMeal = apps.get_model('diets', 'DietMeal')
    ProgramSubscription = apps.get_model('diets', 'ProgramSubscription')
    SmsDeliveryLog = apps.get_model('diets', 'SmsDeliveryLog')

    for meal_plan in MealPlan.objects.all().iterator():
        meal_recipe_ids = {
            'breakfast': list(meal_plan.breakfast.values_list('id', flat=True)),
            'lunch': list(meal_plan.lunch.values_list('id', flat=True)),
            'dinner': list(meal_plan.dinner.values_list('id', flat=True)),
        }
        meal_plan.program_kind = infer_program_kind(meal_plan.title)
        meal_plan.selection_algorithm = 'legacy_migration'
        meal_plan.selection_metadata = {
            'legacy_meal_plan_id': meal_plan.id,
            'migrated_recipe_ids': meal_recipe_ids,
        }
        meal_plan.save(
            update_fields=[
                'program_kind',
                'selection_algorithm',
                'selection_metadata',
            ]
        )

        subscription = ProgramSubscription.objects.create(
            subscriber=meal_plan.subscriber,
            meal_plan=meal_plan,
            breakfast_time=meal_plan.breakfast_time,
            lunch_time=meal_plan.lunch_time,
            dinner_time=meal_plan.dinner_time,
            is_active=meal_plan.is_active,
            date_subscribe=meal_plan.date_subscribe,
        )
        for meal_type, recipe_ids in meal_recipe_ids.items():
            for position, recipe_id in enumerate(recipe_ids, start=1):
                DietMeal.objects.create(
                    meal_plan=meal_plan,
                    meal_type=meal_type,
                    recipe_id=recipe_id,
                    position=position,
                )
        SmsDeliveryLog.objects.filter(diet_id=meal_plan.id).update(subscription=subscription)


def reverse_diet_domain(apps, schema_editor):
    MealPlan = apps.get_model('diets', 'MealPlan')
    DietMeal = apps.get_model('diets', 'DietMeal')
    ProgramSubscription = apps.get_model('diets', 'ProgramSubscription')
    SmsDeliveryLog = apps.get_model('diets', 'SmsDeliveryLog')

    for meal_plan in MealPlan.objects.all().iterator():
        subscription = (
            ProgramSubscription.objects.filter(meal_plan=meal_plan)
            .order_by('-is_active', '-date_subscribe', '-id')
            .first()
        )
        if subscription:
            meal_plan.subscriber = subscription.subscriber
            meal_plan.breakfast_time = subscription.breakfast_time
            meal_plan.lunch_time = subscription.lunch_time
            meal_plan.dinner_time = subscription.dinner_time
            meal_plan.is_active = subscription.is_active
            meal_plan.date_subscribe = subscription.date_subscribe
            meal_plan.save(
                update_fields=[
                    'subscriber',
                    'breakfast_time',
                    'lunch_time',
                    'dinner_time',
                    'is_active',
                    'date_subscribe',
                ]
            )
            SmsDeliveryLog.objects.filter(subscription=subscription).update(diet_id=meal_plan.id)

        for meal_type, relation_name in [
            ('breakfast', 'breakfast'),
            ('lunch', 'lunch'),
            ('dinner', 'dinner'),
        ]:
            recipe_ids = DietMeal.objects.filter(
                meal_plan=meal_plan,
                meal_type=meal_type,
            ).order_by('position').values_list('recipe_id', flat=True)
            getattr(meal_plan, relation_name).set(recipe_ids)


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('diets', '0003_cleanup_diet_weight_models'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Diet',
            new_name='MealPlan',
        ),
        migrations.RemoveConstraint(
            model_name='mealplan',
            name='unique_active_diet_per_user',
        ),
        migrations.AddField(
            model_name='mealplan',
            name='base_tdee',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='mealplan',
            name='program_kind',
            field=models.CharField(
                blank=True,
                choices=[
                    ('gain', 'Gain weight'),
                    ('stable', 'Stable weight'),
                    ('lose', 'Lose weight'),
                ],
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='mealplan',
            name='selection_algorithm',
            field=models.CharField(default='seeded_v1', max_length=50),
        ),
        migrations.AddField(
            model_name='mealplan',
            name='selection_metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='mealplan',
            name='selection_seed',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name='mealplan',
            name='target_calories',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=7, null=True),
        ),
        migrations.CreateModel(
            name='ProgramSubscription',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('breakfast_time', models.TimeField()),
                ('lunch_time', models.TimeField()),
                ('dinner_time', models.TimeField()),
                ('is_active', models.BooleanField(default=True)),
                ('date_subscribe', models.DateField(default=datetime.date.today)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                (
                    'meal_plan',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='subscriptions',
                        to='diets.mealplan',
                    ),
                ),
                (
                    'subscriber',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='program_subscriptions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='DietMeal',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'meal_type',
                    models.CharField(
                        choices=[
                            ('breakfast', 'Breakfast'),
                            ('lunch', 'Lunch'),
                            ('dinner', 'Dinner'),
                        ],
                        max_length=20,
                    ),
                ),
                ('position', models.PositiveIntegerField(default=1)),
                (
                    'target_calories',
                    models.DecimalField(blank=True, decimal_places=1, max_digits=7, null=True),
                ),
                (
                    'meal_plan',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='meals',
                        to='diets.mealplan',
                    ),
                ),
                (
                    'recipe',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='diet_meals',
                        to='recipes.recipe',
                    ),
                ),
            ],
            options={
                'ordering': ('meal_type', 'position'),
            },
        ),
        migrations.AddField(
            model_name='smsdeliverylog',
            name='subscription',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sms_logs',
                to='diets.programsubscription',
            ),
        ),
        migrations.RunPython(migrate_diet_domain, reverse_diet_domain),
        migrations.AlterField(
            model_name='smsdeliverylog',
            name='subscription',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='sms_logs',
                to='diets.programsubscription',
            ),
        ),
        migrations.RemoveConstraint(
            model_name='smsdeliverylog',
            name='unique_sms_delivery_per_meal_day',
        ),
        migrations.RemoveField(
            model_name='smsdeliverylog',
            name='diet',
        ),
        migrations.AddConstraint(
            model_name='dietmeal',
            constraint=models.UniqueConstraint(
                fields=('meal_plan', 'meal_type', 'position'),
                name='unique_diet_meal_position',
            ),
        ),
        migrations.AddConstraint(
            model_name='dietmeal',
            constraint=models.UniqueConstraint(
                fields=('meal_plan', 'meal_type', 'recipe'),
                name='unique_diet_meal_recipe',
            ),
        ),
        migrations.AddConstraint(
            model_name='programsubscription',
            constraint=models.UniqueConstraint(
                condition=models.Q(is_active=True),
                fields=('subscriber',),
                name='unique_active_program_subscription_per_user',
            ),
        ),
        migrations.AddConstraint(
            model_name='smsdeliverylog',
            constraint=models.UniqueConstraint(
                fields=('subscription', 'meal', 'sent_for_date'),
                name='unique_sms_delivery_per_subscription_meal_day',
            ),
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='amount_of_breakfast',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='amount_of_dinner',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='amount_of_lunch',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='breakfast',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='breakfast_time',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='date_subscribe',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='dinner',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='dinner_time',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='lunch',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='lunch_time',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='second_lunch_time',
        ),
        migrations.RemoveField(
            model_name='mealplan',
            name='subscriber',
        ),
    ]
