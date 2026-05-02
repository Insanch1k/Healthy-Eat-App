from datetime import datetime
from uuid import uuid4

from django.db import IntegrityError, transaction
from django.utils import timezone

from . import selectors
from .models import DietMeal, MealPlan, ProgramSubscription, SmsDeliveryLog, Weight
from .recipe_selection import (
    SELECTION_ALGORITHM,
    candidate_recipes_for_targets,
    generate_selection_seed,
    select_recipes,
    target_calories_for_meal,
)
from .strategies import PROGRAMS, build_program_targets


class DuplicateWeightForDateError(Exception):
    pass


def get_weight_item(user, weight_id):
    return selectors.get_weight_for_user(user=user, weight_id=weight_id)


def get_my_weight(user):
    return selectors.weights_for_user(user)


def user_has_weight_today(user, now=None):
    current_date = timezone.localdate(now)
    return selectors.user_has_weight_for_date(user=user, entry_date=current_date)


def create_weight_entry(user, weight, entry_date=None):
    entry_date = entry_date or timezone.localdate()
    try:
        return Weight.objects.create(user=user, weight=weight, date=entry_date)
    except IntegrityError as exc:
        raise DuplicateWeightForDateError from exc


def calculate_bmr_tdee(cleaned_data):
    activity = float(cleaned_data['drop'])
    sex = cleaned_data['sex']
    height = float(cleaned_data['height'])
    weight = float(cleaned_data['weight'])
    age = int(cleaned_data['age'])
    bmi = round(weight / (height ** 2) * 10000, 2)

    if sex == 'Woman':
        bmr = int(655 + (9.6 * weight) + (1.8 * height) - 4.7 * age)
        perfect_weight = (height - 100) - ((height - 100) * 0.15)
    else:
        bmr = int(66 + (13.7 * weight) + (5 * height) - 6.8 * age)
        perfect_weight = (height - 100) - ((height - 100) * 0.1)

    tdee = int(activity * bmr)
    tdee_lose_weight = int(tdee * 0.85)
    tdee_gain_weight = int(tdee * 1.15)
    return {
        'activity': activity,
        'a': activity,
        'sex': sex,
        'bmr': bmr,
        'tdee': tdee,
        'tdee_plus': tdee + 100,
        'tdee_lose_weight': tdee_lose_weight,
        'tdee_lose_weight_plus': tdee_lose_weight + 100,
        'tdee_gain_weight': tdee_gain_weight,
        'tdee_gain_weight_plus': tdee_gain_weight + 100,
        'bmi': bmi,
        'perfect_weight': round(perfect_weight, 1),
    }


def build_program_context(program_kind, base_tdee, user):
    config = PROGRAMS[program_kind]
    targets = build_program_targets(program_kind, base_tdee)
    candidate_map = candidate_recipes_for_targets(targets, config)
    is_subscribe = (
        user.is_authenticated
        and selectors.active_subscriptions_for_user(user).exists()
    )

    context = {
        **targets,
        'is_subscribe': is_subscribe,
        'breakfast_recipes': candidate_map[DietMeal.BREAKFAST],
        'lunch_recipes': candidate_map[DietMeal.LUNCH],
        'dinner_recipes': candidate_map[DietMeal.DINNER],
        'meal_candidates': candidate_map,
    }
    return context


@transaction.atomic
def subscribe_user_to_program(user, program_kind, base_tdee, times):
    config = PROGRAMS[program_kind]
    context = build_program_context(program_kind, base_tdee, user)
    seed = generate_selection_seed()
    selected_recipes, selection_metadata = select_recipes(context['meal_candidates'], seed)

    selectors.active_subscriptions_for_user(user).update(
        is_active=False,
        ended_at=timezone.now(),
    )
    meal_plan = MealPlan.objects.create(
        title=config.title,
        slug=f'{config.slug_prefix}-{user.pk}-{uuid4().hex[:8]}',
        program_kind=program_kind,
        description_of_diet=config.description,
        base_tdee=base_tdee,
        target_calories=context['value'],
        selection_seed=seed,
        selection_algorithm=SELECTION_ALGORITHM,
        selection_metadata=selection_metadata,
    )
    for meal_type, recipes in selected_recipes.items():
        for position, recipe in enumerate(recipes, start=1):
            DietMeal.objects.create(
                meal_plan=meal_plan,
                meal_type=meal_type,
                recipe=recipe,
                position=position,
                target_calories=target_calories_for_meal(context, meal_type),
            )

    return ProgramSubscription.objects.create(
        subscriber=user,
        meal_plan=meal_plan,
        breakfast_time=times['breakfast_time'],
        lunch_time=times['lunch_time'],
        dinner_time=times['dinner_time'],
    )


def unsubscribe_active_programs(user):
    return selectors.active_subscriptions_for_user(user).update(
        is_active=False,
        ended_at=timezone.now(),
    )


def due_meal_logs(now=None):
    now = timezone.localtime(now or timezone.now())
    today = now.date()
    current_tz = timezone.get_current_timezone()
    meal_fields = {
        DietMeal.BREAKFAST: 'breakfast_time',
        DietMeal.LUNCH: 'lunch_time',
        DietMeal.DINNER: 'dinner_time',
    }

    logs = []
    subscriptions = ProgramSubscription.objects.filter(is_active=True).select_related(
        'subscriber',
        'subscriber__profile',
        'meal_plan',
    )
    for subscription in subscriptions:
        for meal, field_name in meal_fields.items():
            meal_time = getattr(subscription, field_name)
            scheduled_for = timezone.make_aware(datetime.combine(today, meal_time), current_tz)
            if scheduled_for > now:
                continue
            log, created = SmsDeliveryLog.objects.get_or_create(
                subscription=subscription,
                meal=meal,
                sent_for_date=today,
                defaults={'scheduled_for': scheduled_for},
            )
            if created or log.status == SmsDeliveryLog.FAILED:
                logs.append(log)
    return logs
