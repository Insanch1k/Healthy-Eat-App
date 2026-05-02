import random
import secrets

from recipes.selectors import recipes_for_meal

from .models import DietMeal

SELECTION_ALGORITHM = 'seeded_v1'
MAX_RECIPES_PER_MEAL = 3


def generate_selection_seed():
    return secrets.randbits(63)


def candidate_recipes_for_targets(targets, config):
    return {
        DietMeal.BREAKFAST: recipes_for_meal(
            category_name='Breakfast',
            calories=targets['breakfast_calories'],
        ),
        DietMeal.LUNCH: recipes_for_meal(
            category_name='Lunch',
            calories=targets['lunch_calories2'],
        ),
        DietMeal.DINNER: recipes_for_meal(
            category_name='Dinner',
            calories=targets['dinner_calories'],
            lower=config.dinner_range[0],
            upper=config.dinner_range[1],
        ),
    }


def target_calories_for_meal(targets, meal_type):
    return {
        DietMeal.BREAKFAST: targets['breakfast_calories'],
        DietMeal.LUNCH: targets['lunch_calories2'],
        DietMeal.DINNER: targets['dinner_calories'],
    }[meal_type]


def select_recipes(candidate_map, seed, max_recipes_per_meal=MAX_RECIPES_PER_MEAL):
    rng = random.Random(seed)
    selected = {}
    metadata = {
        'algorithm': SELECTION_ALGORITHM,
        'seed': seed,
        'max_recipes_per_meal': max_recipes_per_meal,
        'candidates': {},
        'selected': {},
    }

    for meal_type, queryset in candidate_map.items():
        candidates = list(queryset.order_by('id'))
        candidate_ids = [recipe.id for recipe in candidates]
        shuffled = candidates[:]
        rng.shuffle(shuffled)
        meal_selected = shuffled[:max_recipes_per_meal]
        selected[meal_type] = meal_selected
        metadata['candidates'][meal_type] = candidate_ids
        metadata['selected'][meal_type] = [recipe.id for recipe in meal_selected]

    return selected, metadata
