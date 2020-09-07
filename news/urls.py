from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path('', views.MainView.as_view(), name="main"),
    path('<slug:slug>/', views.post_detail, name = "post-detail"),

]