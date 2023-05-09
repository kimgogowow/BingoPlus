from django.urls import path
from auction import views

urlpatterns = [
    path('', views.home),
]