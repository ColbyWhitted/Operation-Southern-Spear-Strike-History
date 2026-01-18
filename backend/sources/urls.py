from django.urls import path

from . import views

urlpatterns = [
    path('<int:strike_pk>/', views.index, name='index'),
]