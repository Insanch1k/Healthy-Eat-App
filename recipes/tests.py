from pathlib import Path

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from . import selectors
from .models import Category, Profile, Recipe


class RecipeViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        Profile.objects.create(user=self.user, phone='+48123456789')
        self.category = Category.objects.create(name='Breakfast', slug='breakfast')
        self.recipe = Recipe.objects.create(
            title='Oatmeal',
            category=self.category,
            slug='oatmeal',
            description='Warm oats',
            calories=400,
            protein=10,
            carbohydrates=50,
            fat=5,
        )

    def test_favorite_requires_login_and_post(self):
        url = reverse('recipes:favorite', args=[self.recipe.id, self.recipe.slug])

        anonymous_response = self.client.post(url)
        self.assertEqual(anonymous_response.status_code, 302)
        self.assertIn('/login/', anonymous_response['Location'])

        self.client.login(username='alice', password='pass12345')
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 405)

        post_response = self.client.post(url)
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(self.recipe.favorite.filter(id=self.user.id).exists())

    def test_my_profile_uses_authenticated_users_favorites(self):
        self.recipe.favorite.add(self.user)
        self.client.login(username='alice', password='pass12345')

        response = self.client.get(reverse('recipes:my_profile'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Oatmeal')

    def test_invalid_calorie_search_does_not_crash(self):
        response = self.client.get(
            reverse('recipes:search_calories', args=[self.category.slug]),
            {'calories': 'abc'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Calories must be a number.')

    def test_recipe_selectors_search_and_calorie_range(self):
        Recipe.objects.create(
            title='Rice Bowl',
            category=self.category,
            slug='rice-bowl',
            description='Savory rice',
            calories=430,
            protein=10,
            carbohydrates=50,
            fat=5,
        )

        search_result = selectors.search_recipes(query='rice')
        _, calories_result = selectors.recipes_for_category_calories(
            category_slug=self.category.slug,
            calories=420,
        )

        self.assertEqual(list(search_result.values_list('title', flat=True)), ['Rice Bowl'])
        self.assertEqual(
            set(calories_result.values_list('title', flat=True)),
            {'Oatmeal', 'Rice Bowl'},
        )

    def test_canonical_and_legacy_recipe_urls(self):
        self.assertEqual(self.client.get(reverse('recipes:recipes_list')).status_code, 200)
        self.assertEqual(
            self.client.get('/meals/recipes/', follow=False)['Location'],
            reverse('recipes:recipes_list'),
        )
        self.assertEqual(
            self.client.get('/meals/by/breakfast', follow=False)['Location'],
            reverse('recipes:recipes_by', args=['breakfast']),
        )

    def test_healthz_is_public(self):
        response = self.client.get('/healthz/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'ok')


class TemplateStyleTests(TestCase):
    def test_templates_do_not_use_inline_css_or_scripts(self):
        root = Path(__file__).resolve().parents[1]
        template_dirs = [
            root / 'diets' / 'templates',
            root / 'recipes' / 'templates',
            root / 'notes' / 'templates',
            root / 'news' / 'templates',
            root / 'templates',
        ]
        violations = []
        for template_dir in template_dirs:
            for template_path in template_dir.rglob('*.html'):
                content = template_path.read_text()
                if '<style' in content:
                    violations.append(f'{template_path}: <style>')
                if 'style=' in content:
                    violations.append(f'{template_path}: style=')
                if '<script>' in content:
                    violations.append(f'{template_path}: inline <script>')
                if 'onclick=' in content or 'onsubmit=' in content:
                    violations.append(f'{template_path}: inline handler')

        self.assertEqual(violations, [])
