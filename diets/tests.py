from datetime import date, time
from unittest.mock import Mock, patch

from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from recipes.models import Category, Profile, Recipe

from . import selectors
from .models import DietMeal, MealPlan, ProgramSubscription, SmsDeliveryLog, Weight
from .recipe_selection import select_recipes
from .services import calculate_bmr_tdee, due_meal_logs
from .strategies import build_program_targets
from .tasks import send_due_meal_reminders, send_sms_delivery_log


class DietDomainTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        Profile.objects.create(user=self.user, phone='+48123456789')
        self.breakfast = Category.objects.create(name='Breakfast', slug='breakfast')
        self.lunch = Category.objects.create(name='Lunch', slug='lunch')
        self.dinner = Category.objects.create(name='Dinner', slug='dinner')
        self.breakfast_recipe = Recipe.objects.create(
            title='Oats',
            category=self.breakfast,
            slug='oats',
            description='x',
            calories=520,
        )
        self.lunch_recipe = Recipe.objects.create(
            title='Bowl',
            category=self.lunch,
            slug='bowl',
            description='x',
            calories=520,
        )
        self.dinner_recipe = Recipe.objects.create(
            title='Stew',
            category=self.dinner,
            slug='stew',
            description='x',
            calories=450,
        )

    def test_calculator_formula_for_man(self):
        result = calculate_bmr_tdee({
            'drop': '1.2',
            'sex': 'Man',
            'height': 180,
            'weight': 80,
            'age': 30,
        })

        self.assertEqual(result['bmr'], 1858)
        self.assertEqual(result['tdee'], 2229)
        self.assertEqual(result['tdee_lose_weight'], 1894)
        self.assertEqual(result['tdee_gain_weight'], 2563)

    def test_weight_can_be_added_once_per_day(self):
        Weight.objects.create(user=self.user, weight=80)
        self.client.login(username='alice', password='pass12345')

        response = self.client.post(reverse('diets:weight'), {'weight': '81.0'})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Weight.objects.filter(user=self.user).count(), 1)

    def test_subscribing_to_new_program_deactivates_previous_active_program(self):
        self.client.login(username='alice', password='pass12345')

        with patch('diets.views.programs.send_program_confirmation.delay'):
            for program_kind in ['stable', 'gain']:
                response = self.client.post(
                    reverse('diets:program', args=[program_kind, 2000]),
                    {
                        'breakfast_time': '08:00',
                        'lunch_time': '13:00',
                        'dinner_time': '19:00',
                    },
                )
                self.assertEqual(response.status_code, 302)

        self.assertEqual(MealPlan.objects.count(), 2)
        self.assertEqual(ProgramSubscription.objects.filter(subscriber=self.user).count(), 2)
        self.assertEqual(
            ProgramSubscription.objects.filter(subscriber=self.user, is_active=True).count(),
            1,
        )
        self.assertGreater(DietMeal.objects.count(), 0)

    def test_weight_date_is_unique_per_user(self):
        entry_date = date(2026, 1, 10)
        Weight.objects.create(user=self.user, weight=80, date=entry_date)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Weight.objects.create(user=self.user, weight=81, date=entry_date)

    def test_program_subscription_subscriber_cannot_be_null(self):
        meal_plan = MealPlan.objects.create(title='Stable', slug='stable')

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ProgramSubscription.objects.create(
                    subscriber=None,
                    meal_plan=meal_plan,
                    breakfast_time=time(7, 0),
                    lunch_time=time(12, 0),
                    dinner_time=time(18, 0),
                )

    def test_program_strategy_returns_tested_targets(self):
        result = build_program_targets('stable', 2000)

        self.assertEqual(result['value'], 2000)
        self.assertEqual(result['breakfast_calories'], 500)
        self.assertEqual(result['lunch_calories'], 900)
        self.assertEqual(result['dinner_calories'], 400)
        self.assertEqual(result['amount_of_protein_for_lunch'], 50)

    def test_seeded_recipe_selection_is_reproducible(self):
        recipes = [
            Recipe.objects.create(
                title=f'Oats {idx}',
                category=self.breakfast,
                slug=f'oats-{idx}',
                description='x',
                calories=500,
            )
            for idx in range(5)
        ]
        candidate_map = {DietMeal.BREAKFAST: Recipe.objects.filter(id__in=[r.id for r in recipes])}

        first, first_metadata = select_recipes(candidate_map, seed=1)
        second, second_metadata = select_recipes(candidate_map, seed=1)
        third, _ = select_recipes(candidate_map, seed=2)

        first_ids = [recipe.id for recipe in first[DietMeal.BREAKFAST]]
        second_ids = [recipe.id for recipe in second[DietMeal.BREAKFAST]]
        third_ids = [recipe.id for recipe in third[DietMeal.BREAKFAST]]
        self.assertEqual(first_ids, second_ids)
        self.assertNotEqual(first_ids, third_ids)
        self.assertEqual(first_metadata, second_metadata)

    def test_weight_selector_orders_by_date(self):
        Weight.objects.create(user=self.user, weight=82, date=date(2026, 1, 2))
        Weight.objects.create(user=self.user, weight=80, date=date(2026, 1, 1))

        result = list(selectors.weights_for_user(self.user).values_list('weight', flat=True))

        self.assertEqual([float(value) for value in result], [80.0, 82.0])

    def test_active_diet_selector_returns_current_program(self):
        old_plan = MealPlan.objects.create(
            title='Old',
            slug='old',
        )
        inactive = ProgramSubscription.objects.create(
            subscriber=self.user,
            meal_plan=old_plan,
            is_active=False,
            breakfast_time=time(7, 0),
            lunch_time=time(12, 0),
            dinner_time=time(18, 0),
        )
        current_plan = MealPlan.objects.create(
            title='Current',
            slug='current',
        )
        active = ProgramSubscription.objects.create(
            subscriber=self.user,
            meal_plan=current_plan,
            breakfast_time=time(7, 0),
            lunch_time=time(12, 0),
            dinner_time=time(18, 0),
        )

        result = selectors.get_active_subscription_for_user(self.user)

        self.assertEqual(result, active)
        self.assertNotEqual(result, inactive)

    def test_canonical_and_legacy_diet_urls(self):
        self.client.login(username='alice', password='pass12345')

        self.assertEqual(self.client.get(reverse('diets:weight')).status_code, 200)
        self.assertEqual(self.client.get(reverse('diets:calculator')).status_code, 200)
        self.assertEqual(
            self.client.get('/diets/', follow=False)['Location'],
            reverse('diets:weight'),
        )
        self.assertEqual(
            self.client.get('/diets/stable_weight/2000', follow=False)['Location'],
            reverse('diets:program', args=['stable', 2000]),
        )

    def test_due_meal_logs_are_unique_per_meal_day(self):
        meal_plan = MealPlan.objects.create(
            title='StableWeight',
            slug='stable-weight-alice',
        )
        subscription = ProgramSubscription.objects.create(
            subscriber=self.user,
            meal_plan=meal_plan,
            breakfast_time=time(7, 0),
            lunch_time=time(12, 0),
            dinner_time=time(18, 0),
        )
        now = timezone.now().replace(hour=20, minute=0, second=0, microsecond=0)

        first = due_meal_logs(now)
        second = due_meal_logs(now)

        self.assertEqual(len(first), 3)
        self.assertEqual(len(second), 0)
        self.assertEqual(SmsDeliveryLog.objects.filter(subscription=subscription).count(), 3)

    @override_settings(SMS_REMINDERS_ENABLED=True)
    def test_due_meal_task_sends_with_mocked_sms_client(self):
        meal_plan = MealPlan.objects.create(
            title='StableWeight',
            slug='stable-weight-task',
        )
        ProgramSubscription.objects.create(
            subscriber=self.user,
            meal_plan=meal_plan,
            breakfast_time=time(0, 0),
            lunch_time=time(0, 0),
            dinner_time=time(0, 0),
        )
        fake_client = Mock()
        fake_client.send.return_value = 'SM123'

        with patch('diets.tasks.get_sms_client', return_value=fake_client):
            with patch(
                'diets.tasks.send_sms_delivery_log.delay',
                side_effect=lambda log_id: send_sms_delivery_log(log_id),
            ):
                with self.captureOnCommitCallbacks(execute=True):
                    result = send_due_meal_reminders()

        self.assertEqual(result['scheduled'], 3)
        self.assertEqual(SmsDeliveryLog.objects.filter(status=SmsDeliveryLog.SENT).count(), 3)
        self.assertEqual(fake_client.send.call_count, 3)
