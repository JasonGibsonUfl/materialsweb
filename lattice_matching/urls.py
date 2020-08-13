from . import views
from django.urls import path, include
from django.conf.urls import url

urlpatterns = [
    path('lattice', views.lattice_view, name='lattice'),
    ]