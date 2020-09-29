from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_view

app_name = 'hairstyle'

urlpatterns = [

    # path('login/', views.user_login, name = 'login'),
    path('start/', views.StartView.as_view(), name='start_page'),
    path('register/', views.register, name='register'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('my_profile/edit/', views.edit, name='edit'),
    path('about', views.AboutView.as_view(), name='about'),
    path('new_template/', views.new_template, name='new_template'),
    path('example/', views.example, name='example'),
    path('recipes/', views.recipe_list, name='recipes_list'),
    path('results/', views.search, name='search_recipes'),
    path('by/<slug:category_slug>', views.recipes_by_category, name='recipes_by'),
    path('res_for/<slug:category_slug>', views.search_calories, name='search_calories'),

    path('<int:id>/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
    path('<int:id>/<slug:slug>/favorite/', views.favorite, name='favorite'),
]
