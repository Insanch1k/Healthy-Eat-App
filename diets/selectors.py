from django.shortcuts import get_object_or_404
from django.utils import timezone

from recipes.models import Recipe

from .models import DietMeal, ProgramSubscription, Weight


def weights_for_user(user):
    return Weight.objects.filter(user=user).order_by('date', 'created')


def get_weight_for_user(*, user, weight_id):
    return get_object_or_404(Weight, user=user, id=weight_id)


def user_has_weight_for_date(*, user, entry_date=None):
    entry_date = entry_date or timezone.localdate()
    return Weight.objects.filter(user=user, date=entry_date).exists()


def subscriptions_for_user(user):
    return ProgramSubscription.objects.filter(subscriber=user).select_related('meal_plan')


def active_subscriptions_for_user(user):
    return subscriptions_for_user(user).filter(is_active=True)


def active_subscription_for_user(user):
    return active_subscriptions_for_user(user).first()


def get_active_subscription_for_user(user):
    return get_object_or_404(active_subscriptions_for_user(user))


def meal_groups_for_plan(meal_plan):
    meals = (
        DietMeal.objects.filter(meal_plan=meal_plan)
        .select_related('recipe', 'recipe__category')
        .order_by('meal_type', 'position')
    )
    return {
        DietMeal.BREAKFAST: [meal for meal in meals if meal.meal_type == DietMeal.BREAKFAST],
        DietMeal.LUNCH: [meal for meal in meals if meal.meal_type == DietMeal.LUNCH],
        DietMeal.DINNER: [meal for meal in meals if meal.meal_type == DietMeal.DINNER],
    }


def snack_recipes():
    return Recipe.objects.filter(category__name='Snack').order_by('title')
