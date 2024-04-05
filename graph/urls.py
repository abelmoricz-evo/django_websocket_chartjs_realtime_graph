from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('update_pid/', views.update_pid),
]