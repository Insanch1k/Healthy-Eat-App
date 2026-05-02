from datetime import datetime, time
from decimal import Decimal

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase
from django.utils import timezone


class DietCleanupMigrationTests(TransactionTestCase):
    migrate_from = [('diets', '0002_modernize_diet_and_sms_delivery')]
    migrate_to = [('diets', '0003_cleanup_diet_weight_models')]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps
        self._prepare_old_state(old_apps)

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        self.apps = self.executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def _prepare_old_state(self, apps):
        User = apps.get_model('auth', 'User')
        Weight = apps.get_model('diets', 'Weight')
        self.user = User.objects.create(username='migration-user')
        old = Weight.objects.create(user=self.user, weight=Decimal('80.0'))
        new = Weight.objects.create(user=self.user, weight=Decimal('81.0'))
        entry_date = timezone.make_aware(datetime(2026, 1, 5, 8, 0, 0))
        Weight.objects.filter(pk=old.pk).update(created=entry_date)
        Weight.objects.filter(pk=new.pk).update(created=entry_date.replace(hour=20))

    def test_weight_date_backfill_deduplicates_by_latest_created(self):
        Weight = self.apps.get_model('diets', 'Weight')

        weights = list(Weight.objects.filter(user_id=self.user.pk))

        self.assertEqual(len(weights), 1)
        self.assertEqual(weights[0].date.isoformat(), '2026-01-05')
        self.assertEqual(weights[0].weight, Decimal('81.00'))


class DietDomainMigrationTests(TransactionTestCase):
    migrate_from = [('diets', '0003_cleanup_diet_weight_models')]
    migrate_to = [('diets', '0004_mealplan_subscription_dietmeal')]

    def setUp(self):
        super().setUp()
        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_from)
        old_apps = self.executor.loader.project_state(self.migrate_from).apps
        self._prepare_old_state(old_apps)

        self.executor = MigrationExecutor(connection)
        self.executor.migrate(self.migrate_to)
        self.apps = self.executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def _prepare_old_state(self, apps):
        User = apps.get_model('auth', 'User')
        Category = apps.get_model('recipes', 'Category')
        Recipe = apps.get_model('recipes', 'Recipe')
        Diet = apps.get_model('diets', 'Diet')
        SmsDeliveryLog = apps.get_model('diets', 'SmsDeliveryLog')

        self.user = User.objects.create(username='diet-migration-user')
        breakfast = Category.objects.create(name='Breakfast', slug='breakfast')
        lunch = Category.objects.create(name='Lunch', slug='lunch')
        dinner = Category.objects.create(name='Dinner', slug='dinner')
        self.breakfast_recipe = Recipe.objects.create(
            title='Oats',
            category=breakfast,
            slug='oats',
            description='x',
            calories=500,
        )
        self.lunch_recipe = Recipe.objects.create(
            title='Bowl',
            category=lunch,
            slug='bowl',
            description='x',
            calories=700,
        )
        self.dinner_recipe = Recipe.objects.create(
            title='Stew',
            category=dinner,
            slug='stew',
            description='x',
            calories=450,
        )
        self.diet = Diet.objects.create(
            title='StableWeight',
            slug='stable-weight-migration',
            subscriber=self.user,
            breakfast_time=time(8, 0),
            lunch_time=time(13, 0),
            dinner_time=time(19, 0),
        )
        self.diet.breakfast.add(self.breakfast_recipe)
        self.diet.lunch.add(self.lunch_recipe)
        self.diet.dinner.add(self.dinner_recipe)
        self.log = SmsDeliveryLog.objects.create(
            diet=self.diet,
            meal='breakfast',
            sent_for_date='2026-01-05',
            scheduled_for=timezone.now(),
        )

    def test_diet_domain_migration_creates_subscription_and_meals(self):
        MealPlan = self.apps.get_model('diets', 'MealPlan')
        ProgramSubscription = self.apps.get_model('diets', 'ProgramSubscription')
        DietMeal = self.apps.get_model('diets', 'DietMeal')
        SmsDeliveryLog = self.apps.get_model('diets', 'SmsDeliveryLog')

        meal_plan = MealPlan.objects.get(pk=self.diet.pk)
        subscription = ProgramSubscription.objects.get(meal_plan=meal_plan)
        meals = DietMeal.objects.filter(meal_plan=meal_plan)
        log = SmsDeliveryLog.objects.get(pk=self.log.pk)

        self.assertEqual(meal_plan.program_kind, 'stable')
        self.assertEqual(meal_plan.selection_algorithm, 'legacy_migration')
        self.assertEqual(subscription.subscriber_id, self.user.pk)
        self.assertTrue(subscription.is_active)
        self.assertEqual(subscription.breakfast_time, time(8, 0))
        self.assertEqual(meals.count(), 3)
        self.assertEqual(
            set(meals.values_list('meal_type', 'recipe_id')),
            {
                ('breakfast', self.breakfast_recipe.pk),
                ('lunch', self.lunch_recipe.pk),
                ('dinner', self.dinner_recipe.pk),
            },
        )
        self.assertEqual(log.subscription_id, subscription.pk)
