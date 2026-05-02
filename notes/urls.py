from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.home_notes, name='home_notes'),
    path('<int:id>/edit/', views.update_notes, name='update'),
    path('<int:id>/delete/', views.delete, name='delete'),
    path(
        'update/<int:id>/',
        RedirectView.as_view(pattern_name='notes:update', permanent=False),
        name='legacy_update',
    ),
    path(
        'delete/<int:id>',
        RedirectView.as_view(pattern_name='notes:delete', permanent=False),
        name='legacy_delete',
    ),
]
