from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from recipes import selectors
from recipes.forms import EditProfile, EditUser, UserRegistrationForm
from recipes.models import Profile


class AboutView(TemplateView):
    template_name = 'health/about.html'


def ensure_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user, defaults={'phone': '+48000000000'})
    return profile


@login_required
def edit(request):
    profile = ensure_profile(request.user)
    if request.method == 'POST':
        user_form = EditUser(instance=request.user, data=request.POST)
        profile_form = EditProfile(instance=profile, data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated.')
            return redirect('recipes:edit')
        messages.error(request, 'Please correct the highlighted fields.')
    else:
        user_form = EditUser(instance=request.user)
        profile_form = EditProfile(instance=profile)
    return render(
        request,
        'profile/edit.html',
        {'user_form': user_form, 'profile_form': profile_form},
    )


@login_required
def my_profile(request):
    profile = ensure_profile(request.user)
    context = {
        **selectors.favorite_recipe_groups(request.user),
        'my_programs': selectors.active_subscriptions_for_user(request.user),
        'program': selectors.active_subscriptions_for_user(request.user),
        'number': profile.phone,
    }
    return render(request, 'profile/my_profile.html', context)


@transaction.atomic
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = EditProfile(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()

            profile = profile_form.save(commit=False)
            profile.user = new_user
            profile.save()

            login(request, new_user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('recipes:about')
    else:
        user_form = UserRegistrationForm()
        profile_form = EditProfile()
    return render(
        request,
        'registration/register.html',
        {'user_form': user_form, 'profile_form': profile_form},
    )
