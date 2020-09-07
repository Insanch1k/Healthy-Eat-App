from django.urls import path, include
from . import views

app_name = 'diets'

urlpatterns = [
    path('', views.show_progress, name='weight'),
    path('delete/<int:id>/', views.delete_weight, name='delete'),
    path('calculator/', views.calculator, name='calculator'),
    path('stable_weight/<int:value>/<int:amount_of_breakfast>/<int:amount_of_lunch>', views.stable_weight_program,
         name='stable_weight'),
    path('lose_weight/<int:value>/<int:amount_of_breakfast>/<int:amount_of_lunch>', views.lose_weight,
         name='lose_weight'),
    path('my_program', views.my_program, name='my_program'),
    path('settings/', views.settings_for_myprogram, name='settings')
]
