from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from diets import selectors
from diets.forms import DietSubscriptionForm
from diets.services import (
    build_program_context,
    subscribe_user_to_program,
    unsubscribe_active_programs,
)
from diets.strategies import PROGRAM_GAIN, PROGRAM_LOSE, PROGRAM_STABLE, PROGRAMS
from diets.tasks import send_program_confirmation

PROGRAM_TEMPLATES = {
    PROGRAM_GAIN: 'gain_program.html',
    PROGRAM_STABLE: 'stable_program.html',
    PROGRAM_LOSE: 'lose_program.html',
}


def _program_view(request, value, program_kind, template_name):
    subscription_form = DietSubscriptionForm(request.POST or None)
    context = build_program_context(program_kind, value, request.user)
    context['subscription_form'] = subscription_form

    if request.method == 'POST' and subscription_form.is_valid():
        subscription = subscribe_user_to_program(
            request.user,
            program_kind,
            value,
            subscription_form.cleaned_data,
        )
        send_program_confirmation.delay(subscription.id)
        return redirect('recipes:my_profile')

    return render(request, template_name, context)


@login_required
def program(request, program_kind, value):
    if program_kind not in PROGRAMS:
        raise Http404('Unknown diet program.')
    return _program_view(request, value, program_kind, PROGRAM_TEMPLATES[program_kind])


@login_required
def gain_weight_program(request, value):
    return _program_view(request, value, PROGRAM_GAIN, PROGRAM_TEMPLATES[PROGRAM_GAIN])


@login_required
def stable_weight_program(request, value):
    return _program_view(request, value, PROGRAM_STABLE, PROGRAM_TEMPLATES[PROGRAM_STABLE])


@login_required
def lose_weight(request, value):
    return _program_view(request, value, PROGRAM_LOSE, PROGRAM_TEMPLATES[PROGRAM_LOSE])


def legacy_gain_weight_program(request, value):
    return redirect('diets:program', program_kind=PROGRAM_GAIN, value=value)


def legacy_stable_weight_program(request, value):
    return redirect('diets:program', program_kind=PROGRAM_STABLE, value=value)


def legacy_lose_weight_program(request, value):
    return redirect('diets:program', program_kind=PROGRAM_LOSE, value=value)


@login_required
def my_program(request):
    subscription = selectors.active_subscription_for_user(request.user)
    meal_plan = subscription.meal_plan if subscription else None
    context = {
        'subscription': subscription,
        'meal_plan': meal_plan,
        'meal_groups': selectors.meal_groups_for_plan(meal_plan) if meal_plan else {},
        'snacks': selectors.snack_recipes(),
    }
    return render(request, 'my_program.html', context)


@login_required
@require_POST
def unsubscribe_program(request):
    unsubscribe_active_programs(request.user)
    return redirect('recipes:my_profile')


@login_required
def settings_for_myprogram(request):
    subscription = get_object_or_404(selectors.active_subscriptions_for_user(request.user))
    return render(request, 'settings_for_my_program.html', {'program': subscription})
