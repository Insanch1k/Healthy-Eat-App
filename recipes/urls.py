from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'recipes'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.my_profile, name='my_profile'),
    path('profile/edit/', views.edit, name='edit'),
    path('about/', views.AboutView.as_view(), name='about'),

    path('recipes/', views.recipe_list, name='recipes_list'),
    path('recipes/search/', views.search, name='search_recipes'),
    path(
        'recipes/category/<slug:category_slug>/',
        views.recipes_by_category,
        name='recipes_by',
    ),
    path(
        'recipes/category/<slug:category_slug>/calories/',
        views.search_calories,
        name='search_calories',
    ),
    path('recipes/<int:id>/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<int:id>/<slug:slug>/favorite/', views.favorite, name='favorite'),

    path(
        'meals/register/',
        RedirectView.as_view(pattern_name='recipes:register', permanent=False),
        name='legacy_register',
    ),
    path(
        'meals/my_profile/',
        RedirectView.as_view(pattern_name='recipes:my_profile', permanent=False),
        name='legacy_my_profile',
    ),
    path(
        'meals/my_profile/edit/',
        RedirectView.as_view(pattern_name='recipes:edit', permanent=False),
        name='legacy_edit',
    ),
    path(
        'meals/about',
        RedirectView.as_view(pattern_name='recipes:about', permanent=False),
        name='legacy_about',
    ),
    path(
        'meals/recipes/',
        RedirectView.as_view(pattern_name='recipes:recipes_list', permanent=False),
        name='legacy_recipes_list',
    ),
    path(
        'meals/results/',
        RedirectView.as_view(pattern_name='recipes:search_recipes', permanent=False),
        name='legacy_search_recipes',
    ),
    path(
        'meals/by/<slug:category_slug>',
        RedirectView.as_view(pattern_name='recipes:recipes_by', permanent=False),
        name='legacy_recipes_by',
    ),
    path(
        'meals/res_for/<slug:category_slug>',
        RedirectView.as_view(pattern_name='recipes:search_calories', permanent=False),
        name='legacy_search_calories',
    ),
    path(
        'meals/<int:id>/<slug:slug>/',
        RedirectView.as_view(pattern_name='recipes:recipe_detail', permanent=False),
        name='legacy_recipe_detail',
    ),
]
