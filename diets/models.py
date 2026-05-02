import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from recipes.models import Recipe


class Weight(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="weights",
        on_delete=models.CASCADE,
    )
    weight = models.DecimalField(decimal_places=2, max_digits=5)
    date = models.DateField(default=timezone.localdate, db_index=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)
        indexes = [
            models.Index(fields=['user', 'date'], name='weight_user_date_idx'),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'date'],
                name='unique_weight_per_user_date',
            ),
        ]

    def __str__(self):
        return f'{self.user} - {self.weight}kg'


class MealPlan(models.Model):
    PROGRAM_GAIN = 'gain'
    PROGRAM_STABLE = 'stable'
    PROGRAM_LOSE = 'lose'
    PROGRAM_CHOICES = [
        (PROGRAM_GAIN, 'Gain weight'),
        (PROGRAM_STABLE, 'Stable weight'),
        (PROGRAM_LOSE, 'Lose weight'),
    ]

    title = models.CharField(blank=True, max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)
    program_kind = models.CharField(
        max_length=20,
        choices=PROGRAM_CHOICES,
        blank=True,
        db_index=True,
    )
    description_of_diet = models.TextField(blank=True)
    base_tdee = models.PositiveIntegerField(null=True, blank=True)
    target_calories = models.DecimalField(
        decimal_places=1,
        max_digits=7,
        null=True,
        blank=True,
    )
    selection_seed = models.PositiveBigIntegerField(null=True, blank=True, db_index=True)
    selection_algorithm = models.CharField(max_length=50, default='seeded_v1')
    selection_metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.title


class DietMeal(models.Model):
    BREAKFAST = 'breakfast'
    LUNCH = 'lunch'
    DINNER = 'dinner'
    MEAL_CHOICES = [
        (BREAKFAST, 'Breakfast'),
        (LUNCH, 'Lunch'),
        (DINNER, 'Dinner'),
    ]

    meal_plan = models.ForeignKey(
        MealPlan,
        related_name='meals',
        on_delete=models.CASCADE,
    )
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    recipe = models.ForeignKey(
        Recipe,
        related_name='diet_meals',
        on_delete=models.CASCADE,
    )
    position = models.PositiveIntegerField(default=1)
    target_calories = models.DecimalField(
        decimal_places=1,
        max_digits=7,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ('meal_type', 'position')
        constraints = [
            models.UniqueConstraint(
                fields=['meal_plan', 'meal_type', 'position'],
                name='unique_diet_meal_position',
            ),
            models.UniqueConstraint(
                fields=['meal_plan', 'meal_type', 'recipe'],
                name='unique_diet_meal_recipe',
            ),
        ]

    def __str__(self):
        return f'{self.meal_plan}: {self.meal_type} #{self.position}'


class ProgramSubscription(models.Model):
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='program_subscriptions',
        on_delete=models.CASCADE,
    )
    meal_plan = models.ForeignKey(
        MealPlan,
        related_name='subscriptions',
        on_delete=models.CASCADE,
    )
    breakfast_time = models.TimeField()
    lunch_time = models.TimeField()
    dinner_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    date_subscribe = models.DateField(default=datetime.date.today)
    ended_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber'],
                condition=models.Q(is_active=True),
                name='unique_active_program_subscription_per_user',
            )
        ]

    def __str__(self):
        return f'{self.subscriber} -> {self.meal_plan}'


class SmsDeliveryLog(models.Model):
    BREAKFAST = 'breakfast'
    LUNCH = 'lunch'
    DINNER = 'dinner'
    MEAL_CHOICES = [
        (BREAKFAST, 'Breakfast'),
        (LUNCH, 'Lunch'),
        (DINNER, 'Dinner'),
    ]

    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SENT, 'Sent'),
        (FAILED, 'Failed'),
    ]

    subscription = models.ForeignKey(
        ProgramSubscription,
        related_name='sms_logs',
        on_delete=models.CASCADE,
    )
    meal = models.CharField(max_length=20, choices=MEAL_CHOICES)
    sent_for_date = models.DateField()
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    provider_sid = models.CharField(max_length=80, blank=True)
    error = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        constraints = [
            models.UniqueConstraint(
                fields=['subscription', 'meal', 'sent_for_date'],
                name='unique_sms_delivery_per_subscription_meal_day',
            )
        ]

    def __str__(self):
        return f'{self.subscription_id}:{self.meal}:{self.sent_for_date}:{self.status}'
