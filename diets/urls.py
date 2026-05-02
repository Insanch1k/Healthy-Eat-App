from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'diets'

urlpatterns = [
    path('weights/', views.show_progress, name='weight'),
    path('weights/<int:id>/delete/', views.delete_weight, name='delete'),
    path('calculator/', views.calculator, name='calculator'),
    path('programs/<str:program_kind>/<int:value>/', views.program, name='program'),
    path('programs/current/', views.my_program, name='my_program'),
    path('programs/current/unsubscribe/', views.unsubscribe_program, name='unsubscribe_program'),
    path('programs/current/settings/', views.settings_for_myprogram, name='settings'),

    path(
        'diets/',
        RedirectView.as_view(pattern_name='diets:weight', permanent=False),
        name='legacy_weight',
    ),
    path(
        'diets/delete/<int:id>/',
        RedirectView.as_view(pattern_name='diets:delete', permanent=False),
        name='legacy_delete',
    ),
    path(
        'diets/calculator/',
        RedirectView.as_view(pattern_name='diets:calculator', permanent=False),
        name='legacy_calculator',
    ),
    path(
        'diets/stable_weight/<int:value>',
        views.legacy_stable_weight_program,
        name='stable_weight',
    ),
    path(
        'diets/lose_weight/<int:value>',
        views.legacy_lose_weight_program,
        name='lose_weight',
    ),
    path(
        'diets/gain_program/<int:value>',
        views.legacy_gain_weight_program,
        name='gain_weight',
    ),
    path(
        'diets/my_program',
        RedirectView.as_view(pattern_name='diets:my_program', permanent=False),
        name='legacy_my_program',
    ),
    path(
        'diets/my_program/unsubscribe/',
        RedirectView.as_view(pattern_name='diets:unsubscribe_program', permanent=False),
        name='legacy_unsubscribe_program',
    ),
    path(
        'diets/settings/',
        RedirectView.as_view(pattern_name='diets:settings', permanent=False),
        name='legacy_settings',
    ),
]
