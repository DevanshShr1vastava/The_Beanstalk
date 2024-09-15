from django.urls import path

from . import views

urlpatterns = [
    path('newHome/', views.new_home, name='newHome'),
]
