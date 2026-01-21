from django.urls import path

from . import views

app_name = 'submit'

urlpatterns = [
    path('', views.index, name='index'),
    path('strike-fields/', views.strike_fields, name='strike_fields'),
]