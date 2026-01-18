from django.urls import path

from . import views

app_name = 'sources'

urlpatterns = [
    path('<int:strike_pk>/', views.index, name='index'),
]