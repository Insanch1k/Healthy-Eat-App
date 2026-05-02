from django.db.models import Q
from django.shortcuts import get_object_or_404

from diets.models import ProgramSubscription

from .models import Category, Recipe


def categories():
    return Category.objects.all()


def recipes():
    return Recipe.objects.select_related('category').all()


def get_recipe(*, recipe_id, slug):
    return get_object_or_404(Recipe, id=recipe_id, slug=slug)


def search_recipes(*, query):
    queryset = recipes()
    if not query:
        return queryset
    return queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))


def get_category(*, slug):
    return get_object_or_404(Category, slug=slug)


def recipes_by_category(*, category):
    return recipes().filter(category=category)


def recipes_for_category_slug(*, category_slug):
    category = get_category(slug=category_slug)
    return category, recipes_by_category(category=category)


def recipes_for_category_calories(*, category_slug, calories, tolerance=50):
    category, queryset = recipes_for_category_slug(category_slug=category_slug)
    return category, queryset.filter(
        calories__range=(calories - tolerance, calories + tolerance),
    )


def favorite_recipe_groups(user):
    favorite_recipes = user.favorite_recipes.select_related('category').all()
    return {
        'favorite_recipe': favorite_recipes,
        'dinner': favorite_recipes.filter(category__name='Dinner'),
        'breakfast': favorite_recipes.filter(category__name='Breakfast'),
        'lunch': favorite_recipes.filter(category__name='Lunch'),
        'snack': favorite_recipes.filter(category__name='Snack'),
    }


def active_subscriptions_for_user(user):
    return ProgramSubscription.objects.filter(
        subscriber=user,
        is_active=True,
    ).select_related('meal_plan')


def recipes_for_meal(*, category_name, calories, lower=100, upper=50):
    return recipes().filter(
        category__name=category_name,
        calories__range=(calories - lower, calories + upper),
    ).order_by('title')
