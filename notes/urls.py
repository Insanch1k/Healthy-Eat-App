from django.urls import path
from . import views
app_name = 'notes'

urlpatterns = [
    path('', views.home_notes, name='home_notes'),
    path('update/<int:id>/', views.update_notes, name='update'),
    path('delete/<int:id>', views.delete, name='delete'),
]
